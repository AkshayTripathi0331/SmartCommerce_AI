
import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "testuser"
PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log(msg, color=Colors.BLUE):
    print(f"{color}{msg}{Colors.RESET}")

def success(msg):
    log(f"✅ {msg}", Colors.GREEN)

def fail(msg):
    log(f"❌ {msg}", Colors.RED)

def make_request(method, endpoint, data=None, headers=None):
    if headers is None:
        headers = {}
    
    url = f"{BASE_URL}{endpoint}"
    
    if data and method == "POST":
         # Check content type for encoding
        if headers.get("Content-Type") == "application/x-www-form-urlencoded":
            data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        else:
            # Default to JSON
            headers["Content-Type"] = "application/json"
            data_encoded = json.dumps(data).encode('utf-8')
    else:
        data_encoded = None

    req = urllib.request.Request(url, method=method, data=data_encoded, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            try:
                content = response.read().decode('utf-8')
                return response.status, json.loads(content)
            except:
                return response.status, {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return e.code, json.loads(body) if body else {}
    except Exception as e:
        fail(f"Request failed: {e}")
        return 0, None

def run_tests():
    log("🚀 Starting SmartCommerce System Test...\n")

    # 1. Health Check (Basic Access)
    try:
        urllib.request.urlopen("http://localhost:8000/docs")
        success("Backend is reachable")
    except:
        fail("Backend is NOT reachable at http://localhost:8000")
        return

    # 2. Authentication
    log("Testing Authentication (Login)...")
    status, res = make_request(
        "POST", 
        "/auth/login", 
        {"username": USERNAME, "password": PASSWORD},
        {"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if status == 200 and "access_token" in res:
        token = res["access_token"]
        success("Login successful")
    else:
        fail(f"Login failed: {status} {res}")
        return

    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Products
    log("Testing Products...")
    status, res = make_request("GET", "/products?skip=0&limit=5", headers=auth_headers)
    
    products = []
    if isinstance(res, list):
        products = res
    elif isinstance(res, dict) and "items" in res:
        products = res["items"]

    if status == 200 and len(products) > 0:
        success(f"Fetched {len(products)} products")
        product_id = products[0]["id"]
    else:
        fail(f"Product fetch failed: {status} {res}")
        return

    # 4. Cart
    log("Testing Cart (Add Item)...")
    cart_data = {"product_id": product_id, "quantity": 1}
    status, res = make_request("POST", "/cart/items", data=cart_data, headers=auth_headers)
    # 200 or 201 expected
    if status in [200, 201]:
        success("Added item to cart")
    else:
        fail(f"Add to cart failed: {status} {res}")

    # 5. AI Chat
    log("Testing AI Chat Agent (this may take a few seconds)...")
    chat_payload = {"message": "Can you recommend a laptop?"}
    
    start_time = time.time()
    status, res = make_request("POST", "/chat", data=chat_payload, headers=auth_headers)
    elapsed = time.time() - start_time
    
    if status == 200 and "response" in res:
        success(f"AI Responded in {elapsed:.1f}s")
        log(f"   🤖 Response: {res['response'][:100]}...") # Print preview
    else:
        fail(f"AI Chat failed: {status} {res}")

    print("\n")
    log("🎉 Test Complete!", Colors.GREEN)

if __name__ == "__main__":
    run_tests()
