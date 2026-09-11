from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings


def create_session_factory(settings: Settings):
    engine = create_engine(settings.db_url(), pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
