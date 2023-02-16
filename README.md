## Code tutorial 

Please first make sure that your working directory is `alpha_zero` by `cd alpha_zero`.

How to play against pure MCTS (early moves can take up to 25 seconds but later moves are quicker): 

`python connect4_mcts_vs_human.py`

How to play against pre-trained AlphaZero (moves are fast): 

`python connect4_alphazero_vs_human.py`

How to train AlphaZero from scratch (3000 self-play games & supervised learning takes around 7-8 hours on GPU): 

`python connect4_train_alphazero.py`

Within the training script, you will see `wandb.init`. `wandb` stands for Weights and Biases, a website for tracking machine learning training runs. You can learn about it from their website or their YouTube channel, and change my username and run name to yours. Here, during training, the parameters of the convolutional policy-value network is saved locally as a `pth` file, but they are all uploaded to the cloud (i.e., to `wandb`). This was convenient for me because I didn't know how to download a file from a remote machine. 

After training has finished, you can put `pvnet_3000.pth` in `trained_models` (in `alpha_zero`) and `connect4_alphazero_vs_human.py` will automatically use it.
