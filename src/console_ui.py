from board import Board, Stone


class ConsoleUI:
    COORD_COLOR = "\033[38;5;208m"
    RESET = "\033[0m"

    def __init__(self, board: Board):
        self.board = board

    def display(self) -> None:
        last_move = self.board.move_history[-1] if self.board.move_history else None

        coordinate_color = True

        # Print column headers
        if coordinate_color:
            print("  ", end="")
            for col in range(self.board.size):
                print(f"{self.COORD_COLOR}{col}{self.RESET}", end=" ")
            print()

        for row_idx, row in enumerate(self.board.grid):
            if coordinate_color:
                print(f"{self.COORD_COLOR}{row_idx}{self.RESET} ", end="")

            for col_idx, cell in enumerate(row):
                #     if (row_idx, col_idx) == last_move:
                #         # Highlight last move
                #         if cell == Stone.BLACK:
                #             print("ⓑ", end=" ")
                #         elif cell == Stone.WHITE:
                #             print("ⓦ", end=" ")
                #     else:
                #         print(
                #             {
                #                 Stone.EMPTY: ".",
                #                 Stone.BLACK: "○",
                #                 Stone.WHITE: "●",
                #             }[cell],
                #             end=" ",
                #         )  # Use cell to index into the dictionary
                symbol = self.get_stone_symbol(cell, (row_idx, col_idx) == last_move)
                print(symbol, end=" ")

            print()

    def get_stone_symbol(self, cell: Stone, highlight=False) -> str:
        if cell == Stone.EMPTY:
            return "." if not highlight else "\033[7m.\033[0m"
        elif cell == Stone.BLACK:
            return "○" if not highlight else "\033[7m●\033[0m"
        elif cell == Stone.WHITE:
            return "●" if not highlight else "\033[7m○\033[0m"

    def prompt_move(self) -> None:
        turn_name = self.board.current_turn.name  # why .name
        cmd = input(f"{turn_name} TO PLAY: ").strip().lower()

        if cmd == "exit":
            print("Thanks for playing!")
            exit()
        elif cmd == "pass":
            print(f"{turn_name} passed.")
            self.board.pass_move()
        elif cmd == "undo":
            try:
                self.board.undo()
            except Exception as e:
                print("Error:", e)
        else:
            try:
                row, col = map(int, cmd.split())
                self.board.place_stone(row, col)
            except Exception as e:
                print("Error:", e)

    def run(self):
        while True:
            self.display()

            if self.board.is_over:
                print("Game Over! Two consecutive passes.")
                scores = self.board.get_final_scores()
                print(
                    f"Final Scores -> Black: {scores['black']}, White: {scores['white']}"
                )
                winner = "Black" if scores["black"] > scores["white"] else "White"
                print(f"{winner} wins!")
                break  # End the game

            self.prompt_move()


if __name__ == "__main__":
    board = Board(5)
    ui = ConsoleUI(board)
    ui.run()
