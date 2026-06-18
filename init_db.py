"""
AccessEase 2.0 — SQLite Database Initializer
Run this once to create tables and seed data:  python init_db.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.environ.get("DB_PATH", "accessease.db")


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  slug       TEXT NOT NULL UNIQUE,
  icon       TEXT DEFAULT 'fa-tag',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  password   TEXT NOT NULL,
  phone      TEXT,
  address    TEXT,
  city       TEXT,
  state      TEXT,
  pincode    TEXT,
  is_active  INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS admins (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  username   TEXT NOT NULL UNIQUE,
  password   TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id    INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  name           TEXT NOT NULL,
  brand          TEXT,
  description    TEXT,
  price          REAL NOT NULL,
  original_price REAL,
  image_url      TEXT,
  image2_url     TEXT,
  image3_url     TEXT,
  stock          INTEGER DEFAULT 0,
  rating         REAL DEFAULT 0.0,
  review_count   INTEGER DEFAULT 0,
  is_featured    INTEGER DEFAULT 0,
  is_active      INTEGER DEFAULT 1,
  created_at     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cart (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  quantity   INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS wishlist (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS orders (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  total_amount     REAL NOT NULL,
  status           TEXT DEFAULT 'pending'
                   CHECK(status IN ('pending','processing','shipped','delivered','cancelled')),
  shipping_name    TEXT,
  shipping_phone   TEXT,
  shipping_address TEXT,
  shipping_city    TEXT,
  shipping_state   TEXT,
  shipping_pincode TEXT,
  payment_method   TEXT DEFAULT 'COD',
  payment_status   TEXT DEFAULT 'pending',
  created_at       TEXT DEFAULT (datetime('now')),
  updated_at       TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS order_items (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id   INTEGER NOT NULL REFERENCES orders(id)   ON DELETE CASCADE,
  product_id INTEGER          REFERENCES products(id) ON DELETE SET NULL,
  name       TEXT NOT NULL,
  quantity   INTEGER NOT NULL,
  price      REAL NOT NULL,
  image_url  TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  user_id    INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
  rating     INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
  title      TEXT,
  review     TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE (product_id, user_id)
);
"""

CATEGORIES = [
    ("Mobiles",  "mobiles",  "fa-mobile-alt"),
    ("Laptops",  "laptops",  "fa-laptop"),
    ("Watches",  "watches",  "fa-clock"),
    ("Earbuds",  "earbuds",  "fa-headphones"),
    ("Speakers", "speakers", "fa-volume-up"),
]

