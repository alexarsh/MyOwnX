"""post-service: posts, replies, likes and post search."""

from fastapi import FastAPI

app = FastAPI(title="post-service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "post-service"}
