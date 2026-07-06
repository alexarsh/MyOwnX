"""user-service: accounts, auth, profiles and the follow graph."""

from fastapi import FastAPI

from app.routes import auth, internal, profiles

app = FastAPI(title="user-service", version="1.0.0")
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(internal.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "user-service"}
