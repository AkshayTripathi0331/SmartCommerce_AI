"""Script to index policy documents into Qdrant for RAG."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai.rag import index_policies
from app.ai.embeddings import embedding_service
from app.ai.vector_store import vector_store


async def main():
    """Index all policy documents."""
    print("🚀 Starting policy document indexing...")
    
    try:
        await index_policies()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await embedding_service.close()
        await vector_store.close()


if __name__ == "__main__":
    asyncio.run(main())
