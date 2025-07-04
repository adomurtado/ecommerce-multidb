-- Users Table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(100),
  email VARCHAR(100) UNIQUE,

);

-- Produk Table
CREATE TABLE IF NOT EXISTS produk (
  sku VARCHAR(20) PRIMARY KEY,
  nama VARCHAR(100),
  harga NUMERIC(10, 2),
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  sku VARCHAR(20) REFERENCES produk(sku),
  jumlah INTEGER,
  total NUMERIC(10, 2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- INSERT Data Users
INSERT INTO users (id, nama, email)
VALUES
  (1, 'Ado', 'ado@example.com'),
  (2, 'Budi', 'budi@example.com'),
  (3, 'Cici', 'cici@example.com');

-- INSERT Data Produk
INSERT INTO produk (sku, nama, harga, kategori)
VALUES
  ('P123', 'Keyboard RGB', 300000, ),
  ('P124', 'Mouse Wireless', 150000, ),
  ('P125', 'Monitor 24 Inch', 1200000, );

-- INSERT Data Orders
INSERT INTO orders (id, user_id, sku, jumlah, total, created_at)
VALUES
  (1, 1, 'P123', 2, 600000, '2025-07-03 08:57:22.587569'),
  (2, 2, 'P124', 1, 150000, '2025-07-03 08:57:22.587569'),
  (3, 3, 'P125', 1, 1200000, '2025-07-03 08:57:22.587569');
