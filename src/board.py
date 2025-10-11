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
        # history of played points (None = pass)
        self.move_history: List[Optional[Tuple[int, int]]] = []
        # parallel history of exactly which stones were removed on each move
        self.captured_history: List[List[Tuple[int, int, Stone]]] = []
        self.ko_point: Optional[Tuple[int, int]] = None
        self.ko_history: List[Optional[Tuple[int, int]]] = []

    def place_stone(self, row: int, col: int) -> None:
        """
        # 1. Tentatively place stone.
        # 2. Collect adjacent enemy groups (only check each group once).
        # 3. Capture any enemy groups with no liberties.
        # 4. If no captures and own group is dead, revert the move (suicide rule).
        # Capturing takes precedence over suicide.
        # Board state is only finalized after all checks pass.
        """

        # Check for basic illegal moves
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(f"Move ({row},{col}) out of bounds")
        if self.grid[row][col] is not Stone.EMPTY:
            raise ValueError("Illegal move: space occupied.")

        # Check if the move violates the current Ko restriction
        if (row, col) == self.ko_point:
            raise ValueError("Illegal move: this move is forbidden by the Ko rule.")

        # Remember previous state and tentatively place stone
        previous_state = self.grid[row][col]
        self.grid[row][col] = self.current_turn

        # record which enemy stones we actually remove
        captured_positions: List[Tuple[int, int, Stone]] = []

        # Determine enemy color
        enemy_color = Stone.BLACK if self.current_turn == Stone.WHITE else Stone.WHITE
        captured_any = False

        # Collect unique adjacent enemy groups
        # Use a set to avoid rechecking the same group
        adjacent_enemies = {
            (row + dr, col + dc)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= row + dr < self.size
            and 0 <= col + dc < self.size
            and self.grid[row + dr][col + dc] == enemy_color
        }

        checked = set()
        for er, ec in adjacent_enemies:
            if (er, ec) in checked:
                continue  # Skip if this group was already checked

            # Check liberties of enemy group
            group, liberties = self.get_group_and_liberties(er, ec)
            checked.update(group)

            if not liberties:
                # Capture enemy group if no liberties
                captured_any = True
                for r, c in group:
                    # record what we're about to remove
                    captured_positions.append((r, c, enemy_color))
                    self.grid[r][c] = Stone.EMPTY

        # Check for suicide
        # If no enemy groups were captured and the placed stone has no liberties, revert the move
        group, liberties = self.get_group_and_liberties(
            row, col
        )  # Check the stone about to be placed
        if not liberties and not captured_any:
            self.grid[row][col] = previous_state  # Roll back
            raise ValueError("Illegal move: suicide is not allowed.")

        # Clear existing ko_point from the previous turn
        self.ko_point = None

        # Check if this move created a new ko situation.
        if captured_any and len(captured_positions) == 1:
            # A single stone was captured. The point where it was captured is the new ko_point.
            captured_r, captured_c, _ = captured_positions[0]
            # We must also check that the capturing group is also a single stone in atari.
            # This prevents setting ko in non-ko situations like "snapback".
            capturing_group, capturing_libs = self.get_group_and_liberties(row, col)
            if len(capturing_group) == 1:
                self.ko_point = (captured_r, captured_c)

        # Finalize move
        self.move_history.append((row, col))
        self.captured_history.append(captured_positions)
        self.ko_history.append(self.ko_point)
        self.switch_turn()

    def switch_turn(self) -> None:
        self.current_turn = (
            Stone.BLACK if self.current_turn is Stone.WHITE else Stone.WHITE
        )

    def pass_move(self) -> None:
        self.move_history.append(None)
        self.captured_history.append([])  # no captures on pass
        self.switch_turn()

    def undo(self) -> None:
        if not self.move_history:
            raise RuntimeError("No moves to undo")

        last_move = self.move_history.pop()
        captured = self.captured_history.pop()
        self.ko_history.pop()

        # Restore the ko_point to what it was BEFORE the last move
        self.ko_point = self.ko_history[-1] if self.ko_history else None

        if last_move is not None:
            row, col = last_move
            # remove the stone we placed
            self.grid[row][col] = Stone.EMPTY

        # restore any stones we captured on that move
        for r, c, color in captured:
            self.grid[r][c] = color

        self.switch_turn()

    def get_group_and_liberties(
        self, row: int, col: int
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Depth-first search starting at (row, col) returning:
          group      - all same-color stones connected to the seed
          liberties  - set of empty neighbouring points for that group
        """
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
