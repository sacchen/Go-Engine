from enum import Enum, auto
from typing import List, Tuple, Set, Optional


class Stone(Enum):
    EMPTY = auto()
    BLACK = auto()
    WHITE = auto()


class Board:
    def __init__(self, size: int):

        self.size: int = size
        self.grid: List[List[Stone]] = [
            [Stone.EMPTY for _ in range(self.size)] for _ in range(self.size)
        ]
        self.current_turn: Stone = Stone.BLACK
        self.move_history: List[Optional[Tuple[int, int]]] = []

    def place_stone(self, row: int, col: int) -> None:
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(f"Move ({row},{col}) out of bounds")

        if self.grid[row][col] is not Stone.EMPTY:
            raise ValueError("Illegal move: space occupied.")

        self.grid[row][col] = self.current_turn
        self.move_history.append((row, col))
        self.switch_turn()

    def switch_turn(self) -> None:
        self.current_turn = (
            Stone.BLACK if self.current_turn is Stone.WHITE else Stone.WHITE
        )

    def pass_move(self) -> None:
        self.move_history.append(None)  # Add None to represent a pass
        self.switch_turn()

    def undo(self) -> None:
        if not self.move_history:
            raise RuntimeError("No moves to undo")
        last_move = self.move_history.pop()
        if last_move is not None:  # If not a pass move
            row, col = last_move
            self.grid[row][col] = Stone.EMPTY
        self.switch_turn()

    def get_group_and_liberties(
        self, row: int, col: int
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        visited = set()
        group = set()
        liberties = set()

        color = self.grid[row][col]
        if color == Stone.EMPTY:  # Empty positions return empty sets
            return (group, liberties)

        def dfs(row: int, col: int) -> None:
            if not (0 <= row < self.size and 0 <= col < self.size):
                return

            if (row, col) in visited:
                return
            visited.add((row, col))

            current_color = self.grid[row][col]

            if current_color == Stone.EMPTY:
                liberties.add((row, col))
                return
            elif current_color == color:
                group.add((row, col))
                # Check all adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_r = row + dr
                    new_c = col + dc
                    if 0 <= new_r < self.size and 0 <= new_c < self.size:
                        dfs(new_r, new_c)

        dfs(row, col)
        return (group, liberties)
