'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { FiCheck, FiCreditCard } from 'react-icons/fi'

export default function CheckoutPage() {
    const router = useRouter()
    const { token } = useAuthStore()
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState<'address' | 'payment' | 'complete'>('address')
    const [orderId, setOrderId] = useState<string | null>(null)

    const [address, setAddress] = useState({
        street: '',
        city: '',
        state: '',
        zip: '',
        country: 'United States',
    })

    async function placeOrder() {
        setLoading(true)
        try {
            const shippingAddress = `${address.street}, ${address.city}, ${address.state} ${address.zip}, ${address.country}`

            const res = await fetch('/api/v1/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ shipping_address: shippingAddress }),
            })

            if (res.ok) {
                const order = await res.json()
                setOrderId(order.id)
                setStep('payment')
            }
        } catch (error) {
            console.error('Failed to place order')
        } finally {
            setLoading(false)
        }
    }

    async function processPayment() {
        if (!orderId) return

        setLoading(true)
        try {
            const res = await fetch(`/api/v1/orders/${orderId}/pay`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    card_number: '4242424242424242',
                    expiry: '12/25',
                    cvv: '123',
                }),
            })

            if (res.ok) {
                setStep('complete')
            }
        } catch (error) {
            console.error('Payment failed')
        } finally {
            setLoading(false)
        }
    }

    if (step === 'complete') {
        return (
            <div className="max-w-2xl mx-auto px-4 py-16 text-center">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <FiCheck className="w-10 h-10 text-green-600" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Order Confirmed!</h1>
                <p className="text-gray-600 mb-8">
                    Thank you for your purchase. You&apos;ll receive an email confirmation shortly.
                </p>
                <button
                    onClick={() => router.push('/orders')}
                    className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700"
                >
                    View Orders
                </button>
            </div>
        )
    }

    return (
        <div className="max-w-2xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

            {/* Progress */}
            <div className="flex items-center gap-4 mb-8">
                <div className={`flex items-center gap-2 ${step === 'address' ? 'text-primary-600' : 'text-green-600'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'address' ? 'bg-primary-100' : 'bg-green-100'}`}>
                        {step === 'payment' ? <FiCheck /> : '1'}
                    </div>
                    <span className="font-medium">Shipping</span>
                </div>
                <div className="flex-1 h-px bg-gray-200" />
                <div className={`flex items-center gap-2 ${step === 'payment' ? 'text-primary-600' : 'text-gray-400'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'payment' ? 'bg-primary-100' : 'bg-gray-100'}`}>
                        2
                    </div>
                    <span className="font-medium">Payment</span>
                </div>
            </div>

            {step === 'address' && (
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Shipping Address</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Street Address</label>
                            <input
                                type="text"
                                value={address.street}
                                onChange={(e) => setAddress({ ...address, street: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                placeholder="123 Main St"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                                <input
                                    type="text"
                                    value={address.city}
                                    onChange={(e) => setAddress({ ...address, city: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="New York"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                                <input
                                    type="text"
                                    value={address.state}
                                    onChange={(e) => setAddress({ ...address, state: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="NY"
                                    required
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">ZIP Code</label>
                                <input
                                    type="text"
                                    value={address.zip}
                                    onChange={(e) => setAddress({ ...address, zip: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="10001"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                                <input
                                    type="text"
                                    value={address.country}
                                    onChange={(e) => setAddress({ ...address, country: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    disabled
                                />
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={placeOrder}
                        disabled={loading || !address.street || !address.city || !address.state || !address.zip}
                        className="w-full mt-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : 'Continue to Payment'}
                    </button>
                </div>
            )}

            {step === 'payment' && (
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Payment</h2>

                    <div className="bg-gray-50 rounded-xl p-4 mb-6">
                        <div className="flex items-center gap-3">
                            <FiCreditCard className="w-8 h-8 text-gray-400" />
                            <div>
                                <p className="font-medium text-gray-900">Test Card</p>
                                <p className="text-sm text-gray-500">•••• •••• •••• 4242</p>
                            </div>
                        </div>
                    </div>

                    <p className="text-sm text-gray-500 mb-4">
                        This is a demo payment. No real charges will be made.
                    </p>

                    <button
                        onClick={processPayment}
                        disabled={loading}
                        className="w-full py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50"
                    >
                        {loading ? 'Processing Payment...' : 'Pay Now'}
                    </button>
                </div>
            )}
        </div>
    )
}
