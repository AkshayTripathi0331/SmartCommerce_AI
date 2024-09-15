import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">
        Welcome to SmartCommerce AI
      </h1>
      <Link href="/login">
        <p className="text-blue-500 mb-4">Login</p>
      </Link>
      <Link href="/register">
        <p className="text-blue-500 mb-4">Register</p>
      </Link>
      <Link href="/products">
        <p className="text-blue-500 mb-4">Products</p>
      </Link>
      <Link href="/products/new">
        <p className="text-blue-500 mb-4">Create New Product</p>
      </Link>
    </div>
  );
}
