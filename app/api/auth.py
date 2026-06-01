from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import hashlib
import secrets
import time

router = APIRouter()

# Simple in-memory user store (for demo purposes)
# In production, use a proper database
USERS_DB = {
    "admin@redrive.edu": {
        "id": "user-admin-001",
        "email": "admin@redrive.edu",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "tenant_id": "tenant-main",
    },
    "teacher@redrive.edu": {
        "id": "user-teacher-001",
        "email": "teacher@redrive.edu",
        "password_hash": hashlib.sha256("teacher123".encode()).hexdigest(),
        "first_name": "Teacher",
        "last_name": "Demo",
        "role": "teacher",
        "tenant_id": "tenant-main",
    },
    "student@redrive.edu": {
        "id": "user-student-001",
        "email": "student@redrive.edu",
        "password_hash": hashlib.sha256("student123".encode()).hexdigest(),
        "first_name": "Student",
        "last_name": "Demo",
        "role": "student",
        "tenant_id": "tenant-main",
    },
}

# Token store
TOKENS = {}

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    tenant_name: str = "Default"
    tenant_slug: str = "default"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

def create_tokens(user_id: str):
    """Create access and refresh tokens."""
    access_token = f"at_{secrets.token_hex(16)}_{user_id}"
    refresh_token = f"rt_{secrets.token_hex(32)}"
    
    TOKENS[access_token] = {
        "user_id": user_id,
        "type": "access",
        "exp": time.time() + 3600
    }
    TOKENS[refresh_token] = {
        "user_id": user_id,
        "type": "refresh",
        "exp": time.time() + 604800  # 7 days
    }
    
    return access_token, refresh_token

@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """Login user and return tokens."""
    user = USERS_DB.get(data.email.lower())
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    password_hash = hashlib.sha256(data.password.encode()).hexdigest()
    if user["password_hash"] != password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token, refresh_token = create_tokens(user["id"])
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )

@router.post("/auth/register")
def register(data: RegisterRequest):
    """Register a new user."""
    if data.email.lower() in USERS_DB:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{secrets.token_hex(8)}"
    tenant_id = f"tenant_{secrets.token_hex(8)}"
    
    USERS_DB[data.email.lower()] = {
        "id": user_id,
        "email": data.email.lower(),
        "password_hash": hashlib.sha256(data.password.encode()).hexdigest(),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "role": "student",
        "tenant_id": tenant_id,
    }
    
    return {
        "id": user_id,
        "email": data.email.lower(),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "tenant_id": tenant_id,
    }

@router.post("/auth/refresh")
def refresh(data: dict):
    """Refresh access token."""
    refresh_token = data.get("refresh_token")
    
    if not refresh_token or refresh_token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_data = TOKENS[refresh_token]
    if token_data["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    if time.time() > token_data["exp"]:
        del TOKENS[refresh_token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    user_id = token_data["user_id"]
    access_token, new_refresh_token = create_tokens(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.get("/auth/me")
def get_current_user(authorization: Optional[str] = None):
    """Get current user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    token = authorization.replace("Bearer ", "")
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_data = TOKENS[token]
    if time.time() > token_data["exp"]:
        del TOKENS[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    # Find user by id
    for user in USERS_DB.values():
        if user["id"] == token_data["user_id"]:
            return {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "role": user["role"],
            }
    
    raise HTTPException(status_code=404, detail="User not found")