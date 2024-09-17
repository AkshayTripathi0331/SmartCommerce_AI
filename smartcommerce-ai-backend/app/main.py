from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from app.models import UserCreate, UserLogin, Product, UserProfile, Order, UserWithOrders, CartItem, Cart
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.email_service import send_order_confirmation_email
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()


# Get environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
print(SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM")
print(ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
fake_db = {
    "testuser": {
        "email": "testuser@example.com",
        "password": pwd_context.hash("testpassword")  # Hashed password
    }
}

# Initial fake products
products_db = {
    1: Product(name="Laptop", description="A high-performance laptop", price=999.99, stock=10),
    2: Product(name="Smartphone", description="A latest model smartphone", price=799.99, stock=25),
    3: Product(name="Headphones", description="Noise-cancelling over-ear headphones", price=199.99, stock=15),
}

profiles_db = {}
orders_db = {}

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

    profiles_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": None,
        "address": None,
        "phone_number": None
    }

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"message": "User registered successfully", "access_token": access_token, "token_type": "bearer"}

@app.post("/login")
def login(user: UserLogin):
    if user.username not in fake_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    hashed_password = fake_db[user.username]["password"]
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@app.post("/products/", response_model=Product)
def create_product(product: Product, token: str = Depends(verify_token)):
    product_id = len(products_db) + 1
    products_db[product_id] = product.copy()  # Prevents reference issues
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
def update_product(product_id: int, product: Product, token: str = Depends(verify_token)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db[product_id] = product.copy()  # Prevents reference issues
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, token: str = Depends(verify_token)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    return {"message": "Product deleted"}


# Endpoint to view user profile
@app.get("/profile/", response_model=UserProfile)
def get_profile(token: str = Depends(verify_token)):
    username = verify_token(token)
    profile = profiles_db.get(username)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# Endpoint to update user profile
@app.put("/profile/")
def update_profile(updated_profile: UserProfile, token: str = Depends(verify_token)):
    username = verify_token(token)
    if username not in profiles_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profiles_db[username] = updated_profile.dict()
    return {"message": "Profile updated successfully"}

# Endpoint to view order history
@app.get("/orders/", response_model=List[Order])
def get_order_history(token: str = Depends(verify_token)):
    username = verify_token(token)
    return orders_db.get(username, [])

# Simulate order placement in backend for testing
@app.post("/orders/")
def create_order(token: str = Depends(verify_token)):
    username = verify_token(token)
    
    if username not in orders_db:
        orders_db[username] = []
    
    order = Order(
        order_id=len(orders_db[username]) + 1,
        product_name="Example Product",
        quantity=1,
        total_price=99.99,
        order_date="2024-09-15"
    )
    
    orders_db[username].append(order)
    
    return {"message": "Order created successfully"}

# Fake storage for carts (for now)
carts_db = {}

# Checkout endpoint
@app.post("/checkout/")
def checkout(cart: Cart, token: str = Depends(verify_token)):
    username = verify_token(token)
    
    if username not in profiles_db:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    if username not in orders_db:
        orders_db[username] = []
    
    total_price = 0
    order_items = []

    for item in cart.items:
        product = products_db.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        total_price += product.price * item.quantity
        product.stock -= item.quantity

        order_items.append({
            "product_name": product.name,
            "quantity": item.quantity,
            "total_price": product.price * item.quantity
        })
    
    order_id = len(orders_db[username]) + 1
    order = Order(
        order_id=order_id,
        product_name=", ".join([item["product_name"] for item in order_items]),
        quantity=sum([item["quantity"] for item in order_items]),
        total_price=total_price,
        order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    orders_db[username].append(order)

    # Send order confirmation email
    user_email = fake_db[username]["email"]
    send_order_confirmation_email(user_email, order)

    return {"message": "Order created successfully", "order": order}
