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
            if self.grid[self.new_rows - 1][col] == Slot.EMPTY
        ]

    def drop_piece(self, col: int, player: Slot) -> bool:
        """
        Scans rows from bottom and set first EMPTY slot to player and return True
        """
        for row in range(self.num_rows):
            if self.grid[row][col] == Slot.EMPTY:
                self.grid[row][col] == player
                return True
        return False  # Column is full
