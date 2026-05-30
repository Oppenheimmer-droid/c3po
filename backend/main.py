from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.api.v1.router import api_router

import threading, time, requests

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.head("/")
def root_head():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/keepalive")
def keepalive():
    return {"status": "alive"}

def keep_alive_loop():
    while True:
        try:
            requests.get("http://0.0.0.0:8000/keepalive", timeout=2)
        except:
            pass
        time.sleep(20)

threading.Thread(target=keep_alive_loop, daemon=True).start()

# ⭐⭐ ESTA ES LA LÍNEA CRÍTICA QUE FALTABA ⭐⭐
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

