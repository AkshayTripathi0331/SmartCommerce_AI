"""Agent tools for the shopping assistant."""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Product, Cart, CartItem, Order, Category
from app.ai.recommendations import RecommendationService
from app.ai.rag import rag_service


class AgentTools:
    """Tools available to the shopping agent."""
    
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.rec_service = RecommendationService(db)
    
    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 5,
    ) -> dict:
        """
        Search for products by query.
        
        Args:
            query: Search terms
            category: Optional category filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            limit: Max results to return
        """
        # Get category ID if provided
        category_id = None
        if category:
            result = await self.db.execute(
                select(Category).where(Category.slug == category.lower())
            )
            cat = result.scalar_one_or_none()
            if cat:
                category_id = cat.id
        
        # Use semantic search
        results = await self.rec_service.search_products_semantic(
            query=query,
            limit=limit,
            category_id=category_id,
        )
        
        # Apply price filters
        if min_price is not None:
            results = [r for r in results if r.get("price", 0) >= min_price]
        if max_price is not None:
            results = [r for r in results if r.get("price", float('inf')) <= max_price]
        
        return {
            "products": results[:limit],
            "count": len(results),
        }
    
    async def get_product_details(self, product_id: str) -> dict:
        """
        Get detailed information about a product.
        
        Args:
            product_id: Product UUID
        """
        try:
            pid = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product ID"}
        
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == pid)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            return {"error": "Product not found"}
        
        return {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock": product.stock,
            "category": product.category.name if product.category else None,
            "rating": float(product.avg_rating) if product.avg_rating else 0,
            "review_count": product.review_count,
            "in_stock": product.stock > 0,
        }
    
    async def add_to_cart(self, product_id: str, quantity: int = 1) -> dict:
        """
        Add a product to the user's cart.
        
        Args:
            product_id: Product UUID
            quantity: Quantity to add
        """
        try:
            pid = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product ID"}
        
        # Get product
        result = await self.db.execute(
            select(Product).where(Product.id == pid, Product.is_active == True)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            return {"error": "Product not found"}
        
        if product.stock < quantity:
            return {"error": f"Insufficient stock. Only {product.stock} available."}
        
        # Get or create cart
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.user_id == self.user_id)
        )
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=self.user_id)
            self.db.add(cart)
            await self.db.flush()
        
        # Check if product already in cart
        existing_item = None
        for item in cart.items:
            if item.product_id == pid:
                existing_item = item
                break
        
        if existing_item:
            new_qty = existing_item.quantity + quantity
            if product.stock < new_qty:
                return {"error": f"Cannot add more. Total would exceed stock ({product.stock})."}
            existing_item.quantity = new_qty
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=pid, quantity=quantity)
            self.db.add(cart_item)
        
        await self.db.flush()
        
        return {
            "success": True,
            "message": f"Added {quantity}x {product.name} to cart",
            "product": product.name,
            "quantity": quantity,
        }
    
    async def view_cart(self) -> dict:
        """View the current contents of the user's cart."""
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.user_id == self.user_id)
        )
        cart = result.scalar_one_or_none()
        
        if not cart or not cart.items:
            return {"items": [], "total": 0, "item_count": 0}
        
        items = []
        total = Decimal("0")
        
        for item in cart.items:
            subtotal = item.product.price * item.quantity
            total += subtotal
            items.append({
                "id": str(item.id),
                "product_id": str(item.product_id),
                "name": item.product.name,
                "price": float(item.product.price),
                "quantity": item.quantity,
                "subtotal": float(subtotal),
            })
        
        return {
            "items": items,
            "total": float(total),
            "item_count": sum(i["quantity"] for i in items),
        }
    
    async def get_recommendations(
        self,
        based_on: str = "cart",
        product_id: Optional[str] = None,
        limit: int = 5,
    ) -> dict:
        """
        Get product recommendations.
        
        Args:
            based_on: "cart" for personalized, "similar" for similar to product
            product_id: Required if based_on is "similar"
            limit: Max recommendations
        """
        if based_on == "similar" and product_id:
            try:
                pid = UUID(product_id)
                results = await self.rec_service.get_similar_products(pid, limit)
            except ValueError:
                return {"error": "Invalid product ID"}
        else:
            results = await self.rec_service.get_personalized_recommendations(
                self.user_id, limit
            )
        
        return {
            "recommendations": results,
            "based_on": based_on,
        }
    
    async def lookup_policy(self, query: str) -> dict:
        """
        Look up shipping, returns, or terms policies.
        
        Args:
            query: Question about policies
        """
        result = await rag_service.answer_policy_question(query)
        return result
    
    async def get_order_status(self, order_id: Optional[str] = None) -> dict:
        """
        Get order status. If no order_id, returns recent orders.
        
        Args:
            order_id: Optional specific order ID
        """
        if order_id:
            try:
                oid = UUID(order_id)
                result = await self.db.execute(
                    select(Order)
                    .options(selectinload(Order.items))
                    .where(Order.id == oid, Order.user_id == self.user_id)
                )
                order = result.scalar_one_or_none()
                
                if not order:
                    return {"error": "Order not found"}
                
                return {
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "total": float(order.total),
                    "created_at": order.created_at.isoformat(),
                    "item_count": sum(i.quantity for i in order.items),
                }
            except ValueError:
                return {"error": "Invalid order ID"}
        else:
            # Get recent orders
            result = await self.db.execute(
                select(Order)
                .where(Order.user_id == self.user_id)
                .order_by(Order.created_at.desc())
                .limit(5)
            )
            orders = result.scalars().all()
            
            return {
                "orders": [
                    {
                        "order_number": o.order_number,
                        "status": o.status.value,
                        "total": float(o.total),
                        "created_at": o.created_at.isoformat(),
                    }
                    for o in orders
                ]
            }


# Tool definitions for Gemini function calling
TOOL_DEFINITIONS = [
    {
        "name": "search_products",
        "description": "Search for products in the store's catalog. Use this when the user asks 'what do you have?', 'search for X', or 'find Y'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing what the user is looking for"
                },
                "category": {
                    "type": "string",
                    "description": "Category filter (e.g., 'electronics', 'clothing')"
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price filter"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price filter"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_product_details",
        "description": "Get detailed information about a specific product. Use when user asks about a particular product.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The product UUID string (copy exactly from search results)"
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "add_to_cart",
        "description": "Add a product to the user's shopping cart.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The product UUID string to add (copy exactly from search results)"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to add",
                    "default": 1
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "view_cart",
        "description": "View the contents of the user's shopping cart.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get product recommendations for the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "based_on": {
                    "type": "string",
                    "enum": ["cart", "similar"],
                    "description": "'cart' for personalized recommendations, 'similar' for products similar to a specific one"
                },
                "product_id": {
                    "type": "string",
                    "description": "Product ID for similar recommendations"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum recommendations",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "lookup_policy",
        "description": "Look up official store policies regarding shipping, returns, refunds, or terms. Use this for ANY question about 'how do I return' or 'how long is shipping'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Question about policies"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_order_status",
        "description": "Get status of orders. Use when user asks about their order or tracking.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Specific order ID (optional, shows recent orders if not provided)"
                }
            }
        }
    }
]
