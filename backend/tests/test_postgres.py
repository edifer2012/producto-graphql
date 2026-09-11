from decimal import Decimal

import pytest
from sqlalchemy.orm.exc import StaleDataError

from app.products.model import Producto
from app.products.service import ProductoService

pytestmark = pytest.mark.postgres


def test_precision_y_persistencia(postgres_factory):
    with postgres_factory() as session:
        product_id = ProductoService(session).crear({"nombre": "Prueba", "precio": "0.01"}).id
    with postgres_factory() as session:
        assert ProductoService(session).obtener_por_id(product_id).precio == Decimal("0.01")


def test_bloqueo_optimista_real(postgres_factory):
    with postgres_factory() as session:
        product_id = ProductoService(session).crear({"nombre": "Prueba", "precio": "2.00"}).id
    with postgres_factory() as first, postgres_factory() as second:
        a = first.get(Producto, product_id)
        b = second.get(Producto, product_id)
        a.nombre = "Primero"
        first.commit()
        b.nombre = "Segundo"
        with pytest.raises(StaleDataError):
            second.commit()
        second.rollback()
