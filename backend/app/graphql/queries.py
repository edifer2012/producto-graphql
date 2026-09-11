import strawberry
from strawberry.types import Info

from app.graphql.context import GraphQLContext
from app.graphql.types import ProductoPagina, ProductoType


@strawberry.type
class Query:
    @strawberry.field
    async def productos(
        self, info: Info[GraphQLContext, None], limite: int = 20, offset: int = 0
    ) -> ProductoPagina:
        def run(service):
            items, total = service.listar(limite, offset)
            return ProductoPagina(
                items=[ProductoType.from_model(p) for p in items],
                total=total,
                limite=limite,
                offset=offset,
            )

        return await info.context.execute(run)

    @strawberry.field
    async def producto(self, info: Info[GraphQLContext, None], id: int) -> ProductoType | None:
        return await info.context.execute(
            lambda service: ProductoType.from_model(service.obtener_por_id(id))
        )
