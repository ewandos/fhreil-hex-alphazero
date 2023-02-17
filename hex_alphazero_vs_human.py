from ast import literal_eval
import torch
import numpy as np

from hex import Hex
from algo_components import Node, mcts_one_iter, PolicyValueNet


game = Hex()

policy_value_net = PolicyValueNet(*game.board.shape)
policy_value_net.load_state_dict(torch.load("trained_models/pvnet_10.pth", map_location=torch.device('cpu')))

print(game)

while True:

    if game.current_player == -1:  # alphazero is always first-hand

        pi_vec, _ = policy_value_net.policy_value_fn(game.board * game.get_current_player(), game.get_valid_moves(), True)
        pi_vec[pi_vec < 0.01] = 0
        print("@@@@@ Prior move probabilities @@@@@")
        print(pi_vec.reshape(game.board.shape))

        root = Node(parent=None, prior_prob=1.0)

        for _ in range(np.random.randint(50, 1000)):  # introduce some stochasticity here
            mcts_one_iter(game, root, policy_value_fn=policy_value_net.policy_value_fn)

        move = root.get_move(temp=0)

    else:

        move = literal_eval(input("What's your move: "))
        move = (move[0], move[1])

    done, winner = game.evolve(move)
    if game.get_previous_player() == -1:
        print("@@@@@ AlphaZero just moved @@@@@")
    print(game)

    if done:
        print(game)
        print(f"Winner is player {winner}.")
        break
