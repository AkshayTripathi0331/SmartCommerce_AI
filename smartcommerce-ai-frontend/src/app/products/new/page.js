"use client";
import { useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';

const NewProduct = () => {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState(0);
  const [stock, setStock] = useState(0);
  const [token, setToken] = useState('');

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      router.push('/login'); // Redirect to login if token is not available
    } else {
      setToken(storedToken); // Set the token in state
    }

    console.log("token",token);
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const product = { name, description, price, stock };
    const response = await fetch('http://127.0.0.1:8000/products/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(product),
    });

    if (response.ok) {
      alert('Product created successfully!');
    } else {
      alert('Failed to create product.');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-4">Create New Product</h2>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="block w-full p-2 border border-gray-300 rounded mb-4"
        />
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="block w-full p-2 border border-gray-300 rounded mb-4"
        />
        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="block w-full p-2 border border-gray-300 rounded mb-4"
        />
        <input
          type="number"
          placeholder="Stock"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          className="block w-full p-2 border border-gray-300 rounded mb-4"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Add Product
        </button>
      </form>
    </div>
  );
};

export default NewProduct;
