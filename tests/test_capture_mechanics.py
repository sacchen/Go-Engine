#python -m unittest tests.test_capture_mechanics

import unittest
from src.board import Board, Stone
from typing import List, Tuple, Optional, Set


class TestBoardCapturing(unittest.TestCase):

    def setUp(self):
        self.b = Board(size=5)

    def play(self, color: Stone, row: int, col: int):
        """Place a stone of the given color, regardless of whose turn it "really" is."""
        self.b.current_turn = color
        self.b.place_stone(row, col)

    def play_sequence(self, moves: List[Tuple[Stone, int, int]]):
        """Play a sequence of moves in order."""
        for color, row, col in moves:
            self.play(color, row, col)

    def setup_board(self, layout: List[str]):
        """Setup board from a string layout (B=blacak, W=white, .=empty)."""
        for r, row in enumerate(layout):
            for c, cell in enumerate(row):
                if cell == 'B':
                    self.play(Stone.BLACK, r, c)
                elif cell == 'W':
                    self.play(Stone.WHITE, r, c)


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

    def test_ko_rule_basic(self):
        """Test that immediate recapture is prevented by Ko rule."""
        
        # Step 1: Setup the board
        initial_layout = [
            ".W.W.",
            ".BWB.",
            "..B..",
            ".....",
            ".....",
        ]
        self.setup_board(initial_layout)
        
        # Step 2: Verify the setup worked
        self.verify_board(initial_layout)
        
        # Step 3: Black captures the white stone at (0, 1)
        self.play(Stone.BLACK, 0, 2)
        
        # Step 4: Verify the capture was successful
        # The new black stone should be at (0, 2)
        self.assertEqual(self.b.grid[0][2], Stone.BLACK)
        # The captured white stone's location (1, 2) should now be EMPTY
        self.assertEqual(self.b.grid[1][2], Stone.EMPTY)
        
        # Step 5: White tries to immediately recapture by playing at (1, 2)
        # This move is illegal due to the Ko rule
        with self.assertRaises(ValueError) as cm:
            self.play(Stone.WHITE, 1, 2)
        
        # Step 6: Verify the error message mentions Ko
        self.assertIn("ko", str(cm.exception).lower())



if __name__ == "__main__":
    unittest.main()
