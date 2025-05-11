# Use
# py -m unittest tests/test_board.py

import unittest
from connect4.src.board import Board, Slot


class TestBoard(unittest.TestCase):

    def test_drop_and_win_horizontal(self):
        b = Board()
        for c in [0, 1, 2, 3]:
            self.assertTrue(b.drop_piece(c, Slot.RED))
        self.assertTrue(b.check_win(Slot.RED))

    def test_full_column_rejects_drop(self):
        b = Board()
        for _ in range(b.num_rows):
            b.drop_piece(0, Slot.YELLOW)
        self.assertFalse(b.drop_piece(0, Slot.YELLOW))


if __name__ == "__main__":
    unittest.main()
