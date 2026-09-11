import logging
from collections.abc import Callable
from typing import TypeVar

from fastapi import Request
from graphql import GraphQLError
from sqlalchemy.orm import sessionmaker
from starlette.concurrency import run_in_threadpool
from strawberry.fastapi import BaseContext

from app.core.exceptions import AppError
from app.products.service import ProductoService

T = TypeVar("T")
logger = logging.getLogger("producto.graphql")


class GraphQLContext(BaseContext):
    def __init__(self, factory: sessionmaker, request_id: str) -> None:
        super().__init__()
        self.factory = factory
        self.request_id = request_id

    async def execute(self, operation: Callable[[ProductoService], T]) -> T:
        def worker() -> T:
            # Cada resolver tiene su sesión. No se comparte una Session entre hilos.
            # La conversión a tipos de salida ocurre antes de cerrar la sesión.
            with self.factory() as session:
                return operation(ProductoService(session))

        try:
            return await run_in_threadpool(worker)
        except AppError as error:
            logger.warning(
                error.code,
                extra={"request_id": self.request_id, "error_type": type(error).__name__},
            )
            raise GraphQLError(
                str(error), extensions={"code": error.code, "requestId": self.request_id}
            ) from None
        except Exception as error:
            logger.error(
                "unexpected_error",
                extra={"request_id": self.request_id, "error_type": type(error).__name__},
            )
            raise GraphQLError(
                "Error interno. Intenta nuevamente.",
                extensions={"code": "INTERNAL_ERROR", "requestId": self.request_id},
            ) from None


async def get_context(request: Request) -> GraphQLContext:
    return GraphQLContext(request.app.state.session_factory, request.state.request_id)
