"use client";

import Link from 'next/link';
import React, { useEffect, useState } from 'react';

const Products = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      const response = await fetch('http://127.0.0.1:8000/products/');
      const data = await response.json();
      setProducts(data);
    };

    fetchProducts();
  }, []);

  return (
    <div className="flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-6">Product List</h1>
      <ul>
        {products.map((product, index) => (
          <li key={index} className="mb-4">
            <h2 className="text-2xl font-bold">
              <Link href={`/products/${index + 1}`}>{product.name}</Link>
            </h2>
            <p>{product.description}</p>
            <p>Price: ${product.price}</p>
            <p>Stock: {product.stock}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Products;
