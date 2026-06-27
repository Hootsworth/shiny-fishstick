from typing import Optional

from fastapi import Cookie, FastAPI, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Mock Store")

# Mock database
PRODUCTS = [
    {"id": "1", "name": "Antigravity Boots", "price": 999.99, "desc": "Walk on the ceiling with ease."},
    {"id": "2", "name": "Quantum Coffee Mug", "price": 49.99, "desc": "Keeps coffee hot in all timelines."},
    {"id": "3", "name": "AI Coding Assistant", "price": 0.00, "desc": "Write code at lightspeed."},
]

CART = []

# Basic layout wrapper with modern CDN Tailwind CSS
def layout(title: str, content: str, username: Optional[str] = None) -> str:
    nav_links = ""
    if username:
        nav_links = f"""
        <span class="text-gray-300 mr-4">Hello, <strong class="text-white">{username}</strong></span>
        <a href="/catalog" class="text-gray-300 hover:text-white mr-4 transition">Catalog</a>
        <a href="/checkout" class="text-gray-300 hover:text-white mr-4 transition">Checkout</a>
        <a href="/logout" class="text-red-400 hover:text-red-300 transition">Logout</a>
        """
    else:
        nav_links = """
        <a href="/login" class="text-blue-400 hover:text-blue-300 transition">Login</a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Mock Store</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{
                background: radial-gradient(circle at top, #1a202c, #0f172a);
                color: #f8fafc;
                min-height: 100vh;
            }}
        </style>
    </head>
    <body class="font-sans flex flex-col justify-between">
        <header class="border-b border-gray-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
                <a href="/catalog" class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                    🌌 Shiny Fishstick Mock Store
                </a>
                <nav class="flex items-center">
                    {nav_links}
                </nav>
            </div>
        </header>
        <main class="max-w-4xl mx-auto px-4 py-12 flex-grow w-full">
            {content}
        </main>
        <footer class="border-t border-gray-800 py-6 text-center text-gray-500 text-sm">
            &copy; 2026 Shiny Fishstick. Verification Sandbox.
        </footer>
    </body>
    </html>
    """

@app.get("/")
def home(session: Optional[str] = Cookie(None)):
    if session:
        return RedirectResponse(url="/catalog")
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(error: Optional[str] = None):
    error_msg = f'<div class="bg-red-900/50 border border-red-500 text-red-200 px-4 py-2 rounded mb-4" id="login-error">{error}</div>' if error else ''
    content = f"""
    <div class="max-w-md mx-auto bg-slate-900/80 border border-gray-800 p-8 rounded-2xl shadow-xl backdrop-blur-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Sign In</h2>
        {error_msg}
        <form action="/login" method="POST" id="login-form" class="space-y-6">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-400 mb-1">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="user@example.com"
                       class="w-full bg-slate-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500">
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-gray-400 mb-1">Password</label>
                <input type="password" id="password" name="password" required placeholder="••••••••"
                       class="w-full bg-slate-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500">
            </div>
            <button type="submit" id="login-submit-btn" class="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold py-2 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition duration-300">
                Continue
            </button>
        </form>
    </div>
    """
    return HTMLResponse(content=layout("Login", content))

@app.post("/login")
def login(response: Response, email: str = Form(...), password: str = Form(...)):
    if email == "admin@example.com" and password == "password123":
        response = RedirectResponse(url="/catalog", status_code=303)
        response.set_cookie(key="session", value="admin-session-token-abc123")
        response.set_cookie(key="username", value="AdminUser")
        return response
    return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session")
    response.delete_cookie("username")
    return response

