"use client";

import { useParams, useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';

const ProductDetail = () => {
  const router = useRouter();
  const { id } = useParams(); // Correctly destructuring the 'id'
  const [product, setProduct] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 0,
    stock: 0,
  });

  useEffect(() => {
    if (id) {
      const fetchProduct = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:8000/products/${id}`);
          if (!response.ok) throw new Error('Failed to fetch product');
          const data = await response.json();
          setProduct(data);
          setFormData({
            name: data.name,
            description: data.description,
            price: data.price,
            stock: data.stock,
          });
        } catch (error) {
          console.error(error);
        }
      };
      fetchProduct();
    }
  }, [id]);

  const handleEdit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://127.0.0.1:8000/products/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert('Product updated successfully!');
        setIsEditing(false);
      } else {
        alert('Failed to update product.');
      }
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/products/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('Product deleted successfully!');
        router.push('/products');
      } else {
        alert('Failed to delete product.');
      }
    } catch (error) {
      console.error('Error deleting product:', error);
    }
  };

  if (!product) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex flex-col items-center">
      {isEditing ? (
        <form onSubmit={handleEdit} className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-4">Edit Product</h2>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="block w-full p-2 border border-gray-300 rounded mb-4"
          />
          <input
            type="text"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="block w-full p-2 border border-gray-300 rounded mb-4"
          />
          <input
            type="number"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            className="block w-full p-2 border border-gray-300 rounded mb-4"
          />
          <input
            type="number"
            value={formData.stock}
            onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
            className="block w-full p-2 border border-gray-300 rounded mb-4"
          />
          <button type="submit" className="bg-blue-500 text-white p-2 rounded">
            Save
          </button>
        </form>
      ) : (
        <>
          <h1 className="text-4xl font-bold mb-6">{product.name}</h1>
          <p>{product.description}</p>
          <p>Price: ${product.price}</p>
          <p>Stock: {product.stock}</p>

          <button
            onClick={() => setIsEditing(true)}
            className="bg-yellow-500 text-white p-2 rounded mt-4"
          >
            Edit Product
          </button>
          <button
            onClick={handleDelete}
            className="bg-red-500 text-white p-2 rounded mt-4 ml-4"
          >
            Delete Product
          </button>
        </>
      )}
    </div>
  );
};

export default ProductDetail;
