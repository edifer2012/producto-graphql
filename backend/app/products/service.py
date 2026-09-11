from contextlib import contextmanager

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.exceptions import ConflictError, NotFoundError, PersistenceError, ValidationError
from app.products.model import Producto
from app.products.repository import ProductoRepository
from app.products.schemas import ProductoDatos


class ProductoService:
    """Casos de uso reutilizables. No importa FastAPI, Strawberry ni HTTP."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = ProductoRepository(session)

    @contextmanager
    def _operation(self, *, write: bool = False):
        try:
            yield
            if write:
                self._session.commit()
        except StaleDataError as error:
            self._session.rollback()
            raise ConflictError(
                "El producto cambió. Actualiza el listado antes de reintentar."
            ) from error
        except SQLAlchemyError as error:
            self._session.rollback()
            raise PersistenceError() from error
        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _validar(datos: dict) -> ProductoDatos:
        try:
            return ProductoDatos.model_validate(datos)
        except PydanticValidationError as error:
            # No se exponen valores de entrada ni detalles internos al cliente.
            fields = ", ".join(sorted({str(e["loc"][0]) for e in error.errors()}))
            raise ValidationError(f"Revisa los campos: {fields}.") from error

    def _get(self, producto_id: int) -> Producto:
        if producto_id < 1:
            raise ValidationError("El identificador debe ser mayor que cero.")
        producto = self._repository.obtener_por_id(producto_id)
        if producto is None:
            raise NotFoundError("El producto no existe.")
        return producto

    @staticmethod
    def _check_version(producto: Producto, version: int) -> None:
        if version != producto.version:
            raise ConflictError("El producto cambió. Actualiza el listado antes de reintentar.")

    def listar(self, limite: int = 20, offset: int = 0) -> tuple[list[Producto], int]:
        if not 1 <= limite <= 100 or offset < 0:
            raise ValidationError(
                "El límite debe estar entre 1 y 100 y el offset no puede ser negativo."
            )
        with self._operation():
            return self._repository.listar(limite, offset)

    def obtener_por_id(self, producto_id: int) -> Producto:
        with self._operation():
            return self._get(producto_id)

    def crear(self, datos: dict) -> Producto:
        validado = self._validar(datos)
        with self._operation(write=True):
            producto = Producto(**validado.model_dump())
            self._repository.agregar(producto)
        return producto

    def actualizar(self, producto_id: int, version: int, datos: dict) -> Producto:
        validado = self._validar(datos)
        with self._operation(write=True):
            producto = self._get(producto_id)
            self._check_version(producto, version)
            for campo, valor in validado.model_dump().items():
                setattr(producto, campo, valor)
        return producto

    def eliminar(self, producto_id: int, version: int) -> int:
        with self._operation(write=True):
            producto = self._get(producto_id)
            self._check_version(producto, version)
            self._repository.eliminar(producto)
        return producto_id
