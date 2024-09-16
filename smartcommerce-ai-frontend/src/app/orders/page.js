"use client";

import React, { useState, useEffect } from 'react';

const OrderHistoryPage = () => {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const fetchOrders = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/orders/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      }
    };

    fetchOrders();
  }, []);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Order History</h1>
      <ul className="space-y-4">
        {orders.map((order) => (
          <li key={order.order_id} className="border p-4 rounded">
            <p><strong>Product:</strong> {order.product_name}</p>
            <p><strong>Quantity:</strong> {order.quantity}</p>
            <p><strong>Total Price:</strong> ${order.total_price}</p>
            <p><strong>Order Date:</strong> {order.order_date}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default OrderHistoryPage;
