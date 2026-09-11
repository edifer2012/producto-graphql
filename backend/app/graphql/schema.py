import logging

import strawberry
from strawberry.extensions import MaxAliasesLimiter, MaxTokensLimiter, QueryDepthLimiter
from strawberry.fastapi import GraphQLRouter

from app.graphql.context import get_context
from app.graphql.mutations import Mutation
from app.graphql.queries import Query


class SafeSchema(strawberry.Schema):
    def process_errors(self, errors, execution_context=None):
        # Evita registrar documentos, variables y stack traces que incluyan datos.
        logging.getLogger("producto.graphql").warning("graphql_operation_errors")


schema = SafeSchema(
    query=Query,
    mutation=Mutation,
    extensions=[
        lambda: QueryDepthLimiter(max_depth=6),
        lambda: MaxTokensLimiter(max_token_count=1000),
        lambda: MaxAliasesLimiter(max_alias_count=10),
    ],
)


def create_graphql_router(ide: bool) -> GraphQLRouter:
    return GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql" if ide else None,
        allow_queries_via_get=False,
    )
