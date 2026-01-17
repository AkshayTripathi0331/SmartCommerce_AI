# SmartCommerce AI - Frontend

Next.js 14 frontend for the AI-powered e-commerce platform.

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Pages

- `/` - Home page with hero, categories, featured products
- `/products` - Product listing with search, filters, pagination
- `/products/[slug]` - Product detail with reviews and similar items
- `/cart` - Shopping cart
- `/checkout` - Multi-step checkout flow
- `/orders` - Order history
- `/login` - Login/Register

## Features

- 🤖 AI Chat Widget - Conversational shopping assistant
- 🎨 Modern UI - Tailwind CSS with glassmorphism and animations
- 📱 Responsive - Mobile-first design
- 🔐 Auth - JWT-based authentication with Zustand persistence

## Environment

The frontend proxies API requests to `http://localhost:8000` via `next.config.js`.