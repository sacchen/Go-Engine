from board import Board, Slot
from bots import RandomBot, MinimaxBot
import random, copy


class GameRunner:
    def __init__(self, bot1, bot2, verbose=True):
        self.bots = [bot1, bot2]
        self.verbose = verbose

    def play(self):
        board = Board()
        turn = 0  # 0 → bot1, 1 → bot2

        # Continue until someone wins or draw
        while True:
            current_bot = self.bots[turn]
            player = current_bot.player

            # Let bot choose its move
            # If it's a MinimaxBot, grab the score it computed:
            if hasattr(current_bot, "_last_score"):
                # clear any old score
                current_bot._last_score = None

            move = current_bot.make_move(board)

            # If you want to capture the minimax score:
            score = getattr(current_bot, "_last_score", None)

            board.drop_piece(move, player)

            if self.verbose:
                print(f"\nTurn {board.move_count}: {player.name} plays column {move}")
                if score is not None:
                    print(f"  → Minimax thinks this is a {score}-point position")
                print(board)  # assuming Board.__str__ prints nicely

            # Check for end of game
            if board.check_win(player):
                print(f"\n{player.name} wins!")
                break
            if not board.valid_moves():
                print("\nDraw!")
                break

            # Swap turn
            turn = 1 - turn

        return board


# --- Hooking into MinimaxBot to record the score it used ---
# Monkey‐patch its minimax call to store the “score” on the bot:

# from bots import MinimaxBot

_orig_minimax = MinimaxBot.minimax


def _tracking_minimax(self, board, depth, is_max, alpha, beta):
    val = _orig_minimax(self, board, depth, is_max, alpha, beta)
    # only store the root‐level call’s return value
    if depth == self.depth - 1 and is_max:
        self._last_score = val
    return val


MinimaxBot.minimax = _tracking_minimax


# --- Tournament loop outside GameRunner class---
def tournament(bot_cls, **kwargs):
    results = {"RED_wins": 0, "YELLOW_wins": 0, "draw": 0}
    for i in range(5):
        # Default player is RED for first bot
        # bot = bot_cls(Slot.RED, **kwargs)
        # mirror‐bot with same class, swapped slot
        # opp = bot_cls(Slot.YELLOW if bot.player == Slot.RED else Slot.RED, **kwargs)

        # Alternate which bot goes first
        if i % 2 == 0:
            bot = bot_cls(Slot.RED, **kwargs)
            opp = bot_cls(Slot.YELLOW, **kwargs)
        else:
            bot = bot_cls(Slot.YELLOW, **kwargs)
            opp = bot_cls(Slot.RED, **kwargs)

        runner = GameRunner(bot, opp, verbose=False)
        final = runner.play()

        if final.check_win(bot.player):
            # Update to use the correct key based on the winner's color
            if bot.player == Slot.RED:
                results["RED_wins"] += 1
            else:
                results["YELLOW_wins"] += 1
        elif final.check_win(opp.player):
            # Update to use the correct key based on the winner's color
            if opp.player == Slot.RED:
                results["RED_wins"] += 1
            else:
                results["YELLOW_wins"] += 1
        else:
            results["draw"] += 1

    print(results)


# --- Runner example usage ---
# if __name__ == "__main__":
#     import random
#     from bots import RandomBot

#     r1 = RandomBot(Slot.RED)
#     r2 = RandomBot(Slot.YELLOW)
#     mm1 = MinimaxBot(Slot.RED, depth=5)
#     mm2 = MinimaxBot(Slot.YELLOW, depth=4)

#     # print("Random vs Random:")
#     # GameRunner(r1, r2).play()

#     # print("\nMinimax vs Random:")
#     # GameRunner(mm1, r2).play()

#     print("\nMinimax vs Minimax:")
#     GameRunner(mm1, mm2).play()

# --- Tournament ---
if __name__ == "__main__":
    tournament(MinimaxBot, depth=4)