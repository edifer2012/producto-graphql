import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import create_session_factory
from app.graphql.schema import create_graphql_router


def create_app(settings: Settings | None = None, session_factory=None) -> FastAPI:
    config = settings or get_settings()
    configure_logging(config.log_level)
    factory = session_factory or create_session_factory(config)

    @asynccontextmanager
    async def lifespan(app):
        yield
        # Solo se dispone el motor creado por la propia aplicación.
        if session_factory is None:
            factory.kw["bind"].dispose()

    app = FastAPI(title="Productos GraphQL", version="0.1.0", lifespan=lifespan)
    app.state.session_factory = factory

    @app.middleware("http")
    async def request_metadata(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        logging.getLogger("producto.http").info(
            "request_complete",
            extra={
                "request_id": request.state.request_id,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )
        return response

    @app.get("/health/live", tags=["Operación"])
    def live():
        return {"status": "alive"}

    @app.get("/health/ready", tags=["Operación"])
    async def ready():
        def check():
            with factory() as session:
                session.execute(text("SELECT 1"))

        try:
            await run_in_threadpool(check)
            return {"status": "ready"}
        except Exception:
            return JSONResponse(status_code=503, content={"status": "not_ready"})

    app.include_router(create_graphql_router(config.graphql_ide), prefix="/graphql")
    return app


app = create_app()
