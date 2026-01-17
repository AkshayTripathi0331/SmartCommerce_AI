'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ProductCard } from '@/components/ProductCard'
import { HeroSection } from '@/components/HeroSection'

interface Product {
    id: string
    name: string
    slug: string
    description: string
    price: number
    image_url: string
    avg_rating: number
    review_count: number
}

interface Category {
    id: string
    name: string
    slug: string
}

export default function HomePage() {
    const [products, setProducts] = useState<Product[]>([])
    const [categories, setCategories] = useState<Category[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchData() {
            try {
                const [productsRes, categoriesRes] = await Promise.all([
                    fetch('/api/v1/products?limit=8'),
                    fetch('/api/v1/categories'),
                ])

                if (productsRes.ok) {
                    const data = await productsRes.json()
                    setProducts(data.items || [])
                }

                if (categoriesRes.ok) {
                    const cats = await categoriesRes.json()
                    setCategories(cats || [])
                }
            } catch (error) {
                console.error('Failed to fetch data:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    return (
        <div className="min-h-screen">
            <HeroSection />

            {/* Categories */}
            <section className="max-w-7xl mx-auto px-4 py-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Shop by Category</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {categories.map((category) => (
                        <Link
                            key={category.id}
                            href={`/products?category=${category.slug}`}
                            className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 p-6 text-white text-center card-hover"
                        >
                            <div className="relative z-10">
                                <h3 className="font-semibold text-lg">{category.name}</h3>
                            </div>
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                        </Link>
                    ))}
                </div>
            </section>

            {/* Featured Products */}
            <section className="max-w-7xl mx-auto px-4 py-12">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Featured Products</h2>
                    <Link
                        href="/products"
                        className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                        View All →
                    </Link>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="animate-pulse">
                                <div className="bg-gray-200 rounded-xl h-48 mb-4" />
                                <div className="bg-gray-200 h-4 rounded w-3/4 mb-2" />
                                <div className="bg-gray-200 h-4 rounded w-1/2" />
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {products.slice(0, 8).map((product) => (
                            <ProductCard key={product.id} product={product} />
                        ))}
                    </div>
                )}
            </section>

            {/* AI Features Banner */}
            <section className="bg-gradient-to-r from-primary-600 to-accent-600 py-16 mt-12">
                <div className="max-w-7xl mx-auto px-4 text-center text-white">
                    <h2 className="text-3xl font-bold mb-4">🤖 AI-Powered Shopping Experience</h2>
                    <p className="text-lg opacity-90 max-w-2xl mx-auto mb-8">
                        Chat with our AI assistant to find perfect products, get personalized
                        recommendations, and answer your questions instantly.
                    </p>
                    <div className="flex gap-4 justify-center">
                        <div className="glass rounded-lg px-6 py-3 text-gray-800">
                            <span className="font-semibold">Smart Search</span>
                        </div>
                        <div className="glass rounded-lg px-6 py-3 text-gray-800">
                            <span className="font-semibold">AI Recommendations</span>
                        </div>
                        <div className="glass rounded-lg px-6 py-3 text-gray-800">
                            <span className="font-semibold">24/7 Assistant</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
