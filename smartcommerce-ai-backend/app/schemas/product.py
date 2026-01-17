from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# --- Category Schemas ---

class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


# --- Product Schemas ---

class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[UUID] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    price: Decimal
    stock: int
    category_id: Optional[UUID]
    image_url: Optional[str]
    avg_rating: Decimal
    review_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithCategory(ProductResponse):
    """Product response with category details."""
    category: Optional[CategoryResponse] = None


class ProductListResponse(BaseModel):
    """Paginated product list response."""
    items: List[ProductResponse]
    total: int
    page: int
    pages: int


# --- Review Schemas ---

class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    """Schema for review response."""
    id: UUID
    product_id: UUID
    user_id: UUID
    rating: int
    content: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """Review with user info."""
    username: str
