import unittest
from board import Board, Stone


class TestBoard(unittest.TestCase):
    def test_get_group_and_liberties(self):
        # Create a 5x5 board
        board = Board(5)

        # Place some stones to create a group with liberties
        # B = Black, W = White, . = Empty
        # . . . . .
        # . B B . .
        # . B . . .
        # . . . . .
        # . . . . .

        board.place_stone(1, 1)  # First black stone
        board.place_stone(1, 2)  # Second black stone
        board.place_stone(2, 1)  # Third black stone

        # Test the group and liberties for the black group
        group, liberties = board.get_group_and_liberties(1, 1)

        # The group should contain all three black stones
        expected_group = {(1, 1), (1, 2), (2, 1)}
        self.assertEqual(group, expected_group)

        # The liberties should be the empty spaces adjacent to the group
        expected_liberties = {(0, 1), (0, 2), (1, 0), (1, 3), (2, 0), (2, 2), (3, 1)}
        self.assertEqual(liberties, expected_liberties)


if __name__ == "__main__":
    unittest.main()
