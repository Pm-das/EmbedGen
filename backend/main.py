from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api.routes import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("embedgen.api")

app = FastAPI(
    title="EmbedGen API",
    version="0.1.0",
    description="AI-assisted embedded firmware generation service.",
)

app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())[:8]
    start = time.perf_counter()
    logger.info(
        "request_start id=%s method=%s path=%s", request_id, request.method, request.url.path
    )

    try:
        response = await call_next(request)
    except Exception:  # pragma: no cover - safety net
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception("request_error id=%s elapsed_ms=%.2f", request_id, elapsed_ms)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error", "request_id": request_id}
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_end id=%s method=%s path=%s status=%s elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
