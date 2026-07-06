"""timeline-service: stateless read-side aggregation (timeline, search)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import clients
from app.routes import search, timeline


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await clients.client.aclose()


app = FastAPI(title="timeline-service", version="1.0.0", lifespan=lifespan)
app.include_router(timeline.router)
app.include_router(search.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "timeline-service"}
