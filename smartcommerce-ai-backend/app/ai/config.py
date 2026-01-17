"""AI module configuration."""
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """AI-specific settings."""
    
    # Google Gemini
    google_api_key: str = ""
    embedding_model: str = "models/text-embedding-004"
    embedding_dimensions: int = 768  # Gemini embedding dimensions
    chat_model: str = "gemini-2.0-flash"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_products: str = "products"
    qdrant_collection_policies: str = "policies"
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False


ai_settings = AISettings()
