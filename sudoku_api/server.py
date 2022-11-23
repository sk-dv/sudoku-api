import os
from aiohttp import web
from strawberry.aiohttp.views import GraphQLView
from graphql_schema import schema


async def app():
    app = web.Application()
    app.router.add_route("*", "/graphql", GraphQLView(schema=schema, graphiql=False))
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app(), port=port)
