'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { FiMinus, FiPlus, FiTrash2, FiArrowRight } from 'react-icons/fi'
import { useAuthStore } from '@/lib/store'

interface CartItem {
    id: string
    product_id: string
    quantity: number
    product_name: string
    product_price: number
    product_image?: string
    subtotal: number
}

interface Cart {
    items: CartItem[]
    total: number
    item_count: number
}

export default function CartPage() {
    const { token } = useAuthStore()
    const [cart, setCart] = useState<Cart | null>(null)
    const [loading, setLoading] = useState(true)
    const [updating, setUpdating] = useState<string | null>(null)

    useEffect(() => {
        if (token) fetchCart()
        else setLoading(false)
    }, [token])

    async function fetchCart() {
        try {
            const res = await fetch('/api/v1/cart', {
                headers: { Authorization: `Bearer ${token}` },
            })
            if (res.ok) setCart(await res.json())
        } catch (error) {
            console.error('Failed to fetch cart')
        } finally {
            setLoading(false)
        }
    }

    async function updateQuantity(itemId: string, quantity: number) {
        if (quantity < 1) return removeItem(itemId)

        setUpdating(itemId)
        try {
            const res = await fetch(`/api/v1/cart/items/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ quantity }),
            })
            if (res.ok) setCart(await res.json())
        } catch (error) {
            console.error('Failed to update')
        } finally {
            setUpdating(null)
        }
    }

    async function removeItem(itemId: string) {
        setUpdating(itemId)
        try {
            const res = await fetch(`/api/v1/cart/items/${itemId}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            })
            if (res.ok) setCart(await res.json())
        } catch (error) {
            console.error('Failed to remove')
        } finally {
            setUpdating(null)
        }
    }

    if (!token) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <span className="text-6xl mb-4 block">🛒</span>
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in to view your cart</h1>
                <Link href="/login" className="inline-block px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700">
                    Sign In
                </Link>
            </div>
        )
    }

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="animate-pulse space-y-4">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="h-24 bg-gray-200 rounded-xl" />
                    ))}
                </div>
            </div>
        )
    }

    if (!cart || cart.items.length === 0) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <span className="text-6xl mb-4 block">🛒</span>
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Your cart is empty</h1>
                <Link href="/products" className="inline-block px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700">
                    Start Shopping
                </Link>
            </div>
        )
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

            <div className="grid lg:grid-cols-3 gap-8">
                {/* Cart items */}
                <div className="lg:col-span-2 space-y-4">
                    {cart.items.map((item) => (
                        <div key={item.id} className="bg-white rounded-xl p-4 border border-gray-100 flex gap-4">
                            {/* Image */}
                            <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                                {item.product_image ? (
                                    <Image
                                        src={item.product_image}
                                        alt={item.product_name}
                                        width={80}
                                        height={80}
                                        className="object-cover w-full h-full"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-2xl">📦</div>
                                )}
                            </div>

                            {/* Details */}
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-gray-900 truncate">{item.product_name}</h3>
                                <p className="text-primary-600 font-medium">${item.product_price.toFixed(2)}</p>
                            </div>

                            {/* Quantity */}
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                    disabled={updating === item.id}
                                    className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50"
                                >
                                    <FiMinus className="w-4 h-4" />
                                </button>
                                <span className="w-8 text-center font-medium">{item.quantity}</span>
                                <button
                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                    disabled={updating === item.id}
                                    className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50"
                                >
                                    <FiPlus className="w-4 h-4" />
                                </button>
                            </div>

                            {/* Subtotal & Remove */}
                            <div className="text-right">
                                <p className="font-bold text-gray-900">${item.subtotal.toFixed(2)}</p>
                                <button
                                    onClick={() => removeItem(item.id)}
                                    disabled={updating === item.id}
                                    className="text-red-500 hover:text-red-700 p-1"
                                >
                                    <FiTrash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Order summary */}
                <div className="bg-white rounded-xl p-6 border border-gray-100 h-fit">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Order Summary</h2>

                    <div className="space-y-2 mb-4">
                        <div className="flex justify-between text-gray-600">
                            <span>Subtotal ({cart.item_count} items)</span>
                            <span>${cart.total.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-gray-600">
                            <span>Shipping</span>
                            <span className="text-green-600">Free</span>
                        </div>
                    </div>

                    <div className="border-t pt-4 mb-6">
                        <div className="flex justify-between text-xl font-bold">
                            <span>Total</span>
                            <span className="text-primary-600">${cart.total.toFixed(2)}</span>
                        </div>
                    </div>

                    <Link
                        href="/checkout"
                        className="w-full py-3 bg-primary-600 text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-primary-700 transition-colors"
                    >
                        Checkout <FiArrowRight />
                    </Link>
                </div>
            </div>
        </div>
    )
}
