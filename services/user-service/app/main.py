"""user-service: accounts, auth, profiles and the follow graph."""

from fastapi import FastAPI

app = FastAPI(title="user-service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "user-service"}
