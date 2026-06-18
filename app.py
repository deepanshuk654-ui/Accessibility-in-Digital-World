"""
AccessEase 2.0 — Accessibility-Focused Electronics E-Commerce
Flask Backend | SQLite Database | Bootstrap 5 Frontend
"""

import os
import sqlite3
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, g, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash

# ──────────────────────────────────────────────────────────────
# APP CONFIGURATION
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "accessease2_super_secret_key_2025")

DB_PATH = os.environ.get("DB_PATH", "accessease.db")


# ──────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ──────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


def query(sql, args=(), one=False, commit=False):
    db = get_db()
    try:
        cur = db.execute(sql, args)
        if commit:
            db.commit()
            return cur.lastrowid
        if one:
            row = cur.fetchone()
            return dict(row) if row else None
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        if commit:
            db.rollback()
        raise e


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db:
        db.close()


# ──────────────────────────────────────────────────────────────
# AUTH DECORATORS
# ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────────────────────
# CONTEXT PROCESSORS
# ──────────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    cart_count = 0
    categories = []
    try:
        categories = query("SELECT * FROM categories ORDER BY id") or []
        if "user_id" in session:
            row = query(
                "SELECT COALESCE(SUM(quantity),0) AS cnt FROM cart WHERE user_id=?",
                (session["user_id"],), one=True
            )
            cart_count = int(row["cnt"]) if row else 0
    except Exception:
        pass
    return dict(
        cart_count=cart_count,
        categories=categories,
        current_user=session.get("user_name"),
        is_logged_in="user_id" in session,
    )


# ──────────────────────────────────────────────────────────────
# HOME
# ──────────────────────────────────────────────────────────────
@app.route("/")
def home():
    featured = query("SELECT p.*, c.name AS cat_name, c.slug AS cat_slug FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.is_featured=1 AND p.is_active=1 LIMIT 8") or []
    mobiles  = query("SELECT p.*, c.slug AS cat_slug FROM products p JOIN categories c ON p.category_id=c.id WHERE c.slug='mobiles'  AND p.is_active=1 LIMIT 4") or []
    laptops  = query("SELECT p.*, c.slug AS cat_slug FROM products p JOIN categories c ON p.category_id=c.id WHERE c.slug='laptops'  AND p.is_active=1 LIMIT 4") or []
    earbuds  = query("SELECT p.*, c.slug AS cat_slug FROM products p JOIN categories c ON p.category_id=c.id WHERE c.slug='earbuds'  AND p.is_active=1 LIMIT 4") or []
    speakers = query("SELECT p.*, c.slug AS cat_slug FROM products p JOIN categories c ON p.category_id=c.id WHERE c.slug='speakers' AND p.is_active=1 LIMIT 4") or []
    return render_template("index.html",
        featured=featured, mobiles=mobiles,
        laptops=laptops, earbuds=earbuds, speakers=speakers)


# ──────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        if not all([name, email, password]):
            flash("All fields are required.", "danger")
            return render_template("signup.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("signup.html")
        if query("SELECT id FROM users WHERE email=?", (email,), one=True):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))
        query("INSERT INTO users (name, email, password) VALUES (?,?,?)",
              (name, email, generate_password_hash(password)), commit=True)
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = query("SELECT * FROM users WHERE email=? AND is_active=1", (email,), one=True)
        if user and check_password_hash(user["password"], password):
            session["user_id"]    = user["id"]
            session["user_name"]  = user["name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(request.args.get("next") or url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))


# ──────────────────────────────────────────────────────────────
# PROFILE
# ──────────────────────────────────────────────────────────────
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user   = query("SELECT * FROM users WHERE id=?", (session["user_id"],), one=True)
    orders = query("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
                   (session["user_id"],)) or []
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        phone   = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city    = request.form.get("city", "").strip()
        state   = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        query("UPDATE users SET name=?,phone=?,address=?,city=?,state=?,pincode=? WHERE id=?",
              (name, phone, address, city, state, pincode, session["user_id"]), commit=True)
        session["user_name"] = name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user, orders=orders)


