from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2
import pymongo
import redis

app = FastAPI(title="E-Commerce Distributed Dashboard", version="1.0")
templates = Jinja2Templates(directory="templates")

# Global connections (non-PostgreSQL)
mongo_client = pymongo.MongoClient("mongodb://admin:admin123@mongo:27017/", authSource="admin")
mongo_coll = mongo_client["ecommerce"]["produk_metadata"]
r = redis.Redis(host="redis", port=6379, db=0)

# Data Models
class User(BaseModel):
    id: int
    nama: str
    email: str

class Produk(BaseModel):
    sku: str
    nama: str
    harga: int

class Order(BaseModel):
    id: int
    user_id: int
    sku: str
    jumlah: int
    total: int

class Metadata(BaseModel):
    sku: str
    deskripsi: str

class Stok(BaseModel):
    sku: str
    stok: int

# Modular PostgreSQL function
def get_pg_data():
    with psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="citus_master",
        port="5432"
    ) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            pg_cur.execute("SET citus.enable_repartition_joins TO on;")

            pg_cur.execute("SELECT id, nama, email FROM users LIMIT 10")
            users = [dict(id=r[0], nama=r[1], email=r[2]) for r in pg_cur.fetchall()]

            pg_cur.execute("SELECT sku, nama, harga FROM produk LIMIT 5")
            produk_list = [dict(sku=r[0], nama=r[1], harga=r[2]) for r in pg_cur.fetchall()]

            pg_cur.execute("SELECT id, user_id, sku, jumlah, total FROM orders LIMIT 5")
            orders = [dict(id=r[0], user_id=r[1], sku=r[2], jumlah=r[3], total=r[4]) for r in pg_cur.fetchall()]

            pg_cur.execute("""
                SELECT
                  o.id, o.jumlah, o.total, o.created_at,
                  u.nama AS pemesan,
                  p.nama AS nama_produk, p.harga
                FROM
                  orders o
                JOIN users u ON o.user_id = u.id
                JOIN produk p ON o.sku = p.sku
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            order_detail = [dict(
                id=r[0], jumlah=r[1], total=r[2], created_at=r[3],
                pemesan=r[4], nama_produk=r[5], harga=r[6]
            ) for r in pg_cur.fetchall()]

    return users, produk_list, orders, order_detail

# Modular MongoDB

def get_mongo_metadata(limit=5):
    docs = mongo_coll.find({}, {"_id": 0, "sku": 1, "deskripsi": 1}).limit(limit)
    metadata = list(docs)
    metadata_map = {doc["sku"]: doc["deskripsi"] for doc in metadata}
    return metadata, metadata_map

# Modular Redis

def get_redis_stok(limit=5):
    keys = r.keys("stok:*")
    stok = []
    stok_map = {}
    for k in keys[:limit]:
        sku = k.decode().split(":")[1]
        jumlah = int(r.get(k))
        stok.append({"sku": sku, "jumlah": jumlah})
        stok_map[sku] = jumlah
    return stok, stok_map

# Route
@app.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request):
    users, produk_list, orders, order_detail = get_pg_data()
    metadata, metadata_map = get_mongo_metadata()
    stok, stok_map = get_redis_stok()

    produk_full = []
    for p in produk_list:
        produk_full.append({
            "sku": p["sku"],
            "nama": p["nama"],
            "harga": p["harga"],
            "kategori": "-",  # tidak ada join kategori karena tabel tidak tersedia
            "deskripsi": metadata_map.get(p["sku"], "tidak tersedia"),
            "stok": stok_map.get(p["sku"], 0)
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard Distribusi E-Commerce",
        "users": users,
        "produk_list": produk_list,
        "orders": orders,
        "metadata": metadata,
        "stok": stok,
        "produk_full": produk_full,
        "order_detail": order_detail
    })
