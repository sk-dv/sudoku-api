class FastDifficultyCalculator:
    """Calculadora simple y directa de dificultad real"""

    def __init__(self, puzzle_board):
        self.board = puzzle_board
        self.empty_cells = puzzle_board.get_empty_cells()
        self.total_empty = len(self.empty_cells)

    def calculate_improved_coefficient(self):
        """Calcula dificultad basada en factores reales"""
        if self.total_empty == 0:
            return 1.0

        # Factor 1: Celdas vacías (más vacías = más difícil)
        empty_factor = min(10, (self.total_empty / 81) * 15)  # 0-10 scale

        # Factor 2: Distribución de opciones
        options_factor = self._calculate_options_complexity()

        # Factor 3: Distribución espacial
        spatial_factor = self._calculate_spatial_complexity()

        # Combinación simple y directa
        final_score = empty_factor * 0.5 + options_factor * 0.3 + spatial_factor * 0.2

        # Asegurar rango 1-10
        return max(1.0, min(10.0, final_score))

    def _calculate_options_complexity(self):
        """Calcula complejidad basada en opciones disponibles"""
        if not self.empty_cells:
            return 1.0

        option_counts = []
        constrained_cells = 0

        for row, col in self.empty_cells:
            options = len(self.board.get_available_numbers(row, col))
            option_counts.append(options)

            # Celdas muy restringidas (1-2 opciones) son más fáciles
            # Celdas con muchas opciones (6+) son más difíciles
            if options <= 2:
                constrained_cells += 1

        # Promedio de opciones por celda
        avg_options = sum(option_counts) / len(option_counts)

        # Porcentaje de celdas muy restringidas (fáciles)
        easy_ratio = constrained_cells / len(self.empty_cells)

        # Más opciones promedio = más difícil
        # Menos celdas restringidas = más difícil
        options_score = min(10, avg_options * 1.5)
        restriction_score = max(0, 10 - easy_ratio * 8)

        return (options_score + restriction_score) / 2

    def _calculate_spatial_complexity(self):
        """Calcula complejidad basada en distribución espacial"""
        if not self.empty_cells:
            return 1.0

        # Contar vacías por región 3x3
        regions = [0] * 9
        for row, col in self.empty_cells:
            region = (row // 3) * 3 + (col // 3)
            regions[region] += 1

        # Calcular distribución
        non_zero_regions = sum(1 for x in regions if x > 0)
        max_in_region = max(regions) if regions else 0

        # Más regiones con vacías = más complejo
        # Concentración alta en una región = menos complejo
        region_spread = min(10, non_zero_regions * 1.2)
        concentration_penalty = max(0, max_in_region - 6) * 0.5

        return max(1, region_spread - concentration_penalty)
