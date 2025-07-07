from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import asyncpg
import redis
from pymongo import MongoClient
from datetime import datetime
from fastapi import Form

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Koneksi ke DB
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
mongo_client = MongoClient("mongodb://admin:admin123@mongo:27017/?authSource=admin")
mongo_db = mongo_client["ecommerce"]
produk_metadata = mongo_db["produk_metadata"]

db_pool = None
def set_db_pool(pool):
    global db_pool
    db_pool = pool

# GET form checkout
@router.get("/checkout")
async def checkout_form(request: Request, sku: str):
    if db_pool is None:
        return {"error": "DB not initialized"}

    # Ambil produk dari PostgreSQL
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT sku, nama, harga FROM produk WHERE sku = $1", sku)
    # Redis
    stok = redis_client.get(f"stok:{sku}") or "0"
    if not row:
        return {"error": "Produk tidak ditemukan"}

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "sku": row["sku"],
        "nama": row["nama"],
        "harga": row["harga"],
        "stok": stok   
    })

# POST form checkout


@router.post("/checkout")
async def process_checkout(
    request: Request,
    user_id: int = Form(...),
    sku: str = Form(...),
    nama: str = Form(...),
    harga: float = Form(...),
    jumlah: int = Form(...)
):
    total = harga * jumlah
    created_at = datetime.utcnow()

    # Cek stok dulu
    stok_key = f"stok:{sku}"
    stok = redis_client.get(stok_key) or "0"
    if int(stok) < jumlah:
        return templates.TemplateResponse("checkout_failed.html", {
            "request": request,
            "error": "Stok tidak mencukupi."
        })

    # Simpan ke orders
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO orders (user_id, sku, jumlah, total, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, sku, jumlah, total, created_at)

    # Kurangi stok di Redis
    redis_client.decrby(stok_key, jumlah)

    return templates.TemplateResponse("checkout_success.html", {
        "request": request,
        "nama": nama,
        "total": total,
        "jumlah": jumlah
    })
