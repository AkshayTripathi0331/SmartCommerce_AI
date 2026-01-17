from typing import List
from uuid import UUID
from fastapi import APIRouter, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import ReviewCreate, ReviewResponse, ReviewWithUser
from app.models import Review, Product, User
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError

router = APIRouter(tags=["Reviews"])


@router.get("/products/{product_id}/reviews", response_model=List[ReviewWithUser])
async def get_product_reviews(product_id: UUID, db: DbSession):
    """Get reviews for a product."""
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    if not result.scalar_one_or_none():
        raise NotFoundError("Product not found")
    
    result = await db.execute(
        select(Review, User.username)
        .join(User, Review.user_id == User.id)
        .where(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.all()
    
    return [
        ReviewWithUser(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            content=review.content,
            created_at=review.created_at,
            username=username,
        )
        for review, username in reviews
    ]


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    product_id: UUID,
    review_data: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a review for a product."""
    # Verify product exists
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product not found")
    
    # Check if user already reviewed this product
    result = await db.execute(
        select(Review).where(
            Review.product_id == product_id,
            Review.user_id == current_user.id
        )
    )
    if result.scalar_one_or_none():
        raise ConflictError("You have already reviewed this product")
    
    # Create review
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=review_data.rating,
        content=review_data.content,
    )
    db.add(review)
    await db.flush()
    
    # Update product rating
    result = await db.execute(
        select(
            func.avg(Review.rating),
            func.count(Review.id)
        ).where(Review.product_id == product_id)
    )
    avg_rating, review_count = result.one()
    
    product.avg_rating = round(avg_rating, 1) if avg_rating else 0
    product.review_count = review_count
    
    await db.flush()
    await db.refresh(review)
    
    return ReviewResponse.model_validate(review)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: UUID, db: DbSession, current_user: CurrentUser):
    """Delete own review."""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise NotFoundError("Review not found")
    
    if review.user_id != current_user.id:
        raise BadRequestError("You can only delete your own reviews")
    
    product_id = review.product_id
    await db.delete(review)
    await db.flush()
    
    # Update product rating
    result = await db.execute(
        select(
            func.avg(Review.rating),
            func.count(Review.id)
        ).where(Review.product_id == product_id)
    )
    avg_rating, review_count = result.one()
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product:
        product.avg_rating = round(avg_rating, 1) if avg_rating else 0
        product.review_count = review_count
        await db.flush()
