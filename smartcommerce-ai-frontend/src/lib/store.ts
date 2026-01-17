import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: string
    email: string
    username: string
    full_name?: string
    role: string
}

interface AuthState {
    user: User | null
    token: string | null
    setAuth: (user: User, token: string) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            setAuth: (user, token) => set({ user, token }),
            logout: () => set({ user: null, token: null }),
        }),
        {
            name: 'auth-storage',
        }
    )
)

interface CartItem {
    id: string
    product_id: string
    name: string
    price: number
    quantity: number
    image_url?: string
}

interface CartState {
    items: CartItem[]
    total: number
    setCart: (items: CartItem[], total: number) => void
    clearCart: () => void
}

export const useCartStore = create<CartState>((set) => ({
    items: [],
    total: 0,
    setCart: (items, total) => set({ items, total }),
    clearCart: () => set({ items: [], total: 0 }),
}))
