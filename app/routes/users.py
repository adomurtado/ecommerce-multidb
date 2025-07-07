from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import hashlib
import redis

router = APIRouter()
templates = Jinja2Templates(directory="templates")

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
db_pool = None

def set_db_pool(pool):
    global db_pool
    db_pool = pool

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if db_pool is None:
        return {"error": "DB not initialized"}

    hashed = hash_password(password)

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE username = $1 AND password_hash = $2", username, hashed)

    if user:
        response = RedirectResponse(url="/dashboard", status_code=302)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Username atau password salah"
        })
