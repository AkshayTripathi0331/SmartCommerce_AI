'use client'

import Link from 'next/link'
import Image from 'next/image'
import { FiStar, FiShoppingCart } from 'react-icons/fi'

interface Product {
    id: string
    name: string
    slug: string
    description?: string
    price: number
    image_url?: string
    avg_rating?: number
    review_count?: number
}

interface ProductCardProps {
    product: Product
}

export function ProductCard({ product }: ProductCardProps) {
    const rating = product.avg_rating || 0

    return (
        <Link href={`/products/${product.slug}`}>
            <div className="group bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden card-hover">
                {/* Image */}
                <div className="relative h-48 bg-gray-100 overflow-hidden">
                    {product.image_url ? (
                        <Image
                            src={product.image_url}
                            alt={product.name}
                            fill
                            className="object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                            <span className="text-4xl">📦</span>
                        </div>
                    )}

                    {/* Quick add button */}
                    <button
                        className="absolute bottom-3 right-3 p-2 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-primary-50"
                        onClick={(e) => {
                            e.preventDefault()
                            // TODO: Add to cart
                        }}
                    >
                        <FiShoppingCart className="w-5 h-5 text-primary-600" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-1 line-clamp-1">
                        {product.name}
                    </h3>

                    {product.description && (
                        <p className="text-sm text-gray-500 mb-2 line-clamp-2">
                            {product.description}
                        </p>
                    )}

                    {/* Rating */}
                    <div className="flex items-center gap-1 mb-2">
                        {[...Array(5)].map((_, i) => (
                            <FiStar
                                key={i}
                                className={`w-4 h-4 ${i < Math.round(rating)
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-300'
                                    }`}
                            />
                        ))}
                        {product.review_count !== undefined && product.review_count > 0 && (
                            <span className="text-xs text-gray-500 ml-1">
                                ({product.review_count})
                            </span>
                        )}
                    </div>

                    {/* Price */}
                    <div className="flex items-center justify-between">
                        <span className="text-lg font-bold text-primary-600">
                            ${Number(product.price).toFixed(2)}
                        </span>
                    </div>
                </div>
            </div>
        </Link>
    )
}