@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    old_pw  = request.form.get("old_password", "")
    new_pw  = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    user = query("SELECT * FROM users WHERE id=?", (session["user_id"],), one=True)
    if not check_password_hash(user["password"], old_pw):
        flash("Current password is incorrect.", "danger")
    elif new_pw != confirm:
        flash("New passwords do not match.", "danger")
    elif len(new_pw) < 6:
        flash("Password must be at least 6 characters.", "danger")
    else:
        query("UPDATE users SET password=? WHERE id=?",
              (generate_password_hash(new_pw), session["user_id"]), commit=True)
        flash("Password changed successfully.", "success")
    return redirect(url_for("profile"))


# ──────────────────────────────────────────────────────────────
# PRODUCTS
# ──────────────────────────────────────────────────────────────
@app.route("/products")
def products():
    category_slug = request.args.get("category", "")
    brand_filter  = request.args.get("brand", "")
    sort          = request.args.get("sort", "popular")
    min_price     = request.args.get("min_price", 0, type=int)
    max_price     = request.args.get("max_price", 500000, type=int)
    page          = request.args.get("page", 1, type=int)
    per_page      = 12

    sql  = "SELECT p.*, c.name AS cat_name, c.slug AS cat_slug FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.is_active=1"
    args = []
    if category_slug:
        sql += " AND c.slug=?"; args.append(category_slug)
    if brand_filter:
        sql += " AND p.brand=?"; args.append(brand_filter)
    sql += " AND p.price BETWEEN ? AND ?"; args += [min_price, max_price]

    sort_map = {"popular": "p.review_count DESC", "newest": "p.created_at DESC",
                "price_asc": "p.price ASC", "price_desc": "p.price DESC", "rating": "p.rating DESC"}
    sql += f" ORDER BY {sort_map.get(sort,'p.review_count DESC')}"

    all_products = query(sql, tuple(args)) or []
    total        = len(all_products)
    total_pages  = max(1, (total + per_page - 1) // per_page)
    paged        = all_products[(page-1)*per_page : page*per_page]

    brands    = query("SELECT DISTINCT brand FROM products WHERE is_active=1 AND brand IS NOT NULL ORDER BY brand") or []
    active_cat = (query("SELECT * FROM categories WHERE slug=?", (category_slug,), one=True) if category_slug else None)
    return render_template("products.html",
        products=paged, brands=brands, active_cat=active_cat,
        sort=sort, brand_filter=brand_filter, category_slug=category_slug,
        min_price=min_price, max_price=max_price,
        page=page, total_pages=total_pages, total=total)


@app.route("/product/<int:pid>")
def product_detail(pid):
    product = query(
        "SELECT p.*, c.name AS cat_name, c.slug AS cat_slug FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=? AND p.is_active=1",
        (pid,), one=True)
    if not product:
        abort(404)
    reviews = query(
        "SELECT r.*, u.name AS user_name FROM reviews r JOIN users u ON r.user_id=u.id WHERE r.product_id=? ORDER BY r.created_at DESC",
        (pid,)) or []
    related = query(
        "SELECT * FROM products WHERE category_id=? AND id!=? AND is_active=1 LIMIT 4",
        (product["category_id"], pid)) or []
    user_review = None
    in_wishlist = False
    if "user_id" in session:
        user_review = query("SELECT * FROM reviews WHERE product_id=? AND user_id=?",
                            (pid, session["user_id"]), one=True)
        in_wishlist = bool(query("SELECT id FROM wishlist WHERE user_id=? AND product_id=?",
                                 (session["user_id"], pid), one=True))
    return render_template("product_detail.html",
        product=product, reviews=reviews, related=related,
        user_review=user_review, in_wishlist=in_wishlist)


@app.route("/product/<int:pid>/review", methods=["POST"])
@login_required
def add_review(pid):
    rating = request.form.get("rating", type=int)
    title  = request.form.get("title", "").strip()
    review = request.form.get("review", "").strip()
    if not rating or not (1 <= rating <= 5):
        flash("Please select a valid rating.", "danger")
        return redirect(url_for("product_detail", pid=pid))
    existing = query("SELECT id FROM reviews WHERE product_id=? AND user_id=?",
                     (pid, session["user_id"]), one=True)
    if existing:
        query("UPDATE reviews SET rating=?,title=?,review=? WHERE product_id=? AND user_id=?",
              (rating, title, review, pid, session["user_id"]), commit=True)
        flash("Review updated.", "success")
    else:
        query("INSERT INTO reviews (product_id,user_id,rating,title,review) VALUES (?,?,?,?,?)",
              (pid, session["user_id"], rating, title, review), commit=True)
        flash("Review submitted.", "success")
    _update_product_rating(pid)
    return redirect(url_for("product_detail", pid=pid))


def _update_product_rating(pid):
    row = query("SELECT ROUND(AVG(CAST(rating AS REAL)),2) AS avg_r, COUNT(*) AS cnt FROM reviews WHERE product_id=?",
                (pid,), one=True)
    if row:
        query("UPDATE products SET rating=?,review_count=? WHERE id=?",
              (row["avg_r"] or 0, row["cnt"], pid), commit=True)


@app.route("/search")
def search():
    q        = request.args.get("q", "").strip()
    page     = request.args.get("page", 1, type=int)
    per_page = 12
    results  = []
    total    = 0
    if q:
        like = f"%{q}%"
        results = query(
            "SELECT p.*, c.name AS cat_name FROM products p LEFT JOIN categories c ON p.category_id=c.id "
            "WHERE p.is_active=1 AND (p.name LIKE ? OR p.brand LIKE ? OR p.description LIKE ?) ORDER BY p.rating DESC",
            (like, like, like)) or []
        total = len(results)
        results = results[(page-1)*per_page : page*per_page]
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template("search_results.html",
        q=q, results=results, total=total, page=page, total_pages=total_pages)


# Category shortcut routes
@app.route("/category/<slug>")
def category(slug):
    return redirect(url_for("products", category=slug))

@app.route("/mobile")
def mobile():
    return redirect(url_for("products", category="mobiles"))

@app.route("/laptop")
def laptop():
    return redirect(url_for("products", category="laptops"))

@app.route("/watch")
def watch():
    return redirect(url_for("products", category="watches"))

@app.route("/earbuds")
def earbuds():
    return redirect(url_for("products", category="earbuds"))

@app.route("/speaker")
def speaker():
    return redirect(url_for("products", category="speakers"))


# ──────────────────────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────────────────────
@app.route("/wishlist/toggle/<int:pid>", methods=["POST"])
@login_required
def toggle_wishlist(pid):
    if query("SELECT id FROM wishlist WHERE user_id=? AND product_id=?",
             (session["user_id"], pid), one=True):
        query("DELETE FROM wishlist WHERE user_id=? AND product_id=?",
              (session["user_id"], pid), commit=True)
        return jsonify({"in_wishlist": False, "message": "Removed from wishlist"})
    query("INSERT INTO wishlist (user_id, product_id) VALUES (?,?)",
          (session["user_id"], pid), commit=True)
    return jsonify({"in_wishlist": True, "message": "Added to wishlist"})


@app.route("/wishlist")
@login_required
def wishlist():
    items = query(
        "SELECT p.*, c.name AS cat_name FROM wishlist w "
        "JOIN products p ON w.product_id=p.id LEFT JOIN categories c ON p.category_id=c.id WHERE w.user_id=?",
        (session["user_id"],)) or []
    return render_template("wishlist.html", items=items)


# ──────────────────────────────────────────────────────────────
# CART
# ──────────────────────────────────────────────────────────────
@app.route("/cart")
def cart():
    if "user_id" not in session:
        return render_template("cart.html", items=[], subtotal=0, shipping=0, total=0)
    items = query(
        "SELECT c.id AS cart_id, c.quantity, p.id AS product_id, p.name, p.price, p.image_url, p.stock "
        "FROM cart c JOIN products p ON c.product_id=p.id WHERE c.user_id=?",
        (session["user_id"],)) or []
    subtotal = sum(i["price"] * i["quantity"] for i in items)
    shipping = 0 if subtotal >= 500 else 49
    total    = subtotal + shipping
    return render_template("cart.html", items=items, subtotal=subtotal, shipping=shipping, total=total)


@app.route("/cart/add", methods=["POST"])
@login_required
def cart_add():
    pid = request.form.get("product_id", type=int)
    qty = request.form.get("quantity", 1, type=int)
    if not pid or qty < 1:
        flash("Invalid request.", "danger")
        return redirect(request.referrer or url_for("home"))
    product = query("SELECT * FROM products WHERE id=? AND is_active=1", (pid,), one=True)
    if not product:
        flash("Product not found.", "danger")
        return redirect(request.referrer or url_for("home"))
    existing = query("SELECT * FROM cart WHERE user_id=? AND product_id=?",
                     (session["user_id"], pid), one=True)
    if existing:
        new_qty = min(existing["quantity"] + qty, product["stock"])
        query("UPDATE cart SET quantity=? WHERE id=?", (new_qty, existing["id"]), commit=True)
    else:
        query("INSERT INTO cart (user_id, product_id, quantity) VALUES (?,?,?)",
              (session["user_id"], pid, min(qty, product["stock"])), commit=True)
    flash(f'"{product["name"]}" added to cart.', "success")
    return redirect(request.referrer or url_for("cart"))


@app.route("/cart/update", methods=["POST"])
@login_required
def cart_update():
    cart_id = request.form.get("cart_id", type=int)
    qty     = request.form.get("quantity", 1, type=int)
    if qty < 1:
        query("DELETE FROM cart WHERE id=? AND user_id=?", (cart_id, session["user_id"]), commit=True)
    else:
        query("UPDATE cart SET quantity=? WHERE id=? AND user_id=?",
              (qty, cart_id, session["user_id"]), commit=True)
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:cart_id>", methods=["POST"])
@login_required
def cart_remove(cart_id):
    query("DELETE FROM cart WHERE id=? AND user_id=?", (cart_id, session["user_id"]), commit=True)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
@login_required
def cart_clear():
    query("DELETE FROM cart WHERE user_id=?", (session["user_id"],), commit=True)
    return redirect(url_for("cart"))


# ──────────────────────────────────────────────────────────────
# CHECKOUT & ORDERS
# ──────────────────────────────────────────────────────────────
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = query(
        "SELECT c.quantity, p.id AS product_id, p.name, p.price, p.image_url, p.stock "
        "FROM cart c JOIN products p ON c.product_id=p.id WHERE c.user_id=?",
        (session["user_id"],)) or []
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart"))
    user     = query("SELECT * FROM users WHERE id=?", (session["user_id"],), one=True)
    subtotal = sum(i["price"] * i["quantity"] for i in items)
    shipping = 0 if subtotal >= 500 else 49
    total    = subtotal + shipping

    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        phone   = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city    = request.form.get("city", "").strip()
        state   = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        payment = request.form.get("payment", "COD")
        if not all([name, phone, address, city, state, pincode]):
            flash("Please fill all address fields.", "danger")
            return render_template("checkout.html", items=items, user=user,
                subtotal=subtotal, shipping=shipping, total=total)
        order_id = query(
            "INSERT INTO orders (user_id,total_amount,shipping_name,shipping_phone,"
            "shipping_address,shipping_city,shipping_state,shipping_pincode,payment_method) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (session["user_id"], total, name, phone, address, city, state, pincode, payment),
            commit=True)
        for item in items:
            query("INSERT INTO order_items (order_id,product_id,name,quantity,price,image_url) VALUES (?,?,?,?,?,?)",
                  (order_id, item["product_id"], item["name"], item["quantity"],
                   item["price"], item["image_url"]), commit=True)
            query("UPDATE products SET stock=MAX(stock-?,0) WHERE id=?",
                  (item["quantity"], item["product_id"]), commit=True)
        query("DELETE FROM cart WHERE user_id=?", (session["user_id"],), commit=True)
        flash("Order placed successfully! 🎉", "success")
        return redirect(url_for("order_detail", order_id=order_id))
    return render_template("checkout.html", items=items, user=user,
        subtotal=subtotal, shipping=shipping, total=total)


@app.route("/orders")
@login_required
def orders():
    my_orders = query(
        "SELECT o.*, (SELECT COUNT(*) FROM order_items WHERE order_id=o.id) AS item_count "
        "FROM orders o WHERE o.user_id=? ORDER BY o.created_at DESC",
        (session["user_id"],)) or []
    return render_template("orders.html", orders=my_orders)


@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    order = query("SELECT * FROM orders WHERE id=? AND user_id=?",
                  (order_id, session["user_id"]), one=True)
    if not order:
        abort(404)
    items = query(
        "SELECT oi.*, p.image_url AS product_img FROM order_items oi "
        "LEFT JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?",
        (order_id,)) or []
    return render_template("order_detail.html", order=order, items=items)


@app.route("/order/<int:order_id>/track")
@login_required
def order_track(order_id):
    order = query("SELECT * FROM orders WHERE id=? AND user_id=?",
                  (order_id, session["user_id"]), one=True)
    if not order:
        abort(404)
    steps = ["pending", "processing", "shipped", "delivered"]
    current_step = steps.index(order["status"]) if order["status"] in steps else 0
    return render_template("order_tracking.html", order=order,
        steps=steps, current_step=current_step)


# ──────────────────────────────────────────────────────────────
# ADMIN
# ──────────────────────────────────────────────────────────────
@app.route("/admin")
def admin_redirect():
    return redirect(url_for("admin_dashboard" if "admin_id" in session else "admin_login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = query("SELECT * FROM admins WHERE username=?", (username,), one=True)
        if admin and check_password_hash(admin["password"], password):
            session["admin_id"]   = admin["id"]
            session["admin_name"] = admin["username"]
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None); session.pop("admin_name", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "total_users":    (query("SELECT COUNT(*) AS c FROM users", one=True) or {}).get("c", 0),
        "total_products": (query("SELECT COUNT(*) AS c FROM products WHERE is_active=1", one=True) or {}).get("c", 0),
        "total_orders":   (query("SELECT COUNT(*) AS c FROM orders", one=True) or {}).get("c", 0),
        "total_revenue":  (query("SELECT COALESCE(SUM(total_amount),0) AS c FROM orders WHERE status!='cancelled'", one=True) or {}).get("c", 0),
        "pending_orders": (query("SELECT COUNT(*) AS c FROM orders WHERE status='pending'", one=True) or {}).get("c", 0),
    }
    recent_orders = query("SELECT o.*, u.name AS user_name FROM orders o JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC LIMIT 8") or []
    low_stock     = query("SELECT * FROM products WHERE stock<=5 AND is_active=1 ORDER BY stock ASC LIMIT 6") or []
    cat_sales     = query("SELECT c.name, COUNT(oi.id) AS sold FROM order_items oi JOIN products p ON oi.product_id=p.id JOIN categories c ON p.category_id=c.id GROUP BY c.id ORDER BY sold DESC") or []
    return render_template("admin/dashboard.html", stats=stats,
        recent_orders=recent_orders, low_stock=low_stock, cat_sales=cat_sales)


@app.route("/admin/products")
@admin_required
def admin_products():
    page = request.args.get("page", 1, type=int); per_page = 15
    search = request.args.get("search", ""); cat_filter = request.args.get("category", "")
    sql = "SELECT p.*, c.name AS cat_name FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE 1=1"
    args = []
    if search:
        sql += " AND (p.name LIKE ? OR p.brand LIKE ?)"; like = f"%{search}%"; args += [like, like]
    if cat_filter:
        sql += " AND c.slug=?"; args.append(cat_filter)
    sql += " ORDER BY p.id DESC"
    all_prods = query(sql, tuple(args)) or []
    total = len(all_prods); total_pages = max(1, (total+per_page-1)//per_page)
    prods = all_prods[(page-1)*per_page:page*per_page]
    cats = query("SELECT * FROM categories") or []
    return render_template("admin/products.html", products=prods,
        page=page, total_pages=total_pages, search=search, cat_filter=cat_filter, categories=cats)


@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    cats = query("SELECT * FROM categories") or []
    if request.method == "POST":
        d = {k: request.form.get(k, "").strip() for k in
             ["name","brand","description","price","original_price","image_url","image2_url","image3_url","stock","category_id","is_featured"]}
        if not d["name"] or not d["price"]:
            flash("Name and price are required.", "danger")
            return render_template("admin/add_product.html", cats=cats)
        query("INSERT INTO products (category_id,name,brand,description,price,original_price,image_url,image2_url,image3_url,stock,is_featured) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
              (d["category_id"] or None, d["name"], d["brand"], d["description"],
               float(d["price"] or 0), float(d["original_price"] or 0) or None,
               d["image_url"], d["image2_url"], d["image3_url"],
               int(d["stock"] or 0), 1 if d["is_featured"]=="1" else 0), commit=True)
        flash("Product added.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin/add_product.html", cats=cats)


@app.route("/admin/products/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_product(pid):
    product = query("SELECT * FROM products WHERE id=?", (pid,), one=True)
    if not product: abort(404)
    cats = query("SELECT * FROM categories") or []
    if request.method == "POST":
        d = {k: request.form.get(k, "").strip() for k in
             ["name","brand","description","price","original_price","image_url","image2_url","image3_url","stock","category_id","is_featured","is_active"]}
        query("UPDATE products SET category_id=?,name=?,brand=?,description=?,price=?,original_price=?,image_url=?,image2_url=?,image3_url=?,stock=?,is_featured=?,is_active=? WHERE id=?",
              (d["category_id"] or None, d["name"], d["brand"], d["description"],
               float(d["price"] or 0), float(d["original_price"] or 0) or None,
               d["image_url"], d["image2_url"], d["image3_url"],
               int(d["stock"] or 0),
               1 if d["is_featured"]=="1" else 0,
               1 if d["is_active"]=="1" else 0, pid), commit=True)
        flash("Product updated.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin/edit_product.html", product=product, cats=cats)


@app.route("/admin/products/<int:pid>/delete", methods=["POST"])
@admin_required
def admin_delete_product(pid):
    query("UPDATE products SET is_active=0 WHERE id=?", (pid,), commit=True)
    flash("Product deactivated.", "info")
    return redirect(url_for("admin_products"))


@app.route("/admin/orders")
@admin_required
def admin_orders():
    status_filter = request.args.get("status", ""); page = request.args.get("page",1,type=int); per_page = 15
    sql = "SELECT o.*, u.name AS user_name, u.email AS user_email FROM orders o JOIN users u ON o.user_id=u.id WHERE 1=1"
    args = []
    if status_filter:
        sql += " AND o.status=?"; args.append(status_filter)
    sql += " ORDER BY o.created_at DESC"
    all_orders = query(sql, tuple(args)) or []
    total = len(all_orders); total_pages = max(1,(total+per_page-1)//per_page)
    paged = all_orders[(page-1)*per_page:page*per_page]
    return render_template("admin/orders.html", orders=paged,
        page=page, total_pages=total_pages, status_filter=status_filter, total=total)


@app.route("/admin/orders/<int:order_id>")
@admin_required
def admin_order_detail(order_id):
    order = query("SELECT o.*, u.name AS user_name, u.email AS user_email, u.phone AS user_phone FROM orders o JOIN users u ON o.user_id=u.id WHERE o.id=?", (order_id,), one=True)
    if not order: abort(404)
    items = query("SELECT oi.*, p.image_url AS product_img FROM order_items oi LEFT JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?", (order_id,)) or []
    return render_template("admin/order_detail.html", order=order, items=items)


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def admin_update_order_status(order_id):
    status = request.form.get("status")
    if status in ["pending","processing","shipped","delivered","cancelled"]:
        query("UPDATE orders SET status=? WHERE id=?", (status, order_id), commit=True)
        flash(f"Order #{order_id} updated to {status}.", "success")
    return redirect(url_for("admin_order_detail", order_id=order_id))


@app.route("/admin/users")
@admin_required
def admin_users():
    search = request.args.get("search",""); page = request.args.get("page",1,type=int); per_page = 15
    sql = "SELECT u.*, (SELECT COUNT(*) FROM orders WHERE user_id=u.id) AS order_count FROM users u WHERE 1=1"
    args = []
    if search:
        sql += " AND (u.name LIKE ? OR u.email LIKE ?)"; like = f"%{search}%"; args += [like, like]
    sql += " ORDER BY u.created_at DESC"
    all_users = query(sql, tuple(args)) or []
    total = len(all_users); total_pages = max(1,(total+per_page-1)//per_page)
    paged = all_users[(page-1)*per_page:page*per_page]
    return render_template("admin/users.html", users=paged,
        page=page, total_pages=total_pages, search=search, total=total)


@app.route("/admin/users/<int:uid>/toggle", methods=["POST"])
@admin_required
def admin_toggle_user(uid):
    user = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
    if user:
        query("UPDATE users SET is_active=? WHERE id=?",
              (0 if user["is_active"] else 1, uid), commit=True)
        flash(f"User {'deactivated' if user['is_active'] else 'activated'}.", "info")
    return redirect(url_for("admin_users"))


# ──────────────────────────────────────────────────────────────
# API
# ──────────────────────────────────────────────────────────────
@app.route("/search-api/suggestions")
def search_suggestions():
    q = request.args.get("q", "").strip()
    if len(q) < 2: return jsonify([])
    like = f"%{q}%"
    results = query("SELECT id, name, brand, price, image_url FROM products WHERE is_active=1 AND (name LIKE ? OR brand LIKE ?) LIMIT 6", (like, like)) or []
    return jsonify(results)


@app.route("/search-api/recommendations/<int:pid>")
def recommendations(pid):
    product = query("SELECT category_id FROM products WHERE id=?", (pid,), one=True)
    if not product: return jsonify([])
    recs = query("SELECT id, name, brand, price, image_url, rating FROM products WHERE category_id=? AND id!=? AND is_active=1 ORDER BY rating DESC LIMIT 4",
                 (product["category_id"], pid)) or []
    return jsonify(recs)


# ──────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ──────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ──────────────────────────────────────────────────────────────
# LEGACY REDIRECTS
# ──────────────────────────────────────────────────────────────
@app.route("/product")
def product():
    return redirect(url_for("products"))

@app.route("/order")
def order():
    return redirect(url_for("orders"))

@app.route("/track")
def track():
    return redirect(url_for("orders"))


# ──────────────────────────────────────────────────────────────
# INIT DB + RUN
# ──────────────────────────────────────────────────────────────
def init_db():
    """Create tables and seed data on first run."""
    if os.path.exists(DB_PATH):
        return
    import init_db as idb
    idb.run()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
