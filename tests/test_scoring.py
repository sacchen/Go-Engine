# python -m unittest discover tests
# python -m unittest tests.test_scoring

import unittest
from src.board import Board, Stone
from typing import List


class TestBoardScoring(unittest.TestCase):
    """
    Test suite for the board's scoring logic.
    These tests use board layouts that are sealed to prevent "leaky" territories.
    """

    def setUp(self):
        """Set up a new 5x5 board for each test."""
        self.board = Board(size=5)

    def setup_board_from_string(self, layout: List[str]):
        """
        Helper function to set up a board from a list of strings.
        'B' = Black, 'W' = White, '.' = Empty. Spaces are ignored.
        """
        for r, row_str in enumerate(layout):
            row_content = row_str.replace(" ", "")
            for c, char in enumerate(row_content):
                if char == "B":
                    self.board.grid[r][c] = Stone.BLACK
                elif char == "W":
                    self.board.grid[r][c] = Stone.WHITE

    def test_simple_territory(self):
        """Test a simple, fully enclosed 2x2 territory for Black."""
        layout = [
            "B B B . .",
            "B . . B .",
            "B . . B .",
            "B B B B .",
            ". . . . .",
        ]
        self.setup_board_from_string(layout)
        territory = self.board.calculate_scores()

        # Black should have a 2x2 = 4 point territory.
        # White has no sealed territory.
        self.assertEqual(
            territory["black_territory"], 4, "Black should have a 2x2 territory"
        )
        self.assertEqual(
            territory["white_territory"], 0, "White should have no territory"
        )

    def test_edge_territory(self):
        """Test territory that is enclosed against the edge of the board."""
        layout = [
            "W W W . .",
            "W . W . .",
            "W W W . .",
            "B B B B B",
            ". . . . .",
        ]
        self.setup_board_from_string(layout)
        territory = self.board.calculate_scores()

        # White has sealed one point (1,1) using the edge as a wall.
        self.assertEqual(territory["white_territory"], 1)
        self.assertEqual(territory["black_territory"], 0)

    def test_complex_territory_with_dame(self):
        """A more complex board with mixed territory and dame (neutral) points."""
        # MODIFIED LAYOUT: Column 2 is now filled, sealing the territories.
        # This leaves a 3-point black territory and a 4-point white territory.
        layout = [
            "B B B W W",
            "B . B . W",
            "B . B . W",
            "B . B . W",
            "B B B W W",
        ]
        self.setup_board_from_string(layout)
        territory = self.board.calculate_scores()

        # Now the assertion should pass
        self.assertEqual(territory["black_territory"], 3)
        self.assertEqual(territory["white_territory"], 4)

    def test_final_score_calculation_chinese_rules(self):
        """Test the final score using Chinese rules (Territory + Stones)."""
        layout = [
            # B Territory: (1,1) = 1 point
            # B Stones: 8
            # B Total: 9
            "B B B . .",
            "B . B W W",
            "B B B W .",
            # W Territory: (3,4) = 1 point
            # W Stones: 5
            # W Total: 1 + 5 + 6.5 komi = 12.5
            ". . . W W",
            ". . . W .",
        ]
        self.setup_board_from_string(layout)
        scores = self.board.get_final_scores(komi=6.5)

        self.assertEqual(scores["black"], 9)
        self.assertEqual(scores["white"], 12.5)


if __name__ == "__main__":
    unittest.main()
