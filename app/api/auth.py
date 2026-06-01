from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import hashlib
import secrets
import time

router = APIRouter()

# Simple in-memory user store (for demo purposes)
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


def extract_token(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization:
        return None
    # Handle both "Bearer <token>" and raw token
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization

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
        "exp": time.time() + 604800
    }
    
    return access_token, refresh_token

@router.post("/login", response_model=TokenResponse)
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

@router.post("/register")
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

@router.post("/refresh")
def refresh(data: dict, authorization: Optional[str] = Header(None)):
    """Refresh access token."""
    # First try to get refresh_token from body
    refresh_token = data.get("refresh_token")
    
    # If no refresh_token in body, try from Authorization header
    if not refresh_token:
        refresh_token = extract_token(authorization)
    
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

@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user info."""
    token = extract_token(authorization)
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_data = TOKENS[token]
    if time.time() > token_data["exp"]:
        del TOKENS[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
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