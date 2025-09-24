import random, copy, time
from board import Board, Slot


class RandomBot:
    def __init__(self, player: Slot):
        self.player = player

    def make_move(self, board: Board) -> int:
        valid_moves = board.valid_moves()
        if not valid_moves:
            raise ValueError("No valid moves available")
        return random.choice(valid_moves)

class MinimaxBot:
    def __init__(self, player: Slot, depth=4):
        self.player = player
        self.opponent = Slot.RED if player == Slot.YELLOW else Slot.YELLOW
        self.depth = depth

    def make_move(self, board: Board) -> int:
        # -- Timer and nodes counter --
        start = time.perf_counter()
        self.nodes_searched = 0

        valid_moves = board.valid_moves()
        if not valid_moves:
            raise ValueError("No valid moves available")

        best_score = float("-inf")
        best_move = valid_moves[0]

        for move in valid_moves:
            # Create a copy of the board to simulate moves
            board_copy = copy.deepcopy(board)
            board_copy.drop_piece(move, self.player)

            # Calculate score for this move
            score = self.minimax(
                board_copy, self.depth - 1, False, float("-inf"), float("inf")
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning.

        Parameters:
        - board: Current game board state
        - depth: How many moves to look ahead
        - is_maximizing: True if maximizing bot's turn, False for minimizing (opponent)
        - alpha, beta: Parameters for alpha-beta pruning

        Returns:
        - best score for the current board position
        """
        # -- Node counter --
        self.nodes_searched += 1

        # Step 1: Check terminal conditions
        # Did someone win or is it a draw?
        if board.check_win(self.player):
            return 100  # Bot wins
        elif board.check_win(self.opponent):
            return -100  # Opponent wins
        elif not board.valid_moves() or depth == 0:
            # Either board is full (draw) or we've reached our depth limit
            return self.evaluate_board(board)

        # Step 2: Implement the minimax recursive algorithm
        if is_maximizing:
            # Bot's turn - trying to maximize score
            best_score = float("-inf")

            # Try each valid move
            for move in board.valid_moves():
                # Make a copy to simulate the move without changing original
                board_copy = copy.deepcopy(board)
                board_copy.drop_piece(move, self.player)

                # Recursively find the value of this move
                score = self.minimax(board_copy, depth - 1, False, alpha, beta)

                # DEBUG: Uncomment to see algorithm
                # print(f"MAX depth={depth}, move={move}, score={score}")

                # Update best score
                best_score = max(best_score, score)

                # Alpha-beta pruning (can be added later)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

            return best_score

        else:
            # Opponent's turn - trying to minimize score
            best_score = float("inf")

            # Try each valid move
            for move in board.valid_moves():
                # Make a copy to simulate the move
                board_copy = copy.deepcopy(board)
                board_copy.drop_piece(move, self.opponent)

                # Recursively find the value of this move
                score = self.minimax(board_copy, depth - 1, True, alpha, beta)

                # DEBUG: Uncomment to see algorithm
                # print(f"MIN depth={depth}, move={move}, score={score}")

                # Update best score
                best_score = min(best_score, score)

                # Alpha-beta pruning (can be added later)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break

            return best_score

    def evaluate_board(self, board):
        """
        Evaluate the current board state.
        A positive score is good for the bot, negative is good for opponent.

        Start with a simple implementation, then improve later.
        """
        # Simple evaluation: just count pieces
        # This is not a good strategy but helps understand the algorithm
        score = 0

        # Count bot's pieces
        # for row in range(board.num_rows):
        #     for col in range(board.num_cols):
        #         if board.grid[row][col] == self.player:
        #             score += 1
        #         elif board.grid[row][col] == self.opponent:
        #             score -= 1

        # return score

        # TODO: Improve this evaluation function to look for patterns
        # like three-in-a-row with an empty space

        # Check horizontal, vertical, and diagonal windows
        for row in range(board.num_rows):
            for col in range(board.num_cols - 3):
                # Horizontal windows
                window = [board.grid[row][col + i] for i in range(4)]
                score += self.evaluate_window(window)

        for row in range(board.num_rows - 3):
            for col in range(board.num_cols):
                # Vertical windows
                window = [board.grid[row + i][col] for i in range(4)]
                score += self.evaluate_window(window)

        for row in range(board.num_rows - 3):
            for col in range(board.num_cols - 3):
                # Diagonal (down-right)
                window = [board.grid[row + i][col + i] for i in range(4)]
                score += self.evaluate_window(window)

        for row in range(board.num_rows - 3):
            for col in range(3, board.num_cols):
                # Diagonal (down-left)
                window = [board.grid[row + i][col - i] for i in range(4)]
                score += self.evaluate_window(window)

        # Also prefer center column
        center_col = board.num_cols // 2
        center_count = sum(
            1
            for row in range(board.num_rows)
            if board.grid[row][center_col] == self.player
        )
        score += center_count * 3

        return score

    def evaluate_window(self, window):
        """
        Score a window of 4 slots based on its pattern.
        """
        bot_count = window.count(self.player)
        opponent_count = window.count(self.opponent)
        empty_count = window.count(Slot.EMPTY)

        # Score based on piece patterns
        if bot_count == 4:
            return 100  # Win
        elif bot_count == 3 and empty_count == 1:
            return 10  # Near win
        elif bot_count == 2 and empty_count == 2:
            return 2  # Potential

        # Defensive scoring
        if opponent_count == 3 and empty_count == 1:
            return -10  # Block opponent's near win

        return 0