from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE SETUP ----------------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        items TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- SAMPLE PRODUCTS ----------------
products = [
    {"id": 1, "name": "Organic Apples", "price": 2.5},
    {"id": 2, "name": "Fresh Milk", "price": 1.2},
    {"id": 3, "name": "Free-range Eggs", "price": 3.0}
]

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

# -------- AUTH --------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# -------- PRODUCTS --------

@app.route("/products")
def product_list():
    return render_template("products.html", products=products)

# -------- CART --------

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(product_id)
    session.modified = True

    return redirect("/cart")

@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    if "cart" in session:
        for pid in session["cart"]:
            for product in products:
                if product["id"] == pid:
                    cart_items.append(product)
                    total += product["price"]

    return render_template("cart.html", items=cart_items, total=total)

# -------- CHECKOUT --------

@app.route("/checkout")
def checkout():
    if "user" not in session:
        return redirect("/login")

    if "cart" not in session or not session["cart"]:
        return "Cart is empty"

    items = str(session["cart"])

    conn = get_db()
    conn.execute("INSERT INTO orders (user, items) VALUES (?, ?)", (session["user"], items))
    conn.commit()
    conn.close()

    session["cart"] = []
    return "Order placed successfully!"

# -------- ORDER TRACKING --------

@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    user_orders = conn.execute("SELECT * FROM orders WHERE user=?", (session["user"],)).fetchall()
    conn.close()

    return render_template("orders.html", orders=user_orders)

# -------- DASHBOARD --------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", products=products)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
