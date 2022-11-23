from aiohttp import web
from strawberry.aiohttp.views import GraphQLView
from graphql_schema import schema

app = web.Application()

app.router.add_route("*", "/graphql", GraphQLView(schema=schema))

if __name__ == '__main__':
    web.run_app(app)