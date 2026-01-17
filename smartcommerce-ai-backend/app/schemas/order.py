from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# --- Cart Schemas ---

class CartItemAdd(BaseModel):
    """Schema for adding item to cart."""
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    """Schema for cart item response."""
    id: UUID
    product_id: UUID
    quantity: int
    product_name: str
    product_price: Decimal
    product_image: Optional[str]
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response."""
    id: UUID
    items: List[CartItemResponse]
    total: Decimal
    item_count: int


# --- Order Schemas ---

class OrderCreate(BaseModel):
    """Schema for creating an order."""
    shipping_address: str = Field(..., min_length=10)


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: UUID
    order_number: str
    status: str
    total: Decimal
    shipping_address: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for order list response."""
    id: UUID
    order_number: str
    status: str
    total: Decimal
    created_at: datetime
    item_count: int
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """Schema for mock payment."""
    payment_method: str = "card"


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    success: bool
    message: str
    transaction_id: Optional[str] = None
