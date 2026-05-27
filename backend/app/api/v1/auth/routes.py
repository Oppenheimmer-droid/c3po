from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/login")
async def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    # Ejemplo simple (reemplazar por tu lógica real)
    if email == "test@test.com" and password == "123456":
        return JSONResponse({"message": "Login OK"})

    return JSONResponse({"error": "Invalid credentials"}, status_code=401)
