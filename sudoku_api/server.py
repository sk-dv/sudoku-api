import os
from aiohttp import web
from strawberry.aiohttp.views import GraphQLView
from graphql_schema import schema
from aiohttp_cors import setup as setup_cors, ResourceOptions


port = int(os.environ.get("PORT", 8080))
graphiql = bool(os.environ.get("GRAPHIQL", True))


async def app():
    app = web.Application()
    app.router.add_route("*", "/graphql", GraphQLView(schema=schema, graphiql=graphiql))
    return app

cors = setup_cors(app, defaults={
    "*": ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*"
    )
})

for route in list(app.router.routes()):
    cors.add(route)


if __name__ == "__main__":
    web.run_app(app(), port=port)
