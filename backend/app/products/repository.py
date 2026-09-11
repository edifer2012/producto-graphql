from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.products.model import Producto


class ProductoRepository:
    """Consultas y cambios ORM; no decide commit ni rollback."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def obtener_por_id(self, producto_id: int) -> Producto | None:
        return self._session.get(Producto, producto_id)

    def listar(self, limite: int, offset: int) -> tuple[list[Producto], int]:
        total = self._session.scalar(select(func.count()).select_from(Producto)) or 0
        items = self._session.scalars(
            select(Producto).order_by(Producto.id).limit(limite).offset(offset)
        ).all()
        return list(items), total

    def agregar(self, producto: Producto) -> None:
        self._session.add(producto)

    def eliminar(self, producto: Producto) -> None:
        self._session.delete(producto)
