"use client";

import React, { useState, useEffect } from 'react';

const CheckoutPage = () => {
  const [cart, setCart] = useState([]);
  const [order, setOrder] = useState(null);

  useEffect(() => {
    // Fetch the cart from local storage or API
    const savedCart = JSON.parse(localStorage.getItem('cart')) || [];
    setCart(savedCart);
  }, []);

  const handleCheckout = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://127.0.0.1:8000/checkout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ items: cart }),
    });

    if (response.ok) {
      const data = await response.json();
      setOrder(data.order);
      localStorage.removeItem('cart');  // Clear the cart after checkout
      alert('Checkout successful!');
    } else {
      alert('Checkout failed.');
    }
  };

  const totalPrice = cart.reduce((acc, item) => acc + item.quantity * item.price, 0);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Checkout</h1>

      {cart.length > 0 ? (
        <div>
          <h2 className="text-xl mb-4">Your Cart</h2>
          <ul className="space-y-4">
            {cart.map((item) => (
              <li key={item.product_id} className="border p-4 rounded">
                <p><strong>Product:</strong> {item.name}</p>
                <p><strong>Quantity:</strong> {item.quantity}</p>
                <p><strong>Price:</strong> ${item.price * item.quantity}</p>
              </li>
            ))}
          </ul>

          <p className="mt-4"><strong>Total Price:</strong> ${totalPrice}</p>

          <button
            onClick={handleCheckout}
            className="bg-green-500 text-white p-2 rounded mt-4"
          >
            Complete Purchase
          </button>
        </div>
      ) : (
        <p>Your cart is empty.</p>
      )}

      {order && (
        <div className="mt-8">
          <h2 className="text-xl mb-4">Order Summary</h2>
          <p><strong>Order ID:</strong> {order.order_id}</p>
          <p><strong>Total Price:</strong> ${order.total_price}</p>
          <p><strong>Order Date:</strong> {order.order_date}</p>
        </div>
      )}
    </div>
  );
};

export default CheckoutPage;
