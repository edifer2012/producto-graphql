from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductoDatos(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=2000)
    precio: Decimal = Field(gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
