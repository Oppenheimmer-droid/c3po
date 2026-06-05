# Minimal test app for Railway deployment
from fastapi import FastAPI

app = FastAPI(title="C3PO Minimal")

@app.get("/")
def root():
    return {"status": "ok", "message": "C3PO minimal backend"}

@app.get("/health")
def health():
    return {"status": "ok"}
