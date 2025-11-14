import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


class TestSudokuAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")

    def test_generate_game(self):
        response = self.client.get("/api/game")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

        game_data = data["data"]
        playable = game_data["playable"]
        self.assertEqual(len(playable["grid"]), 9)
        self.assertEqual(len(playable["grid"][0]), 9)

        empty_cells = sum(1 for row in playable["grid"] for cell in row if cell == 0)
        self.assertGreater(empty_cells, 0)

    def test_validate_board(self):
        valid_board = [
            [6, 2, 4, 5, 3, 9, 1, 8, 7],
            [5, 1, 9, 7, 2, 8, 6, 3, 4],
            [8, 3, 7, 6, 1, 4, 2, 9, 5],
            [1, 4, 3, 8, 6, 5, 7, 2, 9],
            [9, 5, 8, 2, 4, 7, 3, 6, 1],
            [7, 6, 2, 3, 9, 1, 4, 5, 8],
            [3, 7, 1, 9, 5, 6, 8, 4, 2],
            [4, 9, 6, 1, 8, 2, 5, 7, 3],
            [2, 8, 5, 4, 7, 3, 9, 1, 6],
        ]

        response = self.client.post(
            "/api/validate",
            data=json.dumps({"grid": valid_board}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["data"]["is_valid"])

        invalid_board = valid_board.copy()
        invalid_board[0] = [6, 2, 4, 5, 6, 9, 1, 8, 7]

        response = self.client.post(
            "/api/validate",
            data=json.dumps({"grid": invalid_board}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["data"]["is_valid"])

    def test_solve_board(self):
        partial_board = [
            [6, 2, 4, 5, 3, 9, 1, 8, 7],
            [5, 1, 9, 7, 2, 8, 6, 3, 4],
            [8, 3, 7, 6, 1, 4, 2, 9, 5],
            [1, 4, 3, 8, 6, 5, 7, 2, 9],
            [9, 5, 8, 2, 4, 7, 3, 6, 1],
            [7, 6, 2, 3, 9, 1, 4, 5, 8],
            [3, 7, 1, 9, 5, 6, 8, 4, 2],
            [4, 9, 6, 1, 8, 2, 5, 7, 3],
            [2, 8, 5, 4, 7, 3, 9, 1, 0],
        ]

        response = self.client.post(
            "/api/solve",
            data=json.dumps({"grid": partial_board}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("solved_grid", data["data"])


if __name__ == "__main__":
    unittest.main()
