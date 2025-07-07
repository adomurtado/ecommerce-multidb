from fastapi import APIRouter, Request  # <- ini penting
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi import status

import redis
from pymongo import MongoClient

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# Redis
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

# Mongo
mongo_client = MongoClient("mongodb://admin:admin123@mongo:27017/?authSource=admin")
mongo_db = mongo_client["ecommerce"]
mongo_collection = mongo_db["produk_metadata"]

# PostgreSQL pool akan diinject dari main.py
db_pool = None

def set_db_pool(pool):
    global db_pool
    db_pool = pool
@router.get("/dashboard")
async def admin_dashboard(request: Request):
    # PostgreSQL
    async with db_pool.acquire() as conn:
        produk_count = await conn.fetchval("SELECT COUNT(*) FROM produk")
        order_count = await conn.fetchval("SELECT COUNT(*) FROM orders")

    # Redis: hitung stok habis
    stok_keys = redis_client.keys("stok:*")
    produk_habis = sum(1 for key in stok_keys if int(redis_client.get(key) or 0) <= 0)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_produk": produk_count,
        "total_order": order_count,
        "produk_habis": produk_habis
    })

async def get_all_produk():
    if db_pool is None:
        return []
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT sku, nama, harga FROM produk ORDER BY sku")

    produk_list = []
    for row in rows:
        sku = row["sku"]
        nama = row["nama"]
        harga = row["harga"]

        stok = redis_client.get(f"stok:{sku}") or "0"
        metadata = mongo_collection.find_one({"sku": sku}) or {}
        deskripsi = metadata.get("deskripsi", "")
        gambar_url = metadata.get("gambar_url", "https://picsum.photos/150")

        produk_list.append({
            "sku": sku,
            "nama": nama,
            "harga": harga,
            "stok": stok,
            "deskripsi": deskripsi,
            "gambar_url": gambar_url
        })
    return produk_list

@router.get("/dashboard/produk")
async def dashboard_produk(request: Request):
    produk_list = await get_all_produk()
    return templates.TemplateResponse("dashboard_produk_list.html", {
        "request": request,
        "produk": produk_list
    })

@router.get("/produk")
async def list_produk(request: Request):
    if db_pool is None:
        return {"error": "DB not initialized"}
    
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT sku, nama, harga FROM produk ORDER BY sku")

    produk_list = []
    for row in rows:
        sku = row["sku"]
        nama = row["nama"]
        harga = row["harga"]

        # Redis
        stok = redis_client.get(f"stok:{sku}") or "0"

        # Mongo
        metadata = mongo_collection.find_one({"sku": sku}) or {}
        deskripsi = metadata.get("deskripsi", "Tidak ada deskripsi")
        gambar_url = metadata.get("gambar_url", "https://picsum.photos/150")

        produk_list.append({
            "sku": sku,
            "nama": nama,
            "harga": harga,
            "stok": stok,
            "deskripsi": deskripsi,
            "gambar_url": gambar_url,
        })

    return templates.TemplateResponse("produk_list.html", {
        "request": request,
        "produk": produk_list
    })

@router.get("/produk/tambah")
async def tambah_produk_form(request: Request):
    return templates.TemplateResponse("produk_tambah.html", {"request": request})

@router.post("/produk/tambah")
async def tambah_produk(
    request: Request,
    sku: str = Form(...),
    nama: str = Form(...),
    harga: int = Form(...),
    deskripsi: str = Form(...),
    gambar_url: str = Form(...),
    stok: int = Form(...)
):
    # Simpan ke PostgreSQL
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO produk (sku, nama, harga) VALUES ($1, $2, $3)", sku, nama, harga)

    # Simpan ke MongoDB
    mongo_collection.insert_one({
        "sku": sku,
        "deskripsi": deskripsi,
        "gambar_url": gambar_url
    })

    # Simpan ke Redis
    redis_client.set(f"stok:{sku}", stok)

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/produk/{sku}")
async def produk_detail(request: Request, sku: str):
    if db_pool is None:
        return {"error": "DB not initialized"}
    
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT sku, nama, harga FROM produk WHERE sku = $1", sku)
    
    if not row:
        return {"error": "Produk tidak ditemukan"}

    stok = redis_client.get(f"stok:{sku}") or "0"
    metadata = mongo_collection.find_one({"sku": sku}) or {}
    deskripsi = metadata.get("deskripsi", "Tidak ada deskripsi")
    gambar_url = metadata.get("gambar_url", "https://picsum.photos/150")

    return templates.TemplateResponse("produk_detail.html", {
        "request": request,
        "sku": row["sku"],
        "nama": row["nama"],
        "harga": row["harga"],
        "stok": stok,
        "deskripsi": deskripsi,
        "gambar_url": gambar_url
    })


# GET: Form Edit Produk
@router.get("/produk/{sku}/edit")
async def edit_produk_form(request: Request, sku: str):
    if db_pool is None:
        return {"error": "DB not initialized"}

    # PostgreSQL
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT sku, nama, harga FROM produk WHERE sku = $1", sku)

    if not row:
        return {"error": "Produk tidak ditemukan"}

    # Redis
    stok = redis_client.get(f"stok:{sku}") or "0"

    # MongoDB
    metadata = mongo_collection.find_one({"sku": sku}) or {}
    deskripsi = metadata.get("deskripsi", "")
    gambar_url = metadata.get("gambar_url", "")

    return templates.TemplateResponse("produk_edit.html", {
        "request": request,
        "sku": row["sku"],
        "nama": row["nama"],
        "harga": row["harga"],
        "stok": stok,
        "deskripsi": deskripsi,
        "gambar_url": gambar_url
    })

# POST: Update Produk
@router.post("/produk/{sku}/edit")
async def update_produk(
    request: Request,
    sku: str,
    nama: str = Form(...),
    harga: float = Form(...),
    stok: int = Form(...),
    deskripsi: str = Form(""),
    gambar_url: str = Form("")
):
    if db_pool is None:
        return {"error": "DB not initialized"}

    # PostgreSQL update
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE produk SET nama = $1, harga = $2 WHERE sku = $3",
            nama, harga, sku
        )

    # MongoDB update
    mongo_collection.update_one(
        {"sku": sku},
        {"$set": {"deskripsi": deskripsi, "gambar_url": gambar_url}},
        upsert=True
    )

    # Redis update
    redis_client.set(f"stok:{sku}", stok)

    return RedirectResponse(url="/dashboard/produk", status_code=303)

@router.post("/produk/{sku}/delete")
async def delete_produk(request: Request, sku: str):
    if db_pool is None:
        return {"error": "DB not initialized"}

    # Hapus dari PostgreSQL
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM produk WHERE sku = $1", sku)

    # Hapus dari Redis
    redis_client.delete(f"stok:{sku}")

    # Hapus dari MongoDB
    mongo_collection.delete_one({"sku": sku})

    # Redirect ke halaman daftar produk
    return RedirectResponse(url="/produk", status_code=303)
