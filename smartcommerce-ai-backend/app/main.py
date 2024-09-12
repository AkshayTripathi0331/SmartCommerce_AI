from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from app.models import UserCreate, UserLogin, Product  
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage (for now)
fake_db = {}

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/register")
def register(user: UserCreate):
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    fake_db[user.username] = {"email": user.email, "password": hashed_password}
    
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    if user.username not in fake_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    hashed_password = fake_db[user.username]["password"]
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"message": "Login successful"}

# In-memory product storage (for now)
products_db = {}

@app.post("/products/", response_model=Product)
def create_product(product: Product):
    product_id = len(products_db) + 1
    products_db[product_id] = product
    return product

@app.get("/products/", response_model=List[Product])
def read_products():
    return list(products_db.values())

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: Product):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db[product_id] = product
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    return {"message": "Product deleted"}
