from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, cart, orders, reviews, recommendations, chat

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(auth.router)
router.include_router(products.router)
router.include_router(cart.router)
router.include_router(orders.router)
router.include_router(reviews.router)
router.include_router(recommendations.router)
router.include_router(chat.router)
