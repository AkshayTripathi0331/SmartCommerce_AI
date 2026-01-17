# SmartCommerce AI Backend

Production-grade AI-powered e-commerce platform.

## Quick Start

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Seed sample data
docker-compose exec api python scripts/seed_products.py
```

## API Documentation

Once running, visit: http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload
```
