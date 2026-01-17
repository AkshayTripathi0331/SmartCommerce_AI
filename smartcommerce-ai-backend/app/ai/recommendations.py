"""Recommendation engine using embeddings and behavior."""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Product, Cart, CartItem, Order, OrderItem
from app.ai.embeddings import embedding_service
from app.ai.vector_store import vector_store


class RecommendationService:
    """Service for generating product recommendations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_similar_products(
        self,
        product_id: UUID,
        limit: int = 5,
        exclude_self: bool = True,
    ) -> List[dict]:
        """
        Get products similar to the given product using embedding similarity.
        
        Args:
            product_id: ID of the source product
            limit: Maximum number of recommendations
            exclude_self: Whether to exclude the source product
            
        Returns:
            List of similar products with scores
        """
        # Get the product's embedding from Qdrant
        product_data = await vector_store.get_product_by_id(product_id)
        
        if not product_data or "embedding" not in product_data:
            # Fallback: get product and generate embedding
            result = await self.db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()
            if not product:
                return []
            
            # Generate embedding
            text = f"{product.name}. {product.description or ''}"
            embedding = await embedding_service.get_embedding(text)
        else:
            embedding = product_data["embedding"]
        
        # Search for similar products
        search_limit = limit + 1 if exclude_self else limit
        results = await vector_store.search_products(
            query_embedding=embedding,
            limit=search_limit,
            filter_conditions={"is_active": True},
        )
        
        # Filter out the source product if needed
        if exclude_self:
            results = [r for r in results if r["id"] != str(product_id)][:limit]
        
        return results
    
    async def get_personalized_recommendations(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> List[dict]:
        """
        Get personalized recommendations based on user's cart and order history.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended products with scores
        """
        # Get user's cart items
        cart_result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.user_id == user_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        cart_product_ids = set()
        cart_embeddings = []
        
        if cart and cart.items:
            for item in cart.items:
                if item.product and item.product.is_active:
                    cart_product_ids.add(str(item.product.id))
                    # Get embedding text
                    text = f"{item.product.name}. {item.product.description or ''}"
                    cart_embeddings.append(text)
        
        # Get recent order items
        order_result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(5)
        )
        orders = order_result.scalars().all()
        
        order_product_ids = set()
        order_embeddings = []
        
        for order in orders:
            for item in order.items:
                if item.product and item.product.is_active:
                    order_product_ids.add(str(item.product.id))
                    text = f"{item.product.name}. {item.product.description or ''}"
                    order_embeddings.append(text)
        
        # Combine embeddings (prioritize cart)
        all_texts = cart_embeddings + order_embeddings[:5]
        exclude_ids = cart_product_ids | order_product_ids
        
        if not all_texts:
            # No history - return popular products
            return await self.get_popular_products(limit)
        
        # Generate embeddings and average them
        embeddings = await embedding_service.get_embeddings_batch(all_texts)
        
        if not embeddings:
            return await self.get_popular_products(limit)
        
        # Calculate weighted average (cart items get more weight)
        import numpy as np
        
        weights = []
        for i, _ in enumerate(embeddings):
            if i < len(cart_embeddings):
                weights.append(2.0)  # Cart items weighted higher
            else:
                weights.append(1.0)  # Order history
        
        weights = np.array(weights) / sum(weights)
        avg_embedding = np.average(embeddings, axis=0, weights=weights).tolist()
        
        # Search for similar products
        results = await vector_store.search_products(
            query_embedding=avg_embedding,
            limit=limit + len(exclude_ids),
            filter_conditions={"is_active": True},
        )
        
        # Filter out products already in cart/orders
        filtered_results = [r for r in results if r["id"] not in exclude_ids][:limit]
        
        return filtered_results
    
    async def get_popular_products(self, limit: int = 10) -> List[dict]:
        """
        Get popular products as fallback recommendations.
        
        Args:
            limit: Maximum number of products
            
        Returns:
            List of popular products
        """
        result = await self.db.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.avg_rating.desc(), Product.review_count.desc())
            .limit(limit)
        )
        products = result.scalars().all()
        
        return [
            {
                "id": str(product.id),
                "name": product.name,
                "slug": product.slug,
                "price": float(product.price),
                "image_url": product.image_url,
                "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
                "score": 1.0 - (i * 0.05),  # Decreasing score for ranking
            }
            for i, product in enumerate(products)
        ]
    
    async def search_products_semantic(
        self,
        query: str,
        limit: int = 10,
        category_id: Optional[UUID] = None,
    ) -> List[dict]:
        """
        Semantic search for products.
        
        Args:
            query: Search query
            limit: Maximum number of results
            category_id: Optional category filter
            
        Returns:
            List of matching products with scores
        """
        # Generate query embedding (uses retrieval_query task type)
        query_embedding = await embedding_service.get_query_embedding(query)
        
        # Build filter conditions
        filter_conditions = {"is_active": True}
        if category_id:
            filter_conditions["category_id"] = str(category_id)
        
        # Search
        results = await vector_store.search_products(
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=0.3,  # Lower threshold for search
            filter_conditions=filter_conditions,
        )
        
        return results
