"use client";

import React, { useState, useEffect } from 'react';

const ProfilePage = () => {
  const [profile, setProfile] = useState({
    username: '',
    email: '',
    full_name: '',
    address: '',
    phone_number: '',
  });

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/profile/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    };

    fetchProfile();
  }, []);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    const response = await fetch('http://127.0.0.1:8000/profile/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(profile),
    });

    if (response.ok) {
      alert('Profile updated successfully!');
    } else {
      alert('Failed to update profile.');
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Your Profile</h1>
      <form onSubmit={handleUpdateProfile} className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          value={profile.full_name}
          onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
          className="block w-full p-2 border border-gray-300 rounded"
        />
        <input
          type="text"
          placeholder="Address"
          value={profile.address}
          onChange={(e) => setProfile({ ...profile, address: e.target.value })}
          className="block w-full p-2 border border-gray-300 rounded"
        />
        <input
          type="text"
          placeholder="Phone Number"
          value={profile.phone_number}
          onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
          className="block w-full p-2 border border-gray-300 rounded"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Update Profile
        </button>
      </form>
    </div>
  );
};

export default ProfilePage;
