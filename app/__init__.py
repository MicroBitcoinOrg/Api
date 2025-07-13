from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, suppress
from .database import sessionmanager
import fastapi.openapi.utils as fu
from .settings import get_settings
from fastapi import FastAPI
from . import errors


def create_app(init_db: bool = True) -> FastAPI:
    settings = get_settings()
    lifespan = None

    # SQLAlchemy initialization process
    if init_db:
        sessionmanager.init(settings.database.endpoint)

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            yield
            with suppress(Exception):
                await sessionmanager.close()

    fu.validation_error_response_definition = (
        errors.ErrorResponse.model_json_schema()
    )

    app = FastAPI(
        title="API Docs",
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "Blocks"},
            {"name": "Transactions"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.backend.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(errors.Abort, errors.abort_handler)
    app.add_exception_handler(
        RequestValidationError,
        errors.validation_handler,
    )

    from .transactions import router as db_router
    from .blocks import router as blocks_router
    from .address import router as address_router

    app.include_router(address_router)
    app.include_router(blocks_router)
    app.include_router(db_router)

    @app.get("/ping")
    async def ping_pong():
        return "pong"

    return app
