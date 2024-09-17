from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str = None
    address: str = None
    phone_number: str = None

class Order(BaseModel):
    product_id: int
    product_name: str
    quality:int 
    total_price: float
    order_date: str

class UserWithOrders(UserProfile):
    orders: List[Order]

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Cart(BaseModel):
    items: List[CartItem]
