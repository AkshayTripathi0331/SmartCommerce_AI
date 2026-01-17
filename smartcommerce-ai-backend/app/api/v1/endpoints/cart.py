from typing import List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import CartItemAdd, CartItemUpdate, CartItemResponse, CartResponse
from app.models import Cart, CartItem, Product
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(prefix="/cart", tags=["Cart"])


async def get_or_create_cart(db, user_id: UUID) -> Cart:
    """Get user's cart or create one if it doesn't exist."""
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.user_id == user_id)
    )
    cart = result.scalar_one_or_none()
    
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.flush()
        await db.refresh(cart)
    
    return cart


def build_cart_response(cart: Cart) -> CartResponse:
    """Build cart response with calculated totals."""
    items = []
    total = Decimal("0")
    
    for item in cart.items:
        subtotal = Decimal(str(item.product.price)) * item.quantity
        total += subtotal
        items.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=item.product.name,
            product_price=item.product.price,
            product_image=item.product.image_url,
            subtotal=subtotal,
        ))
    
    return CartResponse(
        id=cart.id,
        items=items,
        total=total,
        item_count=sum(item.quantity for item in cart.items),
    )


@router.get("", response_model=CartResponse)
async def get_cart(db: DbSession, current_user: CurrentUser):
    """Get current user's cart."""
    cart = await get_or_create_cart(db, current_user.id)
    return build_cart_response(cart)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(item_data: CartItemAdd, db: DbSession, current_user: CurrentUser):
    """Add item to cart."""
    # Verify product exists and is active
    result = await db.execute(
        select(Product).where(
            Product.id == item_data.product_id,
            Product.is_active == True
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product not found")
    
    if product.stock < item_data.quantity:
        raise BadRequestError(f"Insufficient stock. Available: {product.stock}")
    
    cart = await get_or_create_cart(db, current_user.id)
    
    # Check if item already in cart
    existing_item = None
    for item in cart.items:
        if item.product_id == item_data.product_id:
            existing_item = item
            break
    
    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise BadRequestError(f"Insufficient stock. Available: {product.stock}")
        existing_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        db.add(cart_item)
    
    await db.flush()
    
    # Reload cart with items
    cart = await get_or_create_cart(db, current_user.id)
    return build_cart_response(cart)


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update cart item quantity."""
    cart = await get_or_create_cart(db, current_user.id)
    
    # Find item
    item = None
    for cart_item in cart.items:
        if cart_item.id == item_id:
            item = cart_item
            break
    
    if not item:
        raise NotFoundError("Cart item not found")
    
    # Check stock
    if item.product.stock < item_data.quantity:
        raise BadRequestError(f"Insufficient stock. Available: {item.product.stock}")
    
    item.quantity = item_data.quantity
    await db.flush()
    
    # Reload cart
    cart = await get_or_create_cart(db, current_user.id)
    return build_cart_response(cart)


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(item_id: UUID, db: DbSession, current_user: CurrentUser):
    """Remove item from cart."""
    cart = await get_or_create_cart(db, current_user.id)
    
    # Find and remove item
    item_to_remove = None
    for item in cart.items:
        if item.id == item_id:
            item_to_remove = item
            break
    
    if not item_to_remove:
        raise NotFoundError("Cart item not found")
    
    await db.delete(item_to_remove)
    await db.flush()
    
    # Reload cart
    cart = await get_or_create_cart(db, current_user.id)
    return build_cart_response(cart)
