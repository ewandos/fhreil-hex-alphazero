import numpy as np
import torch
import torch.optim as optim
from tqdm import tqdm

from hex import Hex
from algo_components import PolicyValueNet, Buffer, generate_self_play_data, play_one_game_against_pure_mcts, get_device

# @@@@@@@@@@ hyper-parameters @@@@@@@@@@

game_klass = Hex
num_games_for_training = 1000  # in total, 3000 self-play games will be played
num_grad_steps = 50
eval_freq = 100  # evaluate alphazero once per 1000 self-play games
eval_num_games = 5  # 5 first-hand games, 5 second-hand games
buffer_size = 20000
batch_size = 512
num_mcts_iter_alphazero = 500
num_mcts_iter_pure_mcts = 500

# @@@@@@@@@@ important objects @@@@@@@@@@

board_width, board_height = game_klass().board.shape
policy_value_net = PolicyValueNet(board_width, board_height).float().to(get_device())
optimizer = optim.Adam(policy_value_net.parameters(), lr=1e-3, weight_decay=1e-4)  # l2 norm
buffer = Buffer(board_width, board_height, buffer_size, batch_size)

# @@@@@@@@@@ training loop @@@@@@@@@@

for game_idx in tqdm(range(num_games_for_training)):  # for each self-play game ...

    # self-play means to let the current alphazero play with itself (with exploration noise added)

    states, mcts_probs, zs = generate_self_play_data(
        game_klass=game_klass,
        num_mcts_iter=num_mcts_iter_alphazero,
        policy_value_fn=policy_value_net.policy_value_fn,
        high_temp_for_first_n=3
    )

    buffer.push(states, mcts_probs, zs)

    # update the policy-value network using supervised training

    if buffer.is_ready():

        for n in range(num_grad_steps):

            states_b, mcts_probs_b, zs_b = buffer.sample()
            predicted_log_probs, predicted_zs = policy_value_net(states_b)

            loss_part1 = torch.mean((zs_b - predicted_zs) ** 2)
            loss_part2 = - torch.mean(torch.sum(mcts_probs_b * predicted_log_probs, dim=1))
            loss = loss_part1 + loss_part2

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    # evaluate alphazero infrequently against a pure MCTS play
    # this can be very time-consuming, so set eval_freq to a large value and num_mcts_iter_pure_mcts
    # for a small value

    if (game_idx + 1) % eval_freq == 0:

        first_hand_scores = []
        for i in range(eval_num_games):
            score = play_one_game_against_pure_mcts(
                game_klass=game_klass,
                num_mcts_iters_pure=num_mcts_iter_pure_mcts,
                num_mcts_iters_alphazero=num_mcts_iter_alphazero,
                policy_value_fn=policy_value_net.policy_value_fn,
                first_hand="alphazero"
            )
            first_hand_scores.append(score)

        second_hand_scores = []
        for i in range(eval_num_games):
            score = play_one_game_against_pure_mcts(
                game_klass=game_klass,
                num_mcts_iters_pure=num_mcts_iter_pure_mcts,
                num_mcts_iters_alphazero=num_mcts_iter_alphazero,
                policy_value_fn=policy_value_net.policy_value_fn,
                first_hand="pure_mcts"
            )
            second_hand_scores.append(score)

        mean_first_hand_score = float(np.mean(first_hand_scores))
        mean_second_hand_score = float(np.mean(second_hand_scores))

        mean_score = (mean_first_hand_score + mean_second_hand_score) / 2

        print(f"@@@@@ Eval after {game_idx + 1}/{num_games_for_training} "
              f"games against pure-mcts {num_mcts_iter_pure_mcts} @@@@@")

        print(f"Score (first-hand): {round(mean_first_hand_score, 2)}")
        print(f"Score (second-hand): {round(mean_second_hand_score, 2)}")
        print(f"Score (overall): {round(mean_score, 2)}")

        torch.save(policy_value_net.state_dict(), f"trained_models/pvnet_{game_idx+1}.pth")
