from fastapi import FastAPI

app = FastAPI(title="C3PO Backend")

@app.get("/")
def root():
    return {"status": "ok", "service": "C3PO Backend"}
