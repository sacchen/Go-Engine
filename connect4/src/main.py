from board import Board, Slot
from console_ui import ConsoleUI


def main():
    board = Board()
    ui = ConsoleUI(board)

    while True:
        ui.render()
        try:
            col = ui.prompt_move()
            if not board.drop_piece(col, board.current_turn):
                print("Invalid move! Column is full.")
                continue

            if board.check_win(board.current_turn):
                ui.render()
                print(f"{board.current_turn.name} wins!")
                break

            board.current_turn = (
                Slot.YELLOW if board.current_turn == Slot.RED else Slot.RED
            )

        except ValueError:
            print("Invalid input! Please enter a number between 0 and 6.")
            continue
        except IndexError:
            print("Invalid move! Please enter a number between 0 and 6.")
            continue
        except KeyboardInterrupt:
            print("\nThanks for playing!")
            break


if __name__ == "__main__":
    main()
