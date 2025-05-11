from enum import Enum, auto
from typing import List, Tuple, Set, Optional


class Slot(Enum):
    EMPTY = auto()
    RED = auto()
    YELLOW = auto()


class Board:
    def __init__(self):
        self.num_rows: int = 6
        self.num_cols: int = 7
        self.grid: List[List[Slot]] = [
            [Slot.EMPTY for _ in range(self.num_cols)] for _ in range(self.num_rows)
        ]
        self.current_turn = Slot.RED

    def valid_moves(self) -> List[int]:
        """
        Returns list of columns that have an EMPTY slot at the very top
        """
        return [
            col
            for col in range(self.num_cols)
            if self.grid[self.num_rows - 1][col] == Slot.EMPTY
        ]

    def drop_piece(self, col: int, player: Slot) -> bool:
        """
        Scans rows from bottom and set first EMPTY slot to player and return True
        """
        for row in range(self.num_rows):
            if self.grid[row][col] == Slot.EMPTY:
                self.grid[row][col] = player
                return True
        return False  # Column is full

    def __str__(self):
        rows = []
        for r in reversed(range(self.num_rows)):
            rows.append(" ".join(slot.name[0] for slot in self.grid[r]))
        return "\n".join(rows)

    def check_win(self, player: Slot) -> bool:
        """
        Check if player has won by checkingj:
        1. Horizontal lines
        2. Vertical lines
        3. Diagonal lines (both directions)
        """
        # Check horizontal
        for row in range(self.num_rows):
            for col in range(self.num_cols - 3):
                if all(self.grid[row][col + i] == player for i in range(4)):
                    return True

        # Check vertical
        for row in range(self.num_rows - 3):
            for col in range(self.num_cols):
                if all(self.grid[row + i][col] == player for i in range(4)):
                    return True

        # Check diagonal (down-right)
        for row in range(self.num_rows - 3):
            for col in range(self.num_cols - 3):
                if all(self.grid[row + i][col + i] == player for i in range(4)):
                    return True

        # Check diagonal (down-left)
        for row in range(self.num_rows - 3):
            for col in range(3, self.num_cols):
                if all(self.grid[row + i][col - i] == player for i in range(4)):
                    return True

        return False
