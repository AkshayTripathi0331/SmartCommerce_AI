import Link from 'next/link'

export function HeroSection() {
    return (
        <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-accent-700 text-white">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
                <div className="absolute -top-24 -right-24 w-96 h-96 bg-white rounded-full blur-3xl" />
                <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-accent-500 rounded-full blur-3xl" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 py-20 md:py-28">
                <div className="max-w-3xl">
                    <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-4 py-2 mb-6 backdrop-blur-sm">
                        <span className="text-2xl">🤖</span>
                        <span className="text-sm font-medium">AI-Powered Shopping Experience</span>
                    </div>

                    <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                        Shop Smarter with{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-300">
                            AI Assistance
                        </span>
                    </h1>

                    <p className="text-xl md:text-2xl text-white/80 mb-8 leading-relaxed">
                        Discover products tailored just for you. Our AI assistant helps you find
                        exactly what you need with personalized recommendations.
                    </p>

                    <div className="flex flex-wrap gap-4">
                        <Link
                            href="/products"
                            className="px-8 py-4 bg-white text-primary-700 rounded-xl font-semibold hover:bg-gray-100 transition-colors shadow-lg shadow-black/10"
                        >
                            Browse Products
                        </Link>
                        <button
                            className="px-8 py-4 bg-white/10 backdrop-blur-sm rounded-xl font-semibold hover:bg-white/20 transition-colors border border-white/20"
                            onClick={() => {
                                // Trigger chat widget
                                const chatBtn = document.querySelector('[data-chat-trigger]') as HTMLElement
                                chatBtn?.click()
                            }}
                        >
                            💬 Chat with AI
                        </button>
                    </div>

                    {/* Stats */}
                    <div className="flex flex-wrap gap-8 mt-12 pt-8 border-t border-white/20">
                        <div>
                            <div className="text-3xl font-bold">10K+</div>
                            <div className="text-white/70">Products</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold">50K+</div>
                            <div className="text-white/70">Happy Customers</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold">24/7</div>
                            <div className="text-white/70">AI Support</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}
