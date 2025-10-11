import unittest
from src.board import Board, Stone


class TestBoardCapturing(unittest.TestCase):
    def setUp(self):
        self.b = Board(size=5)

    def play(self, color: Stone, row: int, col: int):
        """Place a stone of the given color, regardless of whose turn it "really" is."""
        self.b.current_turn = color
        self.b.place_stone(row, col)

    def verify_board(self, expected_layout):
        """Verify the board matches the expected layout.

        Args:
            expected_layout: List of strings where:
                '.' = empty, 'B' = black, 'W' = white, spaces are ignored
        """
        for r, row in enumerate(expected_layout):
            row_content = row.replace(" ", "")
            for c, cell in enumerate(row_content):
                expected = {".": Stone.EMPTY, "B": Stone.BLACK, "W": Stone.WHITE}[cell]
                actual = self.b.grid[r][c]
                self.assertEqual(
                    actual,
                    expected,
                    f"Mismatch at {r},{c}: expected {expected}, got {actual}",
                )

    def test_simple_capture_with_verify(self):
        """Test capturing a single stone with board verification.

        Initial setup:   After capture:
        . . . . .       . . . . .
        . . B . .       . . B . .
        . B W B .  -->  . B . B .
        . . B . .       . . B . .
        . . . . .       . . . . .
        """
        # Place the white stone to be captured
        self.play(Stone.WHITE, 2, 2)

        # Verify initial setup
        setup = [
            ".....",
            ".....",
            "..W..",
            ".....",
            ".....",
        ]
        self.verify_board(setup)

        # Place black stones around white
        for r, c in [(1, 2), (2, 1), (2, 3), (3, 2)]:
            self.play(Stone.BLACK, r, c)

        # Verify final state after capture
        expected = [
            ".....",
            "..B..",
            ".B.B.",
            "..B..",
            ".....",
        ]
        self.verify_board(expected)

    def test_multi_group_setup(self):
        """Verify the multi-group setup has the expected properties.

        Board layout before final move:
        . . B . .
        . B W B .
        . . . . .
        . B W B .
        . . B . .

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

        # Verify board state
        expected = [
            "..B..",
            ".BWB.",
            ".....",
            ".BWB.",
            "..B..",
        ]
        self.verify_board(expected)

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

        # 4) Assert both were captured using the verify_board method
        expected = [
            "..B..",
            ".B.B.",
            "..B..",
            ".B.B.",
            "..B..",
        ]
        self.verify_board(expected)

    def test_multi_stone_group_capture(self):
        """Test capturing a chain of connected stones.

        Initial setup:           After capture:
        . . . . .                . . . . .
        . B B B .                . B B B .
        . B W W B       -->      . B . . B
        . B W B .                . B . B .
        . . . . .                . . B . .
        """
        # Place three connected white stones
        whites = [(2, 2), (2, 3), (3, 2)]
        for r, c in whites:
            self.play(Stone.WHITE, r, c)

        # Surround them with black
        surround = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 4), (3, 1), (3, 3)]
        for r, c in surround:
            self.play(Stone.BLACK, r, c)

        # Verify initial state
        initial = [
            ".....",
            ".BBB.",
            ".BWWB",
            ".BWB.",
            ".....",
        ]
        self.verify_board(initial)

        # Place the final black stone to capture
        self.play(Stone.BLACK, 4, 2)

        # Verify all white stones are captured
        expected = [
            ".....",
            ".BBB.",
            ".B..B",
            ".B.B.",
            "..B..",
        ]
        self.verify_board(expected)

    def test_suicide_not_allowed(self):
        """Test that suicide moves are not allowed.

        Board setup:
        . . . . .
        . . B . .
        . B . B .
        . . B . .
        . . . . .

        White cannot play at (2,2) as it would have no liberties.
        """
        # Black surrounds (2,2)
        for r, c in [(1, 2), (2, 1), (2, 3), (3, 2)]:
            self.play(Stone.BLACK, r, c)

        # Verify the board state
        expected = [
            ".....",
            "..B..",
            ".B.B.",
            "..B..",
            ".....",
        ]
        self.verify_board(expected)

        # Now White tries suicide at (2,2)
        with self.assertRaises(ValueError) as cm:
            self.play(Stone.WHITE, 2, 2)
        self.assertIn("suicide", str(cm.exception))

    def test_capture_on_edge(self):
        """Test capturing stones on the edge of the board.

        Initial setup:   After capture:
        W B . . .       . B . . .
        B . . . .  -->  B . . . .
        . . . . .       . . . . .
        . . . . .       . . . . .
        . . . . .       . . . . .
        """
        # White on the corner at (0,0)
        self.play(Stone.WHITE, 0, 0)

        # Verify initial state
        initial = [
            "W....",
            ".....",
            ".....",
            ".....",
            ".....",
        ]
        self.verify_board(initial)

        # Black occupies its two edge‐liberties
        for r, c in [(0, 1), (1, 0)]:
            self.play(Stone.BLACK, r, c)

        # Verify final state
        expected = [
            ".B...",
            "B....",
            ".....",
            ".....",
            ".....",
        ]
        self.verify_board(expected)

    def test_no_false_capture(self):
        """Test that stones with remaining liberties are not captured.

        Board setup:
        . . . . .
        . . B . .
        . B W . .
        . . B . .
        . . . . .

        White still has a liberty at (2,3) so it should not be captured.
        """
        # Surround white on only three sides
        self.play(Stone.WHITE, 2, 2)
        for r, c in [(1, 2), (2, 1), (3, 2)]:
            self.play(Stone.BLACK, r, c)

        # Verify board state
        expected = [
            ".....",
            "..B..",
            ".BW..",
            "..B..",
            ".....",
        ]
        self.verify_board(expected)

        # Verify white stone remains (not captured)
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
            with self.subTest(surrounded=surrounded):
                # Create a fresh board for each subtest
                b = Board(size=5)

                def play(color, r, c):
                    b.current_turn = color
                    b.place_stone(r, c)

                # Place the white stone to be captured
                play(Stone.WHITE, *surrounded)

                # Surround it with black
                for pos in surrounding:
                    play(Stone.BLACK, *pos)

                # Verify capture
                self.assertEqual(b.grid[surrounded[0]][surrounded[1]], Stone.EMPTY)

    def test_undo_after_capture(self):
        # Setup a single capture
        self.play(Stone.WHITE, 1, 1)
        for r, c in [(0, 1), (1, 0), (1, 2), (2, 1)]:
            self.play(Stone.BLACK, r, c)
        # The white at (1,1) should be gone now:
        self.assertEqual(self.b.grid[1][1], Stone.EMPTY)
        # Undo that last capture move
        last_move = self.b.move_history[-1]
        self.b.undo()
        # Capturing black should be removed
        r, c = last_move
        self.assertEqual(self.b.grid[r][c], Stone.EMPTY)
        # White stone should be back
        self.assertEqual(self.b.grid[1][1], Stone.WHITE)
        # Turn restored to BLACK
        self.assertEqual(self.b.current_turn, Stone.BLACK)

    def test_move_history_and_turn_switch(self):
        """Test that move history is correctly recorded and turns switch properly."""
        # Play a few moves
        self.play(Stone.BLACK, 0, 0)
        self.play(Stone.WHITE, 1, 1)

        # Verify move history
        self.assertEqual(self.b.move_history, [(0, 0), (1, 1)])

        # Verify turn switched correctly
        self.assertEqual(self.b.current_turn, Stone.BLACK)

    def test_pass_and_undo(self):
        """Test that pass moves and undo functionality work correctly."""
        # Make a move and then pass
        self.play(Stone.BLACK, 0, 0)
        self.b.pass_move()  # WHITE passes

        # Verify move history and current turn
        self.assertEqual(self.b.move_history, [(0, 0), None])
        self.assertEqual(self.b.current_turn, Stone.BLACK)

        # Undo the pass
        self.b.undo()
        self.assertEqual(self.b.move_history, [(0, 0)])
        self.assertEqual(self.b.current_turn, Stone.WHITE)

        # Undo the move
        self.b.undo()
        self.assertEqual(self.b.move_history, [])
        self.assertEqual(self.b.current_turn, Stone.BLACK)
        self.assertEqual(self.b.grid[0][0], Stone.EMPTY)


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
