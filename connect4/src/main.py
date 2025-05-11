from board import Board, Slot
from console_ui import ConsoleUI
from bots import RandomBot


def main():
    board = Board()
    ui = ConsoleUI(board)
    # Create bot as yellow player
    bot = RandomBot(Slot.YELLOW)

    while True:
        ui.render()

        # Human player's turn (RED)
        if board.current_turn == Slot.RED:
            try:
                col = ui.prompt_move()
                if not board.drop_piece(col, board.current_turn):
                    print("Invalid move! Column is full.")
                    continue

            except ValueError:
                print("Invalid input! Please enter a number between 0 and 6.")
                continue
            except IndexError:
                print("Invalid move! Please enter a number between 0 and 6.")
                continue
            except KeyboardInterrupt:
                print("\nThanks for playing!")
                break

        # Bot's turn (YELLOW)
        else:
            col = bot.make_move(board)
            print(f"Bot players column {col}")
            board.drop_piece(col, Slot.YELLOW)

        # Check for win
        if board.check_win(board.current_turn):
            ui.render()
            print(f"{board.current_turn.name} wins!")
            break

        # Check for draw
        if not board.valid_moves():
            ui.render()
            print("It's a draw!")
            break

        # Switch turn
        board.current_turn = Slot.YELLOW if board.current_turn == Slot.RED else Slot.RED


if __name__ == "__main__":
    main()
