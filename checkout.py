import psycopg2
import redis
from pymongo import MongoClient

# Input dari pengguna
USER_ID = 1
SKU = "P123"
JUMLAH = 2

# 1. Koneksi PostgreSQL (Citus Master)
pg_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
pg_cur = pg_conn.cursor()

# 2. Ambil info produk dari Postgre
pg_cur.execute("SELECT nama, harga FROM produk WHERE sku = %s", (SKU,))
produk = pg_cur.fetchone()
if not produk:
    print("❌ Produk tidak ditemukan di PostgreSQL")
    exit()

nama_produk, harga = produk
total = harga * JUMLAH

# 3. Ambil deskripsi dari MongoDB
mongo = MongoClient("mongodb://admin:admin123@localhost:27017/", authSource="admin")
mongo_db = mongo["ecom"]
meta = mongo_db["produk_metadata"].find_one({"sku": SKU})
if not meta:
    print("⚠️ Deskripsi tidak ditemukan di MongoDB")
    deskripsi = "Deskripsi tidak tersedia"
else:
    deskripsi = meta.get("deskripsi", "Deskripsi kosong")

# 4. Cek dan update stok dari Redis
r = redis.Redis(host="localhost", port=6379, db=0)
stok_key = f"stok:{SKU}"
stok = r.get(stok_key)
if not stok:
    print("⚠️ Produk tidak memiliki stok di Redis")
    exit()

stok = int(stok)
if stok < JUMLAH:
    print(f"❌ Stok tidak cukup. Tersedia: {stok}, Diminta: {JUMLAH}")
    exit()

# Update stok
r.decrby(stok_key, JUMLAH)

# 5. Simpan order ke PostgreSQL
pg_cur.execute(
    "INSERT INTO orders (user_id, sku, jumlah, total) VALUES (%s, %s, %s, %s)",
    (USER_ID, SKU, JUMLAH, total)
)
pg_conn.commit()

# 6. Output hasil transaksi
print("\n✅ Transaksi Berhasil:")
print(f"Produk     : {nama_produk}")
print(f"Deskripsi  : {deskripsi}")
print(f"Harga      : {harga}")
print(f"Jumlah     : {JUMLAH}")
print(f"Total      : {total}")
print(f"Stok Sisa  : {int(r.get(stok_key))}")

# Tutup koneksi
pg_cur.close()
pg_conn.close()
