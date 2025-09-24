from board import Board, Slot
from console_ui import ConsoleUI
from bots import RandomBot
import time


def main():
    board = Board()
    ui = ConsoleUI(board)

    # Ask player to choose color
    while True:
        choice = input("Do you want to play as RED or YELLOW? r/y: ").lower()
        if choice == "r":
            player_color = Slot.RED
            bot_color = Slot.YELLOW
            print("You will play as RED.")
            break
        elif choice == "y":
            player_color = Slot.YELLOW
            bot_color = Slot.RED
            print("You will player as YELLOW.")
            break
        elif choice == "exit":
            print("Exiting the game. Goodbye!")
            exit()
        else:
            print("Invalid color. Enter 'r' for RED or 'y' for YELLOW.")

    # Create bot
    bot = RandomBot(bot_color)

    while True:
        ui.render()

        # Human player's turn
        if board.current_turn == player_color:
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

        # Bot's turn
        else:
            print(f"Bot is thinking...")
            time.sleep(1.0)
            col = bot.make_move(board)
            print(f"Bot players column {col}")
            board.drop_piece(col, bot_color)

        # Check for win
        if board.check_win(board.current_turn):
            ui.render()
            winner_msg = (
                "You win!" if board.current_turn == player_color else "Bot wins!"
            )
            print(f"{winner_msg} ({board.current_turn.name})")
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
