import uuid
from typing import List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import (
    OrderCreate, OrderResponse, OrderListResponse,
    OrderItemResponse, PaymentRequest, PaymentResponse,
)
from app.models import Order, OrderItem, Cart, CartItem, Product, OrderStatus
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate a unique order number."""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=List[OrderListResponse])
async def list_orders(db: DbSession, current_user: CurrentUser):
    """List current user's orders."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    return [
        OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status.value,
            total=order.total,
            created_at=order.created_at,
            item_count=sum(item.quantity for item in order.items),
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, db: DbSession, current_user: CurrentUser):
    """Get order details."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise NotFoundError("Order not found")
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status.value,
        total=order.total,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name if item.product else "Unknown",
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.unit_price * item.quantity,
            )
            for item in order.items
        ],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: DbSession, current_user: CurrentUser):
    """Create order from current cart (checkout)."""
    # Get cart with items
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.user_id == current_user.id)
    )
    cart = result.scalar_one_or_none()
    
    if not cart or not cart.items:
        raise BadRequestError("Cart is empty")
    
    # Validate stock and calculate total
    total = Decimal("0")
    order_items_data = []
    
    for cart_item in cart.items:
        product = cart_item.product
        if not product or not product.is_active:
            raise BadRequestError(f"Product {cart_item.product_id} is not available")
        
        if product.stock < cart_item.quantity:
            raise BadRequestError(
                f"Insufficient stock for {product.name}. Available: {product.stock}"
            )
        
        item_total = product.price * cart_item.quantity
        total += item_total
        order_items_data.append({
            "product": product,
            "quantity": cart_item.quantity,
            "unit_price": product.price,
        })
    
    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        total=total,
        shipping_address=order_data.shipping_address,
    )
    db.add(order)
    await db.flush()
    
    # Create order items and update stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.add(order_item)
        
        # Reduce stock
        item_data["product"].stock -= item_data["quantity"]
    
    # Clear cart
    for cart_item in cart.items:
        await db.delete(cart_item)
    
    await db.flush()
    await db.refresh(order)
    
    # Return order with items
    return await get_order(order.id, db, current_user)


@router.post("/{order_id}/pay", response_model=PaymentResponse)
async def pay_order(
    order_id: UUID,
    payment_data: PaymentRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Process mock payment for order."""
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise NotFoundError("Order not found")
    
    if order.status != OrderStatus.PENDING:
        raise BadRequestError(f"Order cannot be paid. Current status: {order.status.value}")
    
    # Mock payment - always succeeds
    order.status = OrderStatus.PAID
    await db.flush()
    
    return PaymentResponse(
        success=True,
        message="Payment successful",
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
    )
