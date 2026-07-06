"""post-service: posts, replies, likes and post search."""

from fastapi import FastAPI

from app.routes import internal, likes, posts

app = FastAPI(title="post-service", version="1.0.0")
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(internal.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "post-service"}
