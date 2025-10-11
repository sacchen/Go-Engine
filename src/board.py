from enum import Enum, auto
from typing import List, Tuple, Set, Optional
from collections import deque

Point = Tuple[int, int]
Group = Set[Point]
Liberties = Set[Point]


class Stone(Enum):
    EMPTY = auto()
    BLACK = auto()
    WHITE = auto()

    @property
    def opponent(self):
        if self is Stone.BLACK:
            return Stone.WHITE
        if self is Stone.WHITE:
            return Stone.BLACK
        return Stone.EMPTY


class Board:
    NEIGHBORS = ((0, 1), (0, -1), (1, 0), (-1, 0))

    def __init__(self, size: int):
        self.size: int = size
        self.grid: List[List[Stone]] = [
            [Stone.EMPTY for _ in range(self.size)] for _ in range(self.size)
        ]

        self.current_turn: Stone = Stone.BLACK
        # history of played points (None = pass)
        self.move_history: List[Optional[Point]] = []
        # parallel history of exactly which stones were removed on each move
        self.captured_history: List[List[Tuple[int, int, Stone]]] = []
        self.ko_point: Optional[Point] = None
        self.ko_history: List[Optional[Point]] = []
        self.consecutive_passes: int = 0
        self.consecutive_passes_history: List[int] = []

    def _is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

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
        if not self._is_on_board(row, col):
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
        enemy_color = self.current_turn.opponent
        captured_any = False

        # Collect unique adjacent enemy groups
        processed_groups: Set[Point] = set()  # Renamed 'checked' for clarity
        for dr, dc in self.NEIGHBORS:
            neighbor_row, neighbor_col = row + dr, col + dc

            # Use a 'continue' pattern to keep the main logic clean
            if not self._is_on_board(neighbor_row, neighbor_col):
                continue
            if (neighbor_row, neighbor_col) in processed_groups:
                continue
            if self.grid[neighbor_row][neighbor_col] != enemy_color:
                continue

            # If we get here, we've found a new enemy group to check.
            group, liberties = self.get_group_and_liberties(neighbor_row, neighbor_col)
            processed_groups.update(group)  # Mark the whole group as processed

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
        self.consecutive_passes_history.append(self.consecutive_passes)
        self.consecutive_passes = 0
        self.switch_turn()

    def switch_turn(self) -> None:
        self.current_turn = self.current_turn.opponent

    def pass_move(self) -> None:
        self.ko_point = None  # A pass resolves any ko situation.
        self.move_history.append(None)
        self.captured_history.append([])  # no captures on pass
        self.ko_history.append(self.ko_point)  # Record the change to ko history
        self.consecutive_passes_history.append(self.consecutive_passes)
        self.consecutive_passes += 1
        self.switch_turn()

    def undo(self) -> None:
        if not self.move_history:
            raise RuntimeError("No moves to undo")

        last_move = self.move_history.pop()
        captured = self.captured_history.pop()
        self.ko_history.pop()
        self.consecutive_passes_history.pop()

        # Restore the ko_point to what it was BEFORE the last move
        self.ko_point = self.ko_history[-1] if self.ko_history else None

        # Restore the consecutive_passes to what it was BEFORE the last move
        self.consecutive_passes = (
            self.consecutive_passes_history[-1]
            if self.consecutive_passes_history
            else 0
        )

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

    @property
    # Decorator that turns method into a "getter," or read-only.
    def is_over(self) -> bool:
        return self.consecutive_passes >= 2

    def calculate_scores(self) -> dict:
        """
        Calculates territory points for each player.

        This method iterates through each point on the board. If an unvisited
        empty point is found, it starts a search to determine which player(s)
        can reach that empty region.
        """
        black_territory = 0
        white_territory = 0
        visited = set()

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == Stone.EMPTY and (r, c) not in visited:
                    # This group of empty points hasn't been scored yet.
                    # Let's find out who it belongs to.
                    region_points, reaches = self._find_empty_region_reach(r, c)

                    # Mark all points in this region as visited so we don't count them again.
                    visited.update(region_points)

                    # A region is territory if it can only be reached by one color.
                    reaches_black = Stone.BLACK in reaches
                    reaches_white = Stone.WHITE in reaches

                    if reaches_black and not reaches_white:
                        black_territory += len(region_points)
                    elif reaches_white and not reaches_black:
                        white_territory += len(region_points)

        return {"black_territory": black_territory, "white_territory": white_territory}

    def _find_empty_region_reach(
        self, start_row: int, start_col: int
    ) -> Tuple[Set[Point], Set[Stone]]:
        """
        Finds a contiguous region of empty points and determines which stone
        colors are reachable from it.

        Args:
            start_row: The starting row of the empty point.
            start_col: The starting column of the empty point.

        Returns:
            A tuple containing:
            - A set of (row, col) points belonging to the contiguous empty region.
            - A set of Stone enums (BLACK, WHITE) that border the region.
        """
        if self.grid[start_row][start_col] is not Stone.EMPTY:
            return set(), set()

        region_points = set()
        reachable_colors = set()
        queue = deque([(start_row, start_col)])
        visited_in_region = {(start_row, start_col)}

        while queue:
            r, c = queue.popleft()
            region_points.add((r, c))

            for dr, dc in self.NEIGHBORS:
                nr, nc = r + dr, c + dc

                if not self._is_on_board(nr, nc):
                    continue

                neighbor_stone = self.grid[nr][nc]
                if neighbor_stone is Stone.EMPTY:
                    if (nr, nc) not in visited_in_region:
                        visited_in_region.add((nr, nc))
                        queue.append((nr, nc))
                else:
                    # We've reached a colored stone from this empty region.
                    reachable_colors.add(neighbor_stone)

        return region_points, reachable_colors

    def get_final_scores(self, komi: float = 6.5) -> dict:
        """
        Calculates the final score using Chinese scoring rules.
        Score = (Territory) + (Number of stones on the board)
        """
        scores = {"black": 0, "white": 0}

        # Get territory points
        territory = self.calculate_scores()
        scores["black"] += territory["black_territory"]
        scores["white"] += territory["white_territory"]

        # Add stone points
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == Stone.BLACK:
                    scores["black"] += 1
                elif self.grid[r][c] == Stone.WHITE:
                    scores["white"] += 1

        # Add komi for white
        scores["white"] += komi

        return scores