PRODUCTS = [
    # (category_slug, name, brand, description, price, original_price, image_url, stock, rating, review_count, is_featured)
    # ── Mobiles ──
    ("mobiles", "Samsung Galaxy S24 Ultra", "Samsung",
     "200MP camera, Snapdragon 8 Gen 3, 5000mAh, 45W charging, S Pen included. The ultimate Android flagship.",
     119999, 149999, "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80", 25, 4.7, 312, 1),
    ("mobiles", "Apple iPhone 15 Pro", "Apple",
     "A17 Pro chip, 48MP main camera, titanium design, Action Button, USB-C. ProMotion 120Hz Super Retina XDR.",
     134900, 159900, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&q=80", 30, 4.8, 520, 1),
    ("mobiles", "OnePlus 12R", "OnePlus",
     "Snapdragon 8 Gen 2, 50MP Sony camera, 5500mAh, 100W SUPERVOOC charging, 6.78\" fluid AMOLED.",
     42999, 49999, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", 40, 4.5, 278, 1),
    ("mobiles", "Xiaomi 14 Pro", "Xiaomi",
     "Leica optics, Snapdragon 8 Gen 3, 50MP triple camera, HyperOS, 120W HyperCharge.",
     74999, 84999, "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400&q=80", 20, 4.6, 190, 0),
    # ── Laptops ──
    ("laptops", "Apple MacBook Air M3", "Apple",
     "M3 chip, 8GB RAM, 256GB SSD, 15.3\" Liquid Retina, 18-hour battery, fanless design.",
     134900, 149900, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80", 18, 4.9, 445, 1),
    ("laptops", "Lenovo IdeaPad Slim 5", "Lenovo",
     "Intel Core i5-13th Gen, 16GB RAM, 512GB SSD, 14\" FHD IPS, backlit keyboard.",
     62990, 79990, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", 35, 4.4, 312, 1),
    ("laptops", "ASUS ROG Strix G16", "ASUS",
     "Intel i7-13650HX, 16GB DDR5, RTX 4060 8GB, 16\" 165Hz FHD gaming laptop.",
     129990, 149990, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80", 12, 4.7, 230, 0),
    ("laptops", "HP Pavilion 15", "HP",
     "AMD Ryzen 5 7520U, 16GB RAM, 512GB SSD, 15.6\" FHD, Windows 11, B&O audio.",
     54990, 69990, "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&q=80", 28, 4.3, 189, 0),
    # ── Watches ──
    ("watches", "Apple Watch Series 9", "Apple",
     "Always-on Retina, S9 chip, Double Tap gesture, blood oxygen, ECG, crash detection.",
     41900, 45900, "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&q=80", 22, 4.8, 380, 1),
    ("watches", "Samsung Galaxy Watch 6 Classic", "Samsung",
     "Rotating bezel, advanced sleep coaching, BIA body composition, ECG, blood pressure.",
     32999, 39999, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", 18, 4.6, 245, 0),
    ("watches", "Noise ColorFit Ultra 3", "Noise",
     "1.96\" AMOLED, BT calling, 100+ sports modes, SpO2, heart rate, 7-day battery, IP68.",
     3999, 6999, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80", 50, 4.2, 420, 1),
    ("watches", "Garmin Forerunner 265", "Garmin",
     "AMOLED display, advanced running dynamics, HRV, morning report, 15-day battery.",
     39999, 44999, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&q=80", 14, 4.7, 178, 0),
    # ── Earbuds ──
    ("earbuds", "Sony WF-1000XM5", "Sony",
     "Industry-leading ANC, 30-hour total battery, LDAC Hi-Res audio, multipoint connection.",
     19990, 24990, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80", 30, 4.8, 560, 1),
    ("earbuds", "Apple AirPods Pro (2nd Gen)", "Apple",
     "H2 chip, Adaptive Transparency, Personalized Spatial Audio, 6-hour battery, IP54.",
     24900, 26900, "https://images.unsplash.com/photo-1588423771073-b8903fbb85b5?w=400&q=80", 25, 4.7, 720, 1),
    ("earbuds", "boAt Airdopes 141", "boAt",
     "ENx technology, 42-hour total battery, IPX4, ASAP Charge, low latency gaming mode.",
     1499, 3990, "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400&q=80", 80, 4.1, 1250, 1),
    ("earbuds", "OnePlus Buds Pro 2", "OnePlus",
     "Dynaudio co-developed, LHDC 5.0, 48dB ANC, Spatial Audio, 39-hour battery, IP55.",
     9999, 12999, "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&q=80", 40, 4.5, 390, 0),
    # ── Speakers ──
    ("speakers", "JBL Charge 5", "JBL",
     "IP67 waterproof, 20 hours playtime, powerbank function, JBL Pro Sound, PartyBoost.",
     13999, 17999, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&q=80", 35, 4.7, 485, 1),
    ("speakers", "Sony SRS-XB43", "Sony",
     "Extra Bass, 24-hour battery, IP67, Party Connect, live sound mode.",
     14990, 19990, "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&q=80", 20, 4.6, 320, 0),
    ("speakers", "boAt Stone 1200F", "boAt",
     "14W RMS, TWS pairing, 10-hour battery, IPX5, built-in FM radio, USB playback.",
     2499, 5490, "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80", 60, 4.0, 870, 1),
    ("speakers", "Marshall Emberton III", "Marshall",
     "360-degree sound, 32-hour battery, IP67, Multi-host, iconic Marshall look.",
     14999, 17999, "https://images.unsplash.com/photo-1616469829941-c7200edec809?w=400&q=80", 15, 4.8, 290, 1),
]


def run():
    print(f"Initializing database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # Categories
    for name, slug, icon in CATEGORIES:
        conn.execute("INSERT OR IGNORE INTO categories (name,slug,icon) VALUES (?,?,?)",
                     (name, slug, icon))

    # Admin (username: admin  password: Admin@123)
    conn.execute("INSERT OR IGNORE INTO admins (username,password) VALUES (?,?)",
                 ("admin", generate_password_hash("Admin@123")))

    # Products
    for cat_slug, name, brand, desc, price, orig, img, stock, rating, rev_count, featured in PRODUCTS:
        row = conn.execute("SELECT id FROM categories WHERE slug=?", (cat_slug,)).fetchone()
        cat_id = row[0] if row else None
        conn.execute(
            "INSERT OR IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (cat_id, name, brand, desc, price, orig, img, stock, rating, rev_count, featured)
        )

    conn.commit()
    conn.close()
    print(f"Database initialized with {len(PRODUCTS)} products across {len(CATEGORIES)} categories.")
    print("Admin credentials: username=admin  password=Admin@123")


if __name__ == "__main__":
    run()
