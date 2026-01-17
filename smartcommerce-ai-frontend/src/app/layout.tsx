import type { Metadata } from 'next'
import './globals.css'
import { Navbar } from '@/components/Navbar'
import { ChatWidget } from '@/components/ChatWidget'

export const metadata: Metadata = {
    title: 'SmartCommerce AI - AI-Powered Shopping',
    description: 'Experience the future of online shopping with AI-powered recommendations and conversational assistance.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
                <Navbar />
                <main className="pt-16">
                    {children}
                </main>
                <ChatWidget />
            </body>
        </html>
    )
}
