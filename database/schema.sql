-- =====================================================
-- AccessEase 2.0 — MySQL Database Schema
-- Run: mysql -u root -p < database/schema.sql
-- =====================================================

CREATE DATABASE IF NOT EXISTS accesseasedb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE accesseasedb;

-- ── Categories ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(100) NOT NULL,
  slug  VARCHAR(100) NOT NULL UNIQUE,
  icon  VARCHAR(60)  DEFAULT 'fa-tag',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Users ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(150) NOT NULL,
  email      VARCHAR(200) NOT NULL UNIQUE,
  password   VARCHAR(300) NOT NULL,
  phone      VARCHAR(20),
  address    TEXT,
  city       VARCHAR(100),
  state      VARCHAR(100),
  pincode    VARCHAR(10),
  is_active  TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Admins ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admins (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(100) NOT NULL UNIQUE,
  password   VARCHAR(300) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Products ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  category_id    INT,
  name           VARCHAR(300) NOT NULL,
  brand          VARCHAR(100),
  description    TEXT,
  price          DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2),
  image_url      TEXT,
  image2_url     TEXT,
  image3_url     TEXT,
  stock          INT DEFAULT 0,
  rating         DECIMAL(3,2) DEFAULT 0.00,
  review_count   INT DEFAULT 0,
  is_featured    TINYINT(1) DEFAULT 0,
  is_active      TINYINT(1) DEFAULT 1,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ── Cart ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  product_id INT NOT NULL,
  quantity   INT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_cart (user_id, product_id),
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ── Wishlist ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wishlist (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  product_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_wishlist (user_id, product_id),
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ── Orders ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  user_id          INT NOT NULL,
  total_amount     DECIMAL(10,2) NOT NULL,
  status           ENUM('pending','processing','shipped','delivered','cancelled') DEFAULT 'pending',
  shipping_name    VARCHAR(150),
  shipping_phone   VARCHAR(20),
  shipping_address TEXT,
  shipping_city    VARCHAR(100),
  shipping_state   VARCHAR(100),
  shipping_pincode VARCHAR(10),
  payment_method   VARCHAR(50) DEFAULT 'COD',
  payment_status   ENUM('pending','paid','failed','refunded') DEFAULT 'pending',
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Order Items ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  order_id   INT NOT NULL,
  product_id INT,
  name       VARCHAR(300) NOT NULL,
  quantity   INT NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  image_url  TEXT,
  FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- ── Reviews ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  user_id    INT NOT NULL,
  rating     TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  title      VARCHAR(200),
  review     TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_review (product_id, user_id),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE
);

-- =====================================================
-- SEED DATA
-- =====================================================

INSERT IGNORE INTO categories (name, slug, icon) VALUES
  ('Mobiles',  'mobiles',  'fa-mobile-alt'),
  ('Laptops',  'laptops',  'fa-laptop'),
  ('Watches',  'watches',  'fa-clock'),
  ('Earbuds',  'earbuds',  'fa-headphones'),
  ('Speakers', 'speakers', 'fa-volume-up');

-- Admin user: username=admin  password=Admin@123
INSERT IGNORE INTO admins (username, password) VALUES (
  'admin',
  'scrypt:32768:8:1$h2fW7xzd08aHfPzQ$03bbc381901d756f102a43db950a1b6da609d8111214c4b2e5abfb98dfbca3103655dcff232ebcb7a5cf048f7b8d02aba5e7ee38a0774bb2f123a8bed7174ae0'
);

-- ── Mobiles ───────────────────────────────────────────
INSERT IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES
(1,'Samsung Galaxy S24 Ultra','Samsung','200MP camera, Snapdragon 8 Gen 3, 5000mAh, 45W charging, S Pen included.',119999,149999,'https://m.media-amazon.com/images/I/71Sa3dqTqzL._SL1500_.jpg',25,4.7,312,1),
(1,'Apple iPhone 15 Pro','Apple','A17 Pro chip, 48MP main camera, titanium design, Action Button, USB-C.',134900,159900,'https://m.media-amazon.com/images/I/71d-1JfqBhL._SL1500_.jpg',30,4.8,520,1),
(1,'OnePlus 12R','OnePlus','Snapdragon 8 Gen 2, 50MP Sony camera, 5500mAh, 100W SUPERVOOC charging.',42999,49999,'https://m.media-amazon.com/images/I/71TKJ8RfxML._SL1500_.jpg',40,4.5,278,1),
(1,'Xiaomi 14 Pro','Xiaomi','Leica optics, Snapdragon 8 Gen 3, 50MP triple camera, HyperOS.',74999,84999,'https://m.media-amazon.com/images/I/61MIE3QGRVL._SL1500_.jpg',20,4.6,190,0);

