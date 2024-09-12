import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">Welcome to SmartCommerce AI</h1>
      <Link href="/login">
      </Link>
      <Link href="/register">
      </Link>
      <Link href="/products">
             </Link>
      <Link href="/products/new">
          </Link>
    </div>
  );
}
