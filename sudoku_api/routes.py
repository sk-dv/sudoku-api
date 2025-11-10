from sudoku_api.resources.daily import DailyPuzzleResource
from sudoku_api.resources.stats import StatsResource
from sudoku_api.resources.game import GameResource
from sudoku_api.resources.validate import ValidateResource
from sudoku_api.resources.solve import SolveResource


def register_routes(api, models):
    ns = api.namespace("", description="Sudoku API operations")

    # Decorar recursos con modelos
    GameResource.get = ns.doc(responses={200: ("Success", models["game_response"])})(GameResource.get)
    DailyPuzzleResource.get = ns.doc(responses={200: ("Success", models["game_response"])})(DailyPuzzleResource.get)

    ValidateResource.post = ns.expect(models["grid"])(ValidateResource.post)
    SolveResource.post = ns.expect(models["grid"])(SolveResource.post)

    ns.add_resource(DailyPuzzleResource, "/daily")
    ns.add_resource(StatsResource, "/stats")
    ns.add_resource(GameResource, "/game")
    ns.add_resource(ValidateResource, "/validate")
    ns.add_resource(SolveResource, "/solve")
