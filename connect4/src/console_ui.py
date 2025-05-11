from board import Board


class ConsoleUI:
    def __init__(self, board: Board):
        self.board = board

    def render(self):
        print(str(self.board))

    def prompt_move(self) -> int:
        move = input(f"{self.board.current_turn.name}, choose a column (0–6): ")
        return move
