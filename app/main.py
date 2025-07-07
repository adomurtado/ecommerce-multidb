from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import asyncpg
import os

from routes import produk, users, checkout
from routes.produk import set_db_pool as set_db_pool_produk
from routes.checkout import set_db_pool as set_db_pool_checkout
from routes.users import set_db_pool as set_db_pool_users

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register routers
app.include_router(produk.router)
app.include_router(users.router)
app.include_router(checkout.router)

@app.on_event("startup")
async def startup():
    pool = await asyncpg.create_pool(
        user="postgres",
        password="postgres",
        database="postgres",
        host="citus_master",
        port=5432
    )

    # Inject pool ke modul
    set_db_pool_produk(pool)
    set_db_pool_checkout(pool)
    set_db_pool_users(pool)

    app.state.db_pool = pool

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()