@app.get("/catalog", response_class=HTMLResponse)
def catalog(q: Optional[str] = None, session: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/login")

    filtered_products = PRODUCTS
    if q:
        filtered_products = [p for p in PRODUCTS if q.lower() in p["name"].lower() or q.lower() in p["desc"].lower()]

    product_cards = ""
    for p in filtered_products:
        product_cards += f"""
        <div class="bg-slate-900/60 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition duration-300 flex flex-col justify-between product-card" id="product-{p["id"]}">
            <div>
                <h3 class="text-lg font-bold mb-2 product-name">{p["name"]}</h3>
                <p class="text-gray-400 text-sm mb-4">{p["desc"]}</p>
            </div>
            <div class="flex justify-between items-center mt-4 border-t border-gray-800 pt-4">
                <span class="text-xl font-semibold text-blue-400">${p["price"]:.2f}</span>
                <a href="/product/{p["id"]}" id="view-details-{p["id"]}" class="text-sm bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-medium transition view-details-link">
                    View Details
                </a>
            </div>
        </div>
        """

    if not product_cards:
        product_cards = '<p class="text-gray-500 col-span-3 text-center py-8">No products found.</p>'

    content = f"""
    <div class="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
            <h1 class="text-3xl font-extrabold tracking-tight">Explore Products</h1>
            <p class="text-gray-400 mt-1">Discover artificial gravity gadgets and code widgets.</p>
        </div>
        <form action="/catalog" method="GET" id="search-form" class="flex w-full md:w-auto">
            <input type="text" name="q" id="search-input" value="{q or ''}" placeholder="Search catalog..."
                   class="bg-slate-950 border border-gray-800 rounded-l-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500 w-full md:w-64">
            <button type="submit" id="search-submit-btn" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-r-lg font-semibold transition">
                Search
            </button>
        </form>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        {product_cards}
    </div>
    """
    return HTMLResponse(content=layout("Catalog", content, username=username))

@app.get("/product/{id}", response_class=HTMLResponse)
def product_details(id: str, session: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/login")

    p = next((p for p in PRODUCTS if p["id"] == id), None)
    if not p:
        return HTMLResponse(content=layout("Not Found", "<h1 class='text-2xl font-bold'>Product not found</h1>", username=username))

    content = f"""
    <div class="bg-slate-900/60 border border-gray-800 rounded-2xl p-8 max-w-2xl mx-auto flex flex-col md:flex-row gap-8">
        <div class="flex-grow">
            <a href="/catalog" class="text-sm text-blue-400 hover:underline mb-4 inline-block">&larr; Back to Catalog</a>
            <h1 class="text-3xl font-bold mb-2">{p["name"]}</h1>
            <p class="text-blue-400 text-2xl font-semibold mb-4">${p["price"]:.2f}</p>
            <p class="text-gray-300 mb-6">{p["desc"]}</p>

            <button id="add-to-cart-btn" data-product-id="{p["id"]}" class="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-2 px-6 rounded-lg transition duration-300">
                Add to Cart
            </button>
            <div id="status-msg" class="mt-4 text-green-400 font-medium hidden"></div>
        </div>
    </div>

    <script>
        document.getElementById('add-to-cart-btn').addEventListener('click', async function() {{
            const prodId = this.getAttribute('data-product-id');
            const response = await fetch('/api/cart/add', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ product_id: prodId, quantity: 1 }})
            }});
            if (response.ok) {{
                const status = document.getElementById('status-msg');
                status.textContent = 'Success! Added to cart.';
                status.classList.remove('hidden');
                setTimeout(() => status.classList.add('hidden'), 3000);
            }}
        }});
    </script>
    """
    return HTMLResponse(content=layout(p["name"], content, username=username))

class CartItem(BaseModel):
    product_id: str
    quantity: int

@app.post("/api/cart/add")
def add_to_cart(item: CartItem, session: Optional[str] = Cookie(None)):
    if not session:
        return Response(status_code=401, content="Unauthorized")
    CART.append(item.dict())
    return {"status": "success", "cart_size": len(CART)}

@app.get("/checkout", response_class=HTMLResponse)
def checkout_page(session: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/login")

    items_html = ""
    total = 0.0
    for item in CART:
        p = next((p for p in PRODUCTS if p["id"] == item["product_id"]), None)
        if p:
            subtotal = p["price"] * item["quantity"]
            total += subtotal
            items_html += f"""
            <div class="flex justify-between items-center py-2 border-b border-gray-800">
                <span>{p["name"]} (x{item["quantity"]})</span>
                <span class="font-semibold">${subtotal:.2f}</span>
            </div>
            """

    if not CART:
        items_html = '<p class="text-gray-500 text-center py-4">Your cart is empty.</p>'

    content = f"""
    <div class="max-w-md mx-auto bg-slate-900/80 border border-gray-800 p-8 rounded-2xl shadow-xl">
        <h2 class="text-2xl font-bold mb-6 text-center">Checkout Summary</h2>
        <div class="space-y-4 mb-6">
            {items_html}
            <div class="flex justify-between items-center pt-4 text-xl font-bold border-t border-gray-750">
                <span>Total:</span>
                <span class="text-blue-400">${total:.2f}</span>
            </div>
        </div>
        <form action="/checkout" method="POST" id="checkout-form">
            <button type="submit" id="checkout-submit-btn" class="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold py-2 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition duration-300">
                Place Order
            </button>
        </form>
    </div>
    """
    return HTMLResponse(content=layout("Checkout", content, username=username))

@app.post("/checkout")
def place_order(session: Optional[str] = Cookie(None)):
    if not session:
        return RedirectResponse(url="/login")
    CART.clear()
    return RedirectResponse(url="/catalog?msg=Order placed successfully!", status_code=303)
