import ast
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import PersistenceError
from app.products.service import ProductoService


def test_commit_fallido_hace_rollback(factory):
    with factory() as session:
        service = ProductoService(session)
        with patch.object(session, "commit", side_effect=SQLAlchemyError("internal-secret")):
            with pytest.raises(PersistenceError) as error:
                service.crear({"nombre": "Monitor", "precio": "10.00"})
        assert "internal-secret" not in str(error.value)
        items, total = service.listar()
        assert total == 0
        assert items == []


def test_servicio_y_repositorio_no_dependen_del_transporte():
    for file in Path("app/products").glob("*.py"):
        tree = ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("fastapi", "strawberry", "app.graphql"))
            elif isinstance(node, ast.Import):
                assert all(
                    not alias.name.startswith(("fastapi", "strawberry")) for alias in node.names
                )
