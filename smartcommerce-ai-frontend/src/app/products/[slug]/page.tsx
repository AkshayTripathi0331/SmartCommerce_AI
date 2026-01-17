'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { FiStar, FiShoppingCart, FiMinus, FiPlus, FiCheck } from 'react-icons/fi'
import { useAuthStore } from '@/lib/store'
import { ProductCard } from '@/components/ProductCard'

interface Product {
    id: string
    name: string
    slug: string
    description: string
    price: number
    stock: number
    image_url: string
    avg_rating: number
    review_count: number
    category?: { name: string; slug: string }
}

interface Review {
    id: string
    rating: number
    content: string
    username: string
    created_at: string
}

export default function ProductDetailPage() {
    const params = useParams()
    const slug = params.slug as string
    const { token } = useAuthStore()

    const [product, setProduct] = useState<Product | null>(null)
    const [reviews, setReviews] = useState<Review[]>([])
    const [similar, setSimilar] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [quantity, setQuantity] = useState(1)
    const [addedToCart, setAddedToCart] = useState(false)
    const [addingToCart, setAddingToCart] = useState(false)

    useEffect(() => {
        fetchProduct()
    }, [slug])

    async function fetchProduct() {
        setLoading(true)
        try {
            const res = await fetch(`/api/v1/products/${slug}`)
            if (res.ok) {
                const data = await res.json()
                setProduct(data)

                // Fetch reviews and similar products
                const [reviewsRes, similarRes] = await Promise.all([
                    fetch(`/api/v1/products/${data.id}/reviews`),
                    fetch(`/api/v1/products/${data.id}/similar?limit=4`),
                ])

                if (reviewsRes.ok) setReviews(await reviewsRes.json())
                if (similarRes.ok) {
                    const simData = await similarRes.json()
                    setSimilar(simData.recommendations || [])
                }
            }
        } catch (error) {
            console.error('Failed to fetch product')
        } finally {
            setLoading(false)
        }
    }

    async function addToCart() {
        if (!token || !product) return

        setAddingToCart(true)
        try {
            const res = await fetch('/api/v1/cart/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ product_id: product.id, quantity }),
            })

            if (res.ok) {
                setAddedToCart(true)
                setTimeout(() => setAddedToCart(false), 2000)
            }
        } catch (error) {
            console.error('Failed to add to cart')
        } finally {
            setAddingToCart(false)
        }
    }

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="animate-pulse">
                    <div className="grid md:grid-cols-2 gap-8">
                        <div className="bg-gray-200 rounded-xl h-96" />
                        <div className="space-y-4">
                            <div className="bg-gray-200 h-8 rounded w-3/4" />
                            <div className="bg-gray-200 h-6 rounded w-1/4" />
                            <div className="bg-gray-200 h-24 rounded" />
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    if (!product) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-16 text-center">
                <span className="text-6xl mb-4 block">😕</span>
                <h1 className="text-2xl font-bold text-gray-900">Product not found</h1>
                <Link href="/products" className="text-primary-600 hover:underline mt-4 inline-block">
                    Back to products
                </Link>
            </div>
        )
    }

    const rating = product.avg_rating || 0

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Breadcrumb */}
            <nav className="text-sm text-gray-500 mb-6">
                <Link href="/" className="hover:text-primary-600">Home</Link>
                <span className="mx-2">/</span>
                <Link href="/products" className="hover:text-primary-600">Products</Link>
                {product.category && (
                    <>
                        <span className="mx-2">/</span>
                        <Link href={`/products?category=${product.category.slug}`} className="hover:text-primary-600">
                            {product.category.name}
                        </Link>
                    </>
                )}
                <span className="mx-2">/</span>
                <span className="text-gray-900">{product.name}</span>
            </nav>

            {/* Product info */}
            <div className="grid md:grid-cols-2 gap-8 mb-12">
                {/* Image */}
                <div className="relative h-96 md:h-[500px] bg-gray-100 rounded-2xl overflow-hidden">
                    {product.image_url ? (
                        <Image
                            src={product.image_url}
                            alt={product.name}
                            fill
                            className="object-cover"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                            <span className="text-8xl">📦</span>
                        </div>
                    )}
                </div>

                {/* Details */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>

                    {/* Rating */}
                    <div className="flex items-center gap-2 mb-4">
                        <div className="flex">
                            {[...Array(5)].map((_, i) => (
                                <FiStar
                                    key={i}
                                    className={`w-5 h-5 ${i < Math.round(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                        }`}
                                />
                            ))}
                        </div>
                        <span className="text-gray-500">
                            ({product.review_count} reviews)
                        </span>
                    </div>

                    <div className="text-3xl font-bold text-primary-600 mb-4">
                        ${Number(product.price).toFixed(2)}
                    </div>

                    {/* Stock */}
                    <div className={`mb-6 ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {product.stock > 0 ? `✓ In Stock (${product.stock} available)` : '✗ Out of Stock'}
                    </div>

                    {/* Description */}
                    <p className="text-gray-600 mb-6 leading-relaxed">
                        {product.description}
                    </p>

                    {/* Quantity & Add to cart */}
                    {product.stock > 0 && (
                        <div className="flex gap-4 items-center mb-6">
                            <div className="flex items-center border border-gray-200 rounded-lg">
                                <button
                                    onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                                    className="p-3 hover:bg-gray-100"
                                >
                                    <FiMinus />
                                </button>
                                <span className="px-4 font-medium">{quantity}</span>
                                <button
                                    onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
                                    className="p-3 hover:bg-gray-100"
                                >
                                    <FiPlus />
                                </button>
                            </div>

                            {token ? (
                                <button
                                    onClick={addToCart}
                                    disabled={addingToCart}
                                    className={`flex-1 py-3 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${addedToCart
                                        ? 'bg-green-600 text-white'
                                        : 'bg-primary-600 text-white hover:bg-primary-700'
                                        }`}
                                >
                                    {addedToCart ? (
                                        <>
                                            <FiCheck /> Added to Cart
                                        </>
                                    ) : (
                                        <>
                                            <FiShoppingCart /> Add to Cart
                                        </>
                                    )}
                                </button>
                            ) : (
                                <Link
                                    href="/login"
                                    className="flex-1 py-3 px-6 bg-primary-600 text-white rounded-xl font-semibold text-center hover:bg-primary-700"
                                >
                                    Sign in to Add to Cart
                                </Link>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Reviews */}
            {reviews.length > 0 && (
                <section className="mb-12">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Customer Reviews</h2>
                    <div className="space-y-4">
                        {reviews.map((review) => (
                            <div key={review.id} className="bg-white rounded-xl p-6 border border-gray-100">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="flex">
                                        {[...Array(5)].map((_, i) => (
                                            <FiStar
                                                key={i}
                                                className={`w-4 h-4 ${i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                                    }`}
                                            />
                                        ))}
                                    </div>
                                    <span className="font-medium text-gray-900">{review.username}</span>
                                </div>
                                <p className="text-gray-600">{review.content}</p>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Similar products */}
            {similar.length > 0 && (
                <section>
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Similar Products</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {similar.map((p: any) => (
                            <ProductCard key={p.id} product={p} />
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}
