import os
from aiohttp import web
from strawberry.aiohttp.views import GraphQLView
from graphql_schema import schema


port = int(os.environ.get("PORT", 8080))
graphiql = bool(os.environ.get("GRAPHIQL", True))


async def app():
    app = web.Application()
    app.router.add_route("*", "/graphql", GraphQLView(schema=schema, graphiql=graphiql))
    return app


if __name__ == "__main__":
    web.run_app(app(), port=port)
