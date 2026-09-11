import strawberry
from strawberry.types import Info

from app.graphql.context import GraphQLContext
from app.graphql.types import EliminacionResultado, ProductoInput, ProductoType


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def crear_producto(
        self, info: Info[GraphQLContext, None], datos: ProductoInput
    ) -> ProductoType | None:
        return await info.context.execute(
            lambda service: ProductoType.from_model(service.crear(datos.to_dict()))
        )

    @strawberry.mutation
    async def actualizar_producto(
        self, info: Info[GraphQLContext, None], id: int, version: int, datos: ProductoInput
    ) -> ProductoType | None:
        return await info.context.execute(
            lambda service: ProductoType.from_model(
                service.actualizar(id, version, datos.to_dict())
            )
        )

    @strawberry.mutation
    async def eliminar_producto(
        self, info: Info[GraphQLContext, None], id: int, version: int
    ) -> EliminacionResultado | None:
        return await info.context.execute(
            lambda service: EliminacionResultado(id=service.eliminar(id, version), eliminado=True)
        )
