import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.db.base import Base
from app.main import create_app


@pytest.fixture
def factory(tmp_path: Path):
    # SQLite en archivo temporal, no memoria compartida entre hilos.
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(factory):
    app = create_app(Settings(graphql_ide=False), session_factory=factory)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def postgres_factory():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Se requiere TEST_DATABASE_URL de una base aislada terminada en _test")
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").endswith("_test"):
        pytest.fail("TEST_DATABASE_URL debe ser PostgreSQL y su base debe terminar en _test")
    engine = create_engine(url)
    # Solo se elimina nuestra tabla en la BD expresamente autorizada de pruebas.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()
