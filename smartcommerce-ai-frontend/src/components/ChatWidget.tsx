'use client'

import { useState, useRef, useEffect } from 'react'
import { FiMessageCircle, FiX, FiSend, FiTrash2 } from 'react-icons/fi'
import ReactMarkdown from 'react-markdown'
import { useAuthStore } from '@/lib/store'

interface Message {
    role: 'user' | 'assistant'
    content: string
}

export function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "Hi! 👋 I'm your AI shopping assistant. I can help you find products, manage your cart, track orders, and answer questions. What are you looking for today?",
        },
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const { token } = useAuthStore()

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || loading) return

        if (!token) {
            setMessages((prev) => [
                ...prev,
                { role: 'user', content: input },
                { role: 'assistant', content: 'Please sign in to chat with me! I need to know who you are to help with your cart and orders. 😊' },
            ])
            setInput('')
            return
        }

        const userMessage = input.trim()
        setInput('')
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ message: userMessage }),
            })

            if (response.ok) {
                const data = await response.json()
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: data.response },
                ])
            } else if (response.status === 401) {
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: 'Your session has expired. Please log in again to continue chatting! 🔐' },
                ])
            } else {
                throw new Error('Failed to get response')
            }
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: "Sorry, I'm having trouble connecting. Please try again! 🔄" },
            ])
        } finally {
            setLoading(false)
        }
    }

    const clearHistory = async () => {
        if (!token) return

        try {
            await fetch('/api/v1/chat/history', {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            })
            setMessages([
                {
                    role: 'assistant',
                    content: "Chat history cleared! Let's start fresh. How can I help you today? 🛒",
                },
            ])
        } catch (error) {
            console.error('Failed to clear history')
        }
    }

    return (
        <>
            {/* Chat button */}
            <button
                data-chat-trigger
                onClick={() => setIsOpen(true)}
                className={`fixed bottom-6 right-6 z-50 p-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105 ${isOpen ? 'hidden' : ''
                    }`}
            >
                <FiMessageCircle className="w-6 h-6" />
            </button>

            {/* Chat window */}
            {isOpen && (
                <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] h-[500px] max-h-[calc(100vh-6rem)] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in border border-gray-200">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-primary-600 to-accent-600 p-4 text-white flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🤖</span>
                            <div>
                                <h3 className="font-semibold">Shopping Assistant</h3>
                                <p className="text-xs opacity-80">AI-powered help</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={clearHistory}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                                title="Clear history"
                            >
                                <FiTrash2 className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                            >
                                <FiX className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`chat-message flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                    }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-2xl px-4 py-2 ${message.role === 'user'
                                        ? 'bg-primary-600 text-white rounded-br-md'
                                        : 'bg-gray-100 text-gray-800 rounded-bl-md'
                                        }`}
                                >
                                    <ReactMarkdown
                                        className="text-sm prose prose-sm max-w-none"
                                        components={{
                                            p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                                            ul: ({ children }) => <ul className="list-disc list-inside mb-1">{children}</ul>,
                                            li: ({ children }) => <li className="text-sm">{children}</li>,
                                        }}
                                    >
                                        {message.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-gray-100">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder="Ask me anything..."
                                className="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                disabled={loading}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={loading || !input.trim()}
                                className="p-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <FiSend className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
