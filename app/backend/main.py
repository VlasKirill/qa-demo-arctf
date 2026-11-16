from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os

app = FastAPI(title="Auth Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", truncate_error=True)

def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: str

def get_db():
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_access_token(email: str) -> str:
    """Создает JWT-токен для переданного email"""
    expire = get_utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_utc_now():
    """Помощник для получения текущего времени. Вынесен отдельно для удобного мокирования в тестах."""
    from datetime import datetime
    return datetime.utcnow()

def send_welcome_email(email: str):
    """
    Гипотетическая функция отправки email.
    В реальности здесь был бы вызов SMTP-сервера или внешнего API (например, SendGrid).
    Мы будем мокать именно её, чтобы тесты не пытались реально отправить письмо.
    """
    import time
    time.sleep(2)  # Имитация медленного внешнего запроса (2 секунды)
    print(f"Sending welcome email to {email}...")
    return True

@app.post("/register")
def register(user: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = pwd_context.hash(user.password)
    cursor.execute(
        "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
        (user.email, user.username, password_hash)
    )
    db.commit()

    send_welcome_email(user.email)
    
    return {"message": "User registered successfully", "user_id": cursor.lastrowid}

@app.post("/login")
def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, email, username, password_hash FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    
    if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user["id"],
            "email": db_user["email"],
            "username": db_user["username"]
        }
    }

@app.get("/me")
def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: sqlite3.Connection = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    token = authorization.replace("Bearer ", "", 1).strip()

    email = verify_token(token)

    cursor = db.cursor()
    cursor.execute(
        "SELECT id, email, username, created_at FROM users WHERE email = ?",
        (email,)
    )
    db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": db_user["id"],
        "email": db_user["email"],
        "username": db_user["username"],
        "created_at": db_user["created_at"]
    }
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}