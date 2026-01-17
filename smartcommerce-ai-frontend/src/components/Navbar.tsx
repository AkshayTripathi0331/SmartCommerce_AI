'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuthStore } from '@/lib/store'
import { FiShoppingCart, FiUser, FiMenu, FiX } from 'react-icons/fi'

export function Navbar() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const { user, token, logout } = useAuthStore()

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-gray-200/50">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <span className="text-2xl">🛒</span>
                        <span className="font-bold text-xl gradient-text">SmartCommerce</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-8">
                        <Link href="/products" className="text-gray-700 hover:text-primary-600 font-medium transition-colors">
                            Products
                        </Link>
                        <Link href="/categories" className="text-gray-700 hover:text-primary-600 font-medium transition-colors">
                            Categories
                        </Link>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-4">
                        <Link
                            href="/cart"
                            className="relative p-2 text-gray-700 hover:text-primary-600 transition-colors"
                        >
                            <FiShoppingCart className="w-6 h-6" />
                        </Link>

                        {token ? (
                            <div className="flex items-center gap-3">
                                <Link
                                    href="/orders"
                                    className="text-gray-700 hover:text-primary-600 font-medium hidden md:block"
                                >
                                    Orders
                                </Link>
                                <button
                                    onClick={logout}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-red-600 transition-colors"
                                >
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <Link
                                href="/login"
                                className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center gap-2"
                            >
                                <FiUser className="w-4 h-4" />
                                <span className="hidden md:inline">Sign In</span>
                            </Link>
                        )}

                        {/* Mobile menu button */}
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden p-2 text-gray-700"
                        >
                            {mobileMenuOpen ? <FiX className="w-6 h-6" /> : <FiMenu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden py-4 border-t border-gray-200/50">
                        <div className="flex flex-col gap-4">
                            <Link href="/products" className="text-gray-700 hover:text-primary-600 font-medium">
                                Products
                            </Link>
                            <Link href="/categories" className="text-gray-700 hover:text-primary-600 font-medium">
                                Categories
                            </Link>
                            {token && (
                                <Link href="/orders" className="text-gray-700 hover:text-primary-600 font-medium">
                                    Orders
                                </Link>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    )
}
