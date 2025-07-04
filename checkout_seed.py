import psycopg2
import pymongo
import redis

# --- Koneksi ---
pg_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
pg_cursor = pg_conn.cursor()

mongo_client = pymongo.MongoClient("mongodb://admin:admin123@localhost:27017/")
mongo_db = mongo_client["ecommerce"]
mongo_collection = mongo_db["produk_metadata"]

redis_client = redis.Redis(host="localhost", port=6379, db=0)

# --- Data Dummy ---
users = [
    (1, 'Ado', 'ado@example.com'),
    (2, 'Budi', 'budi@example.com'),
    (3, 'Cici', 'cici@example.com'),
    (4, 'Dian', 'dian@example.com'),
    (5, 'Eko', 'eko@example.com'),
]

products = [
    ('P123', 'Keyboard RGB', 300000),
    ('P124', 'Mouse Wireless', 150000),
    ('P125', 'Monitor 24 Inch', 1200000),
    ('P126', 'Headset Gaming', 500000),
    ('P127', 'Webcam Full HD', 250000),
]

metadata = {
    'P123': "Keyboard RGB tahan air dengan lampu RGB",
    'P124': "Mouse tanpa kabel dengan baterai tahan lama",
    'P125': "Monitor IPS Full HD 24 inch",
    'P126': "Headset gaming dengan noise cancellation",
    'P127': "Webcam 1080p dengan mikrofon stereo",
}

# --- Insert Users ---
print("➕ Seeding users...")
for u in users:
    pg_cursor.execute(
        "INSERT INTO users (id, nama, email) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;",
        u
    )

# --- Insert Products ---
print("➕ Seeding produk...")
for p in products:
    pg_cursor.execute(
        "INSERT INTO produk (sku, nama, harga) VALUES (%s, %s, %s) ON CONFLICT (sku) DO NOTHING;",
        p
    )

pg_conn.commit()

# --- Insert Metadata ke MongoDB ---
print("➕ Seeding metadata produk (MongoDB)...")
for sku, desc in metadata.items():
    mongo_collection.update_one(
        {"sku": sku},
        {"$set": {
            "sku": sku,
            "deskripsi": desc,
            "tags": ["ecommerce", "produk", sku]
        }},
        upsert=True
    )

# --- Set stok awal di Redis ---
print("➕ Set stok awal ke Redis...")
for sku, _, _ in products:
    redis_client.set(f"stok:{sku}", 20)

print("\n✅ Seeder selesai: 5 user, 5 produk, metadata & stok siap!")

# --- Cleanup ---
pg_cursor.close()
pg_conn.close()
mongo_client.close()
