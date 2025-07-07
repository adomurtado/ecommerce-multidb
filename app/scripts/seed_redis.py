import redis

# Koneksi ke Redis di dalam jaringan Docker
r = redis.Redis(host="redis", port=6379)

# Data stok dummy
stok_data = {
    "P123": 20,
    "P124": 50,
    "P125": 0,
}

for sku, jumlah in stok_data.items():
    r.set(f"stok:{sku}", jumlah)

print("✅ Redis seeded dengan data stok produk.")
