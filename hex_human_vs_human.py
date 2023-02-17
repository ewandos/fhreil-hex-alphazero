from ast import literal_eval
import torch

from hex import Hex
from algo_components import PolicyValueNet


game = Hex()

policy_value_net = PolicyValueNet(*game.board.shape)
policy_value_net.load_state_dict(torch.load("trained_models/pvnet_10.pth", map_location=torch.device('cpu')))

print(game)

while True:

    if game.current_player == -1:  # alphazero is always first-hand

        move = literal_eval(input("What's your move play -1: "))
        move = (move[0], move[1])

    else:

        move = literal_eval(input("What's your move player 1: "))
        move = (move[0], move[1])

    done, winner = game.evolve(move)
    if game.get_previous_player() == -1:
        print("@@@@@ -1 just moved @@@@@")
    print(game)

    if done:
        print(game)
        print(f"Winner is player {winner}.")
        break
