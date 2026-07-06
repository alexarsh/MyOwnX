"""timeline-service: stateless read-side aggregation (timeline, search)."""

from fastapi import FastAPI

app = FastAPI(title="timeline-service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "timeline-service"}
