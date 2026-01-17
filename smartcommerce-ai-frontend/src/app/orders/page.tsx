'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store'
import { FiPackage, FiChevronRight } from 'react-icons/fi'

interface Order {
    id: string
    order_number: string
    status: string
    total: number
    created_at: string
    item_count: number
}

const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-blue-100 text-blue-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
}

export default function OrdersPage() {
    const { token } = useAuthStore()
    const [orders, setOrders] = useState<Order[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token) fetchOrders()
        else setLoading(false)
    }, [token])

    async function fetchOrders() {
        try {
            const res = await fetch('/api/v1/orders', {
                headers: { Authorization: `Bearer ${token}` },
            })
            if (res.ok) setOrders(await res.json())
        } catch (error) {
            console.error('Failed to fetch orders')
        } finally {
            setLoading(false)
        }
    }

    if (!token) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <FiPackage className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in to view your orders</h1>
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

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Your Orders</h1>

            {orders.length === 0 ? (
                <div className="text-center py-12">
                    <FiPackage className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-700 mb-2">No orders yet</h2>
                    <p className="text-gray-500 mb-4">Start shopping to see your orders here</p>
                    <Link href="/products" className="inline-block px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700">
                        Browse Products
                    </Link>
                </div>
            ) : (
                <div className="space-y-4">
                    {orders.map((order) => (
                        <Link
                            key={order.id}
                            href={`/orders/${order.id}`}
                            className="block bg-white rounded-xl p-6 border border-gray-100 hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="font-bold text-gray-900">{order.order_number}</span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[order.status] || 'bg-gray-100 text-gray-800'}`}>
                                            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500">
                                        {new Date(order.created_at).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric',
                                        })}
                                        {' • '}
                                        {order.item_count} item{order.item_count !== 1 ? 's' : ''}
                                    </p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-xl font-bold text-primary-600">${Number(order.total).toFixed(2)}</span>
                                    <FiChevronRight className="w-5 h-5 text-gray-400" />
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
