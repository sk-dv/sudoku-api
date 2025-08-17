import unittest
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


class TestSudokuAPI(unittest.TestCase):

    def setUp(self):
        """Configurar cliente de testing"""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        """Test del endpoint de health check"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "sudoku-api")

    def test_generate_game_default(self):
        """Test generar juego con parámetros por defecto"""
        response = self.client.get("/api/game")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("data", data)

        game_data = data["data"]
        self.assertIn("playable", game_data)
        self.assertIn("solution", game_data)
        self.assertIn("difficulty", game_data)

        # Verificar estructura del tablero
        playable = game_data["playable"]
        self.assertEqual(len(playable["grid"]), 9)
        self.assertEqual(len(playable["grid"][0]), 9)
        self.assertIsInstance(playable["is_valid"], bool)

        # Verificar que el juego tenga celdas vacías
        empty_cells = sum(1 for row in playable["grid"] for cell in row if cell == 0)
        self.assertGreater(empty_cells, 0)

    def test_generate_game_custom_iterations(self):
        """Test generar juego con iteraciones personalizadas"""
        response = self.client.get("/api/game?iterations=50")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["data"]["metadata"]["iterations_used"], 50)

    def test_generate_game_invalid_iterations(self):
        """Test con iteraciones inválidas"""
        # Muy bajo
        response = self.client.get("/api/game?iterations=5")
        self.assertEqual(response.status_code, 400)

        # Muy alto
        response = self.client.get("/api/game?iterations=300")
        self.assertEqual(response.status_code, 400)

    def test_validate_valid_board(self):
        """Test validar un tablero válido"""
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
        self.assertTrue(data["success"])
        self.assertTrue(data["data"]["is_valid"])

    def test_validate_invalid_board(self):
        """Test validar un tablero inválido"""
        invalid_board = [
            [6, 2, 4, 5, 6, 9, 1, 8, 7],  # 6 repetido en la fila
            [5, 1, 9, 7, 2, 8, 6, 3, 4],
            [8, 3, 7, 6, 1, 4, 2, 9, 5],
            [1, 4, 3, 8, 6, 5, 7, 2, 9],
            [9, 5, 8, 2, 9, 7, 3, 6, 1],  # 9 repetido en la fila
            [7, 6, 2, 3, 9, 1, 4, 5, 8],
            [3, 7, 1, 9, 5, 6, 8, 4, 2],
            [4, 9, 6, 1, 4, 2, 5, 7, 3],  # 4 repetido en la fila
            [2, 8, 5, 4, 7, 3, 9, 1, 6],
        ]

        response = self.client.post(
            "/api/validate",
            data=json.dumps({"grid": invalid_board}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertFalse(data["data"]["is_valid"])

    def test_validate_missing_grid(self):
        """Test validar sin enviar grid"""
        response = self.client.post(
            "/api/validate", data=json.dumps({}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_validate_invalid_format(self):
        """Test validar con formato inválido"""
        invalid_format = {"grid": [[1, 2, 3]]}  # Grid muy pequeño

        response = self.client.post(
            "/api/validate",
            data=json.dumps(invalid_format),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_solve_board(self):
        """Test resolver un tablero parcial"""
        partial_board = [
            [6, 2, 4, 5, 3, 9, 1, 8, 7],
            [5, 1, 9, 7, 2, 8, 6, 3, 4],
            [8, 3, 7, 6, 1, 4, 2, 9, 5],
            [1, 4, 3, 8, 6, 5, 7, 2, 9],
            [9, 5, 8, 2, 4, 7, 3, 6, 1],
            [7, 6, 2, 3, 9, 1, 4, 5, 8],
            [3, 7, 1, 9, 5, 6, 8, 4, 2],
            [4, 9, 6, 1, 8, 2, 5, 7, 3],
            [2, 8, 5, 4, 7, 3, 9, 1, 0],  # Una celda vacía
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

    def test_404_endpoint(self):
        """Test endpoint inexistente"""
        response = self.client.get("/api/nonexistent")
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertIn("available_endpoints", data)

    def test_405_method_not_allowed(self):
        """Test método no permitido"""
        response = self.client.post("/api/game")  # POST en endpoint GET
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
