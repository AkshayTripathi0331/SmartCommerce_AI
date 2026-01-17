from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import (
    RecommendationResponse,
    RecommendationsListResponse,
    SearchRequest,
    SearchResultResponse,
)
from app.ai import RecommendationService

router = APIRouter(tags=["AI & Recommendations"])


@router.get("/recommendations", response_model=RecommendationsListResponse)
async def get_personalized_recommendations(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
):
    """Get personalized product recommendations based on cart and order history."""
    rec_service = RecommendationService(db)
    results = await rec_service.get_personalized_recommendations(
        user_id=current_user.id,
        limit=limit,
    )
    
    recommendations = [
        RecommendationResponse(
            id=UUID(r["id"]),
            name=r["name"],
            slug=r["slug"],
            price=r["price"],
            image_url=r.get("image_url"),
            avg_rating=r.get("avg_rating", 0.0),
            score=r["score"],
        )
        for r in results
    ]
    
    based_on = "cart" if recommendations else "popular"
    
    return RecommendationsListResponse(
        recommendations=recommendations,
        based_on=based_on,
    )


@router.get("/products/{product_id}/similar", response_model=RecommendationsListResponse)
async def get_similar_products(
    product_id: UUID,
    db: DbSession,
    limit: int = Query(5, ge=1, le=20),
):
    """Get products similar to the specified product."""
    rec_service = RecommendationService(db)
    results = await rec_service.get_similar_products(
        product_id=product_id,
        limit=limit,
    )
    
    recommendations = [
        RecommendationResponse(
            id=UUID(r["id"]),
            name=r["name"],
            slug=r["slug"],
            price=r["price"],
            image_url=r.get("image_url"),
            avg_rating=r.get("avg_rating", 0.0),
            score=r["score"],
        )
        for r in results
    ]
    
    return RecommendationsListResponse(
        recommendations=recommendations,
        based_on="similar",
    )


@router.get("/search", response_model=list[SearchResultResponse])
async def semantic_search(
    db: DbSession,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[UUID] = None,
):
    """
    Semantic search for products using AI embeddings.
    
    This searches products based on meaning, not just keywords.
    For example, "wireless audio device" will find headphones and earbuds.
    """
    rec_service = RecommendationService(db)
    results = await rec_service.search_products_semantic(
        query=q,
        limit=limit,
        category_id=category_id,
    )
    
    return [
        SearchResultResponse(
            id=UUID(r["id"]),
            name=r["name"],
            slug=r["slug"],
            description=r.get("description"),
            price=r["price"],
            image_url=r.get("image_url"),
            score=r["score"],
        )
        for r in results
    ]
