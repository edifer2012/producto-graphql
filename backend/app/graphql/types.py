from datetime import datetime
from decimal import Decimal

import strawberry

from app.products.model import Producto


@strawberry.type
class ProductoType:
    id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    version: int
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def from_model(cls, producto: Producto) -> "ProductoType":
        return cls(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio=producto.precio,
            version=producto.version,
            creado_en=producto.creado_en,
            actualizado_en=producto.actualizado_en,
        )


@strawberry.type
class ProductoPagina:
    items: list[ProductoType]
    total: int
    limite: int
    offset: int


@strawberry.input
class ProductoInput:
    nombre: str
    precio: Decimal
    descripcion: str | None = None

    def to_dict(self) -> dict:
        return {"nombre": self.nombre, "precio": self.precio, "descripcion": self.descripcion}


@strawberry.type
class EliminacionResultado:
    id: int
    eliminado: bool
