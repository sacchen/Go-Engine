import unittest
from src.board import Board, Stone


class TestBoardCapturing(unittest.TestCase):

    def setUp(self):
        self.b = Board(size=5)

    def play(self, color: Stone, row: int, col: int):
        """Place a stone of the given color, regardless of whose turn it “really” is."""
        self.b.current_turn = color
        self.b.place_stone(row, col)

    def verify_board(self, expected_layout):
        """Verify the board matches the expected layout.

        Args:
            expected_layout: List of strings where:
                '.' = empty, 'B' = black, 'W' = white
        """
        for r, row in enumerate(expected_layout):
            for c, cell in enumerate(row.replace(" ", "")):
                expected = {".": Stone.EMPTY, "B": Stone.BLACK, "W": Stone.WHITE}[cell]
                self.assertEqual(self.b.grid[r][c], expected, f"Mismatch at {r},{c}")

    def setup_capture_scenario(self, center=(2, 2), color=Stone.WHITE):
        """Setup a standard capture scenario with one stone surrounded on 4 sides.
        Returns the coordinates of the surrounded stone and surrounding stones.
        """
        r, c = center
        surrounded = [(r, c)]
        surrounding = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]

        # Place the surrounded stone
        self.play(color, r, c)

        return surrounded, surrounding

    def test_simple_capture(self):
        """Test capturing a single stone.
        Initial setup:   After capture:
        . . . . .       . . . . .
        . . B . .       . . B . .
        . B W B .  -->  . B . B .
        . . B . .       . . B . .
        . . . . .       . . . . .
        """
        # White goes in center, then Black surrounds on all four sides
        self.play(Stone.WHITE, 2, 2)
        for r, c in [(1, 2), (2, 1), (2, 3), (3, 2)]:
            self.play(Stone.BLACK, r, c)
        # after the last black play, the white at (2,2) must be gone
        self.assertEqual(self.b.grid[2][2], Stone.EMPTY)

    def test_multi_group_setup(self):
        """Verify the multi-group setup has the expected properties.

        Board layout before final move:
        . B . . .
        B W B . .
        . . . . .
        B W B . .
        . B . . .

        Both white stones share only one liberty at (2,2).
        """
        whites = [(1, 2), (3, 2)]
        # 1) Place the two white stones
        for r, c in whites:
            self.play(Stone.WHITE, r, c)

        # 2) Fill *all* non‐shared liberties
        surround = [
            (0, 2),
            (1, 1),
            (1, 3),  # liberties of (1,2) except (2,2)
            (3, 1),
            (3, 3),
            (4, 2),  # liberties of (3,2) except (2,2)
        ]
        for r, c in surround:
            self.play(Stone.BLACK, r, c)

        # Verify both white groups have exactly one liberty at (2,2)
        for pos in whites:
            with self.subTest(white_stone=pos):
                _, libs = self.b.get_group_and_liberties(*pos)
                self.assertEqual(libs, {(2, 2)}, f"{pos} should only have (2,2) left")

    def test_multi_group_capture(self):
        """Test capturing multiple separate groups with a single move.

        Board layout before final move:    After capture:
        . B . . .                         . B . . .
        B W B . .                         B . B . .
        . . . . .           -->           . B . . .
        B W B . .                         B . B . .
        . B . . .                         . B . . .
        """
        # Setup the same scenario as in test_multi_group_setup
        whites = [(1, 2), (3, 2)]
        for r, c in whites:
            self.play(Stone.WHITE, r, c)

        surround = [
            (0, 2),
            (1, 1),
            (1, 3),
            (3, 1),
            (3, 3),
            (4, 2),
        ]
        for r, c in surround:
            self.play(Stone.BLACK, r, c)

        # 3) Now play on (2,2) to remove that last liberty for *both* groups
        self.play(Stone.BLACK, 2, 2)

        # 4) Assert both were captured
        for r, c in whites:
            with self.subTest(white_stone=(r, c)):
                self.assertEqual(
                    self.b.grid[r][c],
                    Stone.EMPTY,
                    f"Stone at {r},{c} should be captured",
                )

    def test_suicide_not_allowed(self):
        # Black surrounds (2,2)
        for r, c in [(1, 2), (2, 1), (2, 3), (3, 2)]:
            self.play(Stone.BLACK, r, c)

        # Now White tries suicide at (2,2)
        with self.assertRaises(ValueError) as cm:
            self.play(Stone.WHITE, 2, 2)
        self.assertIn("suicide", str(cm.exception))

    def test_capture_on_edge(self):
        # White on the top edge at (0,1)
        self.play(Stone.WHITE, 0, 1)
        # Black occupies its three edge‐liberties
        for r, c in [(0, 0), (0, 2), (1, 1)]:
            self.play(Stone.BLACK, r, c)
        # once all liberties are gone, white must be removed
        self.assertEqual(self.b.grid[0][1], Stone.EMPTY)

    def test_no_false_capture(self):
        # Surround white on only three sides
        self.play(Stone.WHITE, 2, 2)
        for r, c in [(1, 2), (2, 1), (3, 2)]:
            self.play(Stone.BLACK, r, c)
        # one liberty remains at (2,3)
        self.assertEqual(self.b.grid[2][2], Stone.WHITE)

    def test_edge_captures(self):
        """Test captures on different board edges and corners."""
        # Test cases with: (surrounded_pos, surrounding_positions)
        edge_cases = [
            # Edge cases
            ((0, 1), [(0, 0), (0, 2), (1, 1)]),
            ((4, 2), [(4, 1), (4, 3), (3, 2)]),
            ((2, 0), [(1, 0), (3, 0), (2, 1)]),
            # Corner case
            ((0, 0), [(0, 1), (1, 0)]),
        ]

        for surrounded, surrounding in edge_cases:
            # Create a fresh board
            self.setUp()

            # Place the white stone to be captured
            self.play(Stone.WHITE, *surrounded)

            # Surround it with black
            for pos in surrounding:
                self.play(Stone.BLACK, *pos)

            # Verify capture
            self.assertEqual(self.b.grid[surrounded[0]][surrounded[1]], Stone.EMPTY)

    # …and so on for turn‐history, pass, undo, etc.


if __name__ == "__main__":
    unittest.main()
