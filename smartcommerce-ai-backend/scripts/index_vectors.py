"""Script to index all products into Qdrant vector database."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db import async_session_maker
from app.models import Product
from app.ai.embeddings import embedding_service
from app.ai.vector_store import vector_store


async def index_products():
    """Index all active products into Qdrant."""
    print("🚀 Starting product indexing...")
    
    # Ensure collections exist
    await vector_store.ensure_collections()
    print("✅ Qdrant collections ready")
    
    async with async_session_maker() as session:
        # Get all active products
        result = await session.execute(
            select(Product).where(Product.is_active == True)
        )
        products = result.scalars().all()
        
        print(f"📦 Found {len(products)} products to index")
        
        if not products:
            print("No products to index")
            return
        
        # Prepare texts for embedding
        texts = []
        for product in products:
            # Combine name and description for richer embeddings
            text = f"{product.name}. {product.description or ''}"
            texts.append(text)
        
        # Generate embeddings in batch
        print("🔄 Generating embeddings...")
        embeddings = await embedding_service.get_embeddings_batch(texts)
        
        # Prepare product data for upsert
        products_data = []
        for product, embedding in zip(products, embeddings):
            products_data.append({
                "id": product.id,
                "embedding": embedding,
                "payload": {
                    "name": product.name,
                    "slug": product.slug,
                    "description": product.description,
                    "price": float(product.price),
                    "category_id": str(product.category_id) if product.category_id else None,
                    "image_url": product.image_url,
                    "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
                    "review_count": product.review_count,
                    "is_active": product.is_active,
                },
            })
        
        # Batch upsert to Qdrant
        print("📤 Uploading to Qdrant...")
        await vector_store.upsert_products_batch(products_data)
        
        print(f"✅ Successfully indexed {len(products)} products!")


async def main():
    try:
        await index_products()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await embedding_service.close()
        await vector_store.close()


if __name__ == "__main__":
    asyncio.run(main())
