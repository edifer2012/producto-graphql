"""Crear la tabla de productos con control de versión."""

import sqlalchemy as sa

from alembic import op

revision = "0001_productos"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("precio", sa.Numeric(12, 2), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("precio > 0", name="ck_productos_precio_positivo"),
        sa.CheckConstraint("length(trim(nombre)) > 0", name="ck_productos_nombre_no_vacio"),
    )


def downgrade():
    op.drop_table("productos")
