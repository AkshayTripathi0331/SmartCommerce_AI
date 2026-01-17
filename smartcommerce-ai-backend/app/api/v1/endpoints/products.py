from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.v1.deps import DbSession, AdminUser
from app.schemas import (
    CategoryCreate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    ProductWithCategory, ProductListResponse,
)
from app.models import Category, Product
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(tags=["Products"])


# --- Categories ---

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(db: DbSession):
    """List all categories."""
    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: DbSession, admin: AdminUser):
    """Create a new category (admin only)."""
    # Check slug uniqueness
    result = await db.execute(select(Category).where(Category.slug == category_data.slug))
    if result.scalar_one_or_none():
        raise ConflictError("Category slug already exists")
    
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)


# --- Products ---

@router.get("/products", response_model=ProductListResponse)
async def list_products(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = Query("created_at", regex="^(name|price|rating|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """List products with filtering and pagination."""
    query = select(Product).where(Product.is_active == True)
    count_query = select(func.count(Product.id)).where(Product.is_active == True)
    
    # Apply filters
    if category_id:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    
    if search:
        search_filter = Product.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)
    
    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)
    
    # Sorting
    sort_column = getattr(Product, sort_by if sort_by != "rating" else "avg_rating")
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute
    result = await db.execute(query)
    products = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.get("/products/{slug}", response_model=ProductWithCategory)
async def get_product(slug: str, db: DbSession):
    """Get product by slug."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.slug == slug)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product not found")
    
    response = ProductWithCategory.model_validate(product)
    if product.category:
        response.category = CategoryResponse.model_validate(product.category)
    
    return response


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: DbSession, admin: AdminUser):
    """Create a new product (admin only)."""
    # Check slug uniqueness
    result = await db.execute(select(Product).where(Product.slug == product_data.slug))
    if result.scalar_one_or_none():
        raise ConflictError("Product slug already exists")
    
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: DbSession,
    admin: AdminUser,
):
    """Update a product (admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product not found")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.flush()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, db: DbSession, admin: AdminUser):
    """Soft delete a product (admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product not found")
    
    product.is_active = False
    await db.flush()
