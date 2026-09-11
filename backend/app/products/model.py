from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_productos_precio_positivo"),
        CheckConstraint("length(trim(nombre)) > 0", name="ck_productos_nombre_no_vacio"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    __mapper_args__ = {"version_id_col": version}
