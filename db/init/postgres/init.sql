-- ================================
-- 📦 INIT SQL - E-Commerce Citus
-- ================================

-- USERS TABLE (reference)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(100),
  email VARCHAR(100) UNIQUE
);

-- PRODUK TABLE (distributed by sku)
CREATE TABLE IF NOT EXISTS produk (
  sku VARCHAR(20) PRIMARY KEY,
  nama VARCHAR(100),
  harga NUMERIC(10, 2)
);

-- ORDERS TABLE (distributed by id)
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  sku VARCHAR(20) REFERENCES produk(sku),
  jumlah INTEGER,
  total NUMERIC(10, 2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ===================
-- 🚀 INSERT SEED DATA
-- ===================

-- USERS
INSERT INTO users (id, nama, email) VALUES
  (1, 'Ado', 'ado@example.com'),
  (2, 'Budi', 'budi@example.com'),
  (3, 'Cici', 'cici@example.com')
ON CONFLICT DO NOTHING;

-- PRODUK
INSERT INTO produk (sku, nama, harga) VALUES
  ('P123', 'Keyboard RGB', 300000),
  ('P124', 'Mouse Wireless', 150000),
  ('P125', 'Monitor 24 Inch', 1200000)
ON CONFLICT DO NOTHING;