-- ── Laptops ───────────────────────────────────────────
INSERT IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES
(2,'Apple MacBook Air M3','Apple','M3 chip, 8GB RAM, 256GB SSD, 15.3" Liquid Retina, 18-hour battery.',134900,149900,'https://m.media-amazon.com/images/I/71vFKBpKakL._SL1500_.jpg',18,4.9,445,1),
(2,'Lenovo IdeaPad Slim 5','Lenovo','Intel Core i5-13th Gen, 16GB RAM, 512GB SSD, 14" FHD IPS.',62990,79990,'https://m.media-amazon.com/images/I/61mtCPQSmXL._SL1500_.jpg',35,4.4,312,1),
(2,'ASUS ROG Strix G16','ASUS','Intel i7-13650HX, 16GB DDR5, RTX 4060 8GB, 16" 165Hz gaming laptop.',129990,149990,'https://m.media-amazon.com/images/I/71y7J0EGVNL._SL1500_.jpg',12,4.7,230,0),
(2,'HP Pavilion 15','HP','AMD Ryzen 5 7520U, 16GB RAM, 512GB SSD, 15.6" FHD, Windows 11.',54990,69990,'https://m.media-amazon.com/images/I/81n+5V9k3WL._SL1500_.jpg',28,4.3,189,0);

-- ── Watches ───────────────────────────────────────────
INSERT IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES
(3,'Apple Watch Series 9','Apple','Always-on Retina, S9 chip, Double Tap, blood oxygen, ECG, 18-hour battery.',41900,45900,'https://m.media-amazon.com/images/I/71qFtYMzGmL._SL1500_.jpg',22,4.8,380,1),
(3,'Samsung Galaxy Watch 6 Classic','Samsung','Rotating bezel, sleep coaching, BIA, ECG, blood pressure, Wear OS 4.',32999,39999,'https://m.media-amazon.com/images/I/71X3HNJN8cL._SL1500_.jpg',18,4.6,245,0),
(3,'Noise ColorFit Ultra 3','Noise','1.96" AMOLED, BT calling, 100+ sports modes, SpO2, 7-day battery, IP68.',3999,6999,'https://m.media-amazon.com/images/I/61QwNm4ZYZL._SL1500_.jpg',50,4.2,420,1),
(3,'Garmin Forerunner 265','Garmin','AMOLED, advanced running dynamics, HRV, morning report, 15-day battery.',39999,44999,'https://m.media-amazon.com/images/I/71bYDQQ1VAL._SL1500_.jpg',14,4.7,178,0);

-- ── Earbuds ───────────────────────────────────────────
INSERT IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES
(4,'Sony WF-1000XM5','Sony','Industry-leading ANC, 30-hour battery, LDAC Hi-Res audio, multipoint.',19990,24990,'https://m.media-amazon.com/images/I/61X1gGOxteL._SL1500_.jpg',30,4.8,560,1),
(4,'Apple AirPods Pro (2nd Gen)','Apple','H2 chip, Adaptive Transparency, Personalized Spatial Audio, IP54.',24900,26900,'https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg',25,4.7,720,1),
(4,'boAt Airdopes 141','boAt','ENx technology, 42-hour total battery, IPX4, ASAP Charge, low latency.',1499,3990,'https://m.media-amazon.com/images/I/61yGdm9SLJL._SL1500_.jpg',80,4.1,1250,1),
(4,'OnePlus Buds Pro 2','OnePlus','Dynaudio co-developed, LHDC 5.0, 48dB ANC, Spatial Audio, 39-hour battery.',9999,12999,'https://m.media-amazon.com/images/I/61-i8OQIITL._SL1500_.jpg',40,4.5,390,0);

-- ── Speakers ─────────────────────────────────────────
INSERT IGNORE INTO products (category_id,name,brand,description,price,original_price,image_url,stock,rating,review_count,is_featured) VALUES
(5,'JBL Charge 5','JBL','IP67 waterproof, 20 hours playtime, powerbank function, PartyBoost.',13999,17999,'https://m.media-amazon.com/images/I/61Rp9LMFP5L._SL1500_.jpg',35,4.7,485,1),
(5,'Sony SRS-XB43','Sony','Extra Bass, 24-hour battery, IP67, Party Connect, live sound mode.',14990,19990,'https://m.media-amazon.com/images/I/61+5g4PHMTL._SL1500_.jpg',20,4.6,320,0),
(5,'boAt Stone 1200F','boAt','14W RMS, TWS pairing, 10-hour battery, IPX5, built-in FM, USB playback.',2499,5490,'https://m.media-amazon.com/images/I/71MalF9BVJL._SL1500_.jpg',60,4.0,870,1),
(5,'Marshall Emberton III','Marshall','360-degree sound, 32-hour battery, IP67, Multi-host, iconic Marshall look.',14999,17999,'https://m.media-amazon.com/images/I/71F3FHiHxjL._SL1500_.jpg',15,4.8,290,1);
