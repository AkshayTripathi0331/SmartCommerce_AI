"""Pydantic schemas for API request/response validation."""
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    MessageResponse,
)
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithCategory,
    ProductListResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewWithUser,
)
from app.schemas.order import (
    CartItemAdd,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderListResponse,
    PaymentRequest,
    PaymentResponse,
)
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    RecommendationResponse,
    RecommendationsListResponse,
    SearchRequest,
    SearchResultResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "MessageResponse",
    # Product
    "CategoryCreate",
    "CategoryResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductWithCategory",
    "ProductListResponse",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewWithUser",
    # Order
    "CartItemAdd",
    "CartItemUpdate",
    "CartItemResponse",
    "CartResponse",
    "OrderCreate",
    "OrderItemResponse",
    "OrderResponse",
    "OrderListResponse",
    "PaymentRequest",
    "PaymentResponse",
    # Chat
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "RecommendationResponse",
    "RecommendationsListResponse",
    "SearchRequest",
    "SearchResultResponse",
]
