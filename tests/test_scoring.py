# python -m unittest discover

import unittest
from src.board import Board, Stone


class TestBoardScoring(unittest.TestCase):
    def setUp(self):
        """Create a new 5x5 board for each test."""
        self.b = Board(size=5)

    def setup_board(self, layout):
        """
        Set the board state directly from a layout string.
        This is useful for testing scoring on specific end-game positions
        without having to play all the moves to get there.

        Args:
            layout: List of strings where:
                '.' = empty, 'B' = black, 'W' = white, spaces are ignored.
        """
        stone_map = {".": Stone.EMPTY, "B": Stone.BLACK, "W": Stone.WHITE}
        for r, row_str in enumerate(layout):
            row_content = row_str.replace(" ", "")
            for c, char in enumerate(row_content):
                self.b.grid[r][c] = stone_map[char]

    def test_empty_board_scoring(self):
        """On an empty board, there is no territory and no stones."""
        layout = [
            ".....",
            ".....",
            ".....",
            ".....",
            ".....",
        ]
        self.setup_board(layout)

        # Test territory calculation
        territory = self.b.calculate_scores()
        self.assertEqual(territory["black_territory"], 0)
        self.assertEqual(territory["white_territory"], 0)

        # Test final score (with default komi 6.5)
        scores = self.b.get_final_scores()
        self.assertEqual(scores["black"], 0)
        self.assertEqual(scores["white"], 6.5)

    def test_simple_territory(self):
        """Test a simple, fully enclosed 2x2 territory for each player."""
        layout = [
            "BB...",
            "B..B.",
            "B..B.",
            ".WW.W",
            ".W..W",
        ]
        self.setup_board(layout)

        territory = self.b.calculate_scores()
        self.assertEqual(
            territory["black_territory"], 4, "Black should have a 2x2 territory"
        )
        self.assertEqual(
            territory["white_territory"], 2, "White should have a 1x2 territory"
        )

    def test_edge_territory(self):
        """Test territory that is enclosed against the edge of the board."""
        layout = [
            "BB...",
            "B.B..",
            "BB...",
            ".....",
            ".....",
        ]
        self.setup_board(layout)
        territory = self.b.calculate_scores()
        self.assertEqual(territory["black_territory"], 1)
        self.assertEqual(territory["white_territory"], 0)

    def test_dame_points_are_not_territory(self):
        """Test that neutral points (dame) are not counted as territory."""
        layout = [
            "BB.WW",
            "BB.WW",
            "BB.WW",
            "BB.WW",
            "BB.WW",
        ]
        self.setup_board(layout)
        territory = self.b.calculate_scores()
        # The middle column is dame (bordered by both B and W), so no territory
        self.assertEqual(territory["black_territory"], 0)
        self.assertEqual(territory["white_territory"], 0)

    def test_complex_territory_with_dame(self):
        """A more complex board with mixed territory and dame points."""
        layout = [
            "W W W W W",
            "W . . . W",
            "W . B . W",
            "W B B B W",
            "W . . . W",
        ]
        self.setup_board(layout)
        territory = self.b.calculate_scores()
        # White has 2 points at (1,1) and (1,2)
        # Black has 1 point at (2,2)
        # All other empty points are dame
        self.assertEqual(territory["white_territory"], 8)
        self.assertEqual(territory["black_territory"], 1)

    def test_final_score_calculation_chinese_rules(self):
        """
        Test the final score using Chinese rules (Territory + Stones).
        Board:
        B B . . .   Black: 4 stones + 2 territory = 6
        B B . . .
        . . . . .
        . . W W .   White: 4 stones + 2 territory = 6
        . . W W .
        """
        layout = [
            "BB...",
            "BB...",
            ".....",
            "..WW.",
            "..WW.",
        ]
        self.setup_board(layout)

        # Test territory first
        territory = self.b.calculate_scores()
        self.assertEqual(territory["black_territory"], 2)
        self.assertEqual(territory["white_territory"], 2)

        # Test final score with default komi
        scores = self.b.get_final_scores()  # komi=6.5
        self.assertEqual(scores["black"], 4 + 2)  # 4 stones + 2 territory
        self.assertEqual(scores["white"], 4 + 2 + 6.5)  # 4 stones + 2 territory + komi

    def test_final_score_with_custom_komi(self):
        """Ensure custom komi value is applied correctly."""
        layout = [
            "B....",
            ".....",
            ".....",
            ".....",
            "....W",
        ]
        self.setup_board(layout)
        scores = self.b.get_final_scores(komi=0.5)

        # Black: 1 stone + 0 territory = 1
        # White: 1 stone + 0 territory + 0.5 komi = 1.5
        self.assertEqual(scores["black"], 1)
        self.assertEqual(scores["white"], 1.5)


if __name__ == "__main__":
    unittest.main()
