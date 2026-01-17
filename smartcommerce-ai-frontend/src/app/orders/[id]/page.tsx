'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useParams } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { FiPackage, FiArrowLeft, FiMapPin, FiCreditCard } from 'react-icons/fi'

interface OrderItem {
    id: string
    product_id: string
    quantity: number
    product_name: string
    product_price: number
    product_image?: string
    subtotal: number
}

interface Order {
    id: string
    order_number: string
    status: string
    total: number
    shipping_address: string
    created_at: string
    items: OrderItem[]
}

const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-blue-100 text-blue-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
}

export default function OrderDetailsPage() {
    const params = useParams()
    const { token } = useAuthStore()
    const [order, setOrder] = useState<Order | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token && params.id) fetchOrder()
        else setLoading(false)
    }, [token, params.id])

    async function fetchOrder() {
        try {
            const res = await fetch(`/api/v1/orders/${params.id}`, {
                headers: { Authorization: `Bearer ${token}` },
            })
            if (res.ok) setOrder(await res.json())
        } catch (error) {
            console.error('Failed to fetch order')
        } finally {
            setLoading(false)
        }
    }

    if (!token) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <FiPackage className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in to view order details</h1>
                <Link href="/login" className="inline-block px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700">
                    Sign In
                </Link>
            </div>
        )
    }

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="animate-pulse space-y-8">
                    <div className="h-8 bg-gray-200 w-1/3 rounded-lg" />
                    <div className="grid grid-cols-3 gap-8">
                        <div className="col-span-2 space-y-4">
                            <div className="h-32 bg-gray-200 rounded-xl" />
                            <div className="h-32 bg-gray-200 rounded-xl" />
                        </div>
                        <div className="h-64 bg-gray-200 rounded-xl" />
                    </div>
                </div>
            </div>
        )
    }

    if (!order) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Order not found</h1>
                <Link href="/orders" className="text-primary-600 hover:text-primary-700 font-medium">
                    ← Back to Orders
                </Link>
            </div>
        )
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <Link href="/orders" className="inline-flex items-center text-gray-500 hover:text-gray-900 mb-6 group">
                <FiArrowLeft className="mr-2 group-hover:-translate-x-1 transition-transform" />
                Back to Orders
            </Link>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Order #{order.order_number}</h1>
                    <p className="text-gray-500">
                        Placed on {new Date(order.created_at).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: 'numeric',
                        })}
                    </p>
                </div>
                <div className={`px-4 py-2 rounded-full font-medium ${statusColors[order.status] || 'bg-gray-100 text-gray-800'}`}>
                    {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
                {/* Order Items */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
                            <h2 className="font-semibold text-gray-900">Items ({order.items.length})</h2>
                        </div>
                        <div className="divide-y divide-gray-100">
                            {order.items.map((item) => (
                                <div key={item.id} className="p-4 flex gap-4">
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
                                    <div className="flex-1">
                                        <h3 className="font-medium text-gray-900 mb-1">{item.product_name}</h3>
                                        <p className="text-gray-500 text-sm mb-2">Quantity: {item.quantity}</p>
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-500">${Number(item.product_price).toFixed(2)} each</span>
                                            <span className="font-bold text-gray-900">${Number(item.subtotal).toFixed(2)}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar Info */}
                <div className="space-y-6">
                    {/* Summary */}
                    <div className="bg-white rounded-xl p-6 border border-gray-100">
                        <h2 className="font-bold text-gray-900 mb-4">Order Summary</h2>
                        <div className="space-y-2 mb-4 text-sm">
                            <div className="flex justify-between text-gray-600">
                                <span>Subtotal</span>
                                <span>${Number(order.total).toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-gray-600">
                                <span>Shipping</span>
                                <span className="text-green-600">Free</span>
                            </div>
                        </div>
                        <div className="border-t pt-4 flex justify-between font-bold text-lg">
                            <span>Total</span>
                            <span className="text-primary-600">${Number(order.total).toFixed(2)}</span>
                        </div>
                    </div>

                    {/* Shipping Address */}
                    <div className="bg-white rounded-xl p-6 border border-gray-100">
                        <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <FiMapPin className="text-gray-400" />
                            Shipping Address
                        </h2>
                        <p className="text-gray-600 whitespace-pre-wrap leading-relaxed">
                            {order.shipping_address}
                        </p>
                    </div>

                    {/* Payment Info */}
                    <div className="bg-white rounded-xl p-6 border border-gray-100">
                        <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <FiCreditCard className="text-gray-400" />
                            Payment Method
                        </h2>
                        <div className="flex items-center gap-3 text-gray-600">
                            <div className="bg-gray-100 p-2 rounded">
                                <FiCreditCard />
                            </div>
                            <span>Credit Card ending in 4242</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
