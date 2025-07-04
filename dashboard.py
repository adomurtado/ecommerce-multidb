import psycopg2
import pymongo
import redis
from tabulate import tabulate

# Koneksi PostgreSQL
pg_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",  # ganti sesuai password lo
    host="localhost",
    port="5432"
)
pg_cursor = pg_conn.cursor()

# Koneksi MongoDB
# Koneksi MongoDB (dengan autentikasi)
mongo_client = pymongo.MongoClient("mongodb://admin:admin123@localhost:27017/")
mongo_db = mongo_client["ecommerce"]
mongo_collection = mongo_db["produk_metadata"]

# Koneksi Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0)

print("=== 📦 DASHBOARD DATA DISTRIBUSI E-COMMERCE ===\n")

# 1. Users
print("🧩 USERS (PostgreSQL - Reference Table)")
pg_cursor.execute("SELECT id, nama, email FROM users LIMIT 5;")
users = pg_cursor.fetchall()
print(tabulate(users, headers=["ID", "Nama", "Email"], tablefmt="grid"))
print()

# 2. Produk
print("📦 PRODUK (PostgreSQL - Reference Table)")
pg_cursor.execute("SELECT sku, nama, harga FROM produk LIMIT 5;")
produk = pg_cursor.fetchall()
print(tabulate(produk, headers=["SKU", "Nama", "Harga"], tablefmt="grid"))
print()

# 3. Orders
print("🛒 ORDERS (PostgreSQL - Sharded Table)")
pg_cursor.execute("SELECT id, user_id, sku, jumlah, total FROM orders LIMIT 5;")
orders = pg_cursor.fetchall()
print(tabulate(orders, headers=["ID", "User ID", "SKU", "Jumlah", "Total"], tablefmt="grid"))
print()

# 4. Produk Metadata (MongoDB)
print("📖 PRODUK METADATA (MongoDB)")
metadata = mongo_collection.find({}, {"_id": 0, "sku": 1, "deskripsi": 1}).limit(5)
rows = [(doc["sku"], doc["deskripsi"]) for doc in metadata]
print(tabulate(rows, headers=["SKU", "Deskripsi"], tablefmt="grid"))
print()

# 5. Stok Produk (Redis)
print("📦 STOK PRODUK (Redis)")
keys = redis_client.keys("stok:*")
stok_data = []
for key in keys:
    sku = key.decode().split(":")[1]
    jumlah = redis_client.get(key).decode()
    stok_data.append((sku, jumlah))
print(tabulate(stok_data, headers=["SKU", "Stok"], tablefmt="grid"))
print()

# Tutup koneksi
pg_cursor.close()
pg_conn.close()
mongo_client.close()
