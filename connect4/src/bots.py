import random
from board import Board, Slot


class RandomBot:
    def __init__(self, player: Slot):
        self.player = player

    def make_move(self, board: Board) -> int:
        valid_moves = board.valid_moves()
        if not valid_moves:
            raise ValueError("No valid moves available")
        return random.choice(valid_moves)
