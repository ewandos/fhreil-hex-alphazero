import numpy as np


class Hex:
    """
        The class hexPosition stores data on a hex board position. The slots of an object are: size (an integer between 2
        and 26), board (an array, 0=noStone, 1=whiteStone, 2=blackStone), and winner (0=noWin, 1=whiteWin, 2=blackWin).
        """

    def __init__(self, size=5):
        super().__init__()
        self.size = max(2, min(size, 26))
        self.board_array = [[0 for _ in range(max(2, min(size, 26)))] for _ in range(max(2, min(size, 26)))]
        self.board = np.array(self.board_array)
        self.winner = 0
        self.players = [-1, 1]
        self.current_player = -1

    # ----------------------------------
    # A I     A P I
    # ----------------------------------

    def get_previous_player(self) -> int:
        return self.current_player * -1

    def get_current_player(self) -> int:
        return self.current_player

    def evolve(self, chosen):
        self.board_array[chosen[0]][chosen[1]] = self.current_player
        self.current_player = 1 if self.current_player == -1 else -1
        self.white_win()
        self.black_win()
        return (False, None) if (self.winner == 0) else (True, self.winner)

    def get_valid_moves(self, recode_black_as_white=False) -> list:
        """
        This method returns a list of array positions which are empty (on which stones may be put).
        """

        actions = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board_array[i][j] == 0:
                    actions.append((i, j))
        if recode_black_as_white:
            return [self.recode_coordinates(action) for action in actions]
        else:
            return actions

    def reset(self):
        """
        This method resets the hex board. All stones are removed from the board.
        """

        self.board_array = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.winner = 0

    # ----------------------------------
    # E N G I N E   F U N C T I O N S
    # ----------------------------------

    def get_adjacent(self, position):
        """
        Helper function to obtain adjacent cells in the board array.
        """

        """
        up = (position[0] - 1, position[1])down = (position[0] + 1, position[1])right = (position[0], position[1] - 1)left = (position[0], position[1] + 1)up_right(position[0] - 1, position[1] - 1)
up_left(position[0] - 1, position[1] + 1)
down_right(position[0] + 1, position[1] - 1)
down_left(position[0] + 1, position[1] + 1)
        """

        up = (position[0] - 1, position[1])
        down = (position[0] + 1, position[1])
        right = (position[0], position[1] - 1)
        left = (position[0], position[1] + 1)
        up_right = (position[0] - 1, position[1] + 1)
        down_left = (position[0] + 1, position[1] - 1)
        down_right = (position[0] + 1, position[1] + 1)
        up_left = (position[0] - 1, position[1] - 1)

        return [pair for pair in [up, down, right, left, up_right, down_left, down_right, up_left] if
                max(pair[0], pair[1]) <= self.size - 1 and min(pair[0], pair[1]) >= 0]

    def recode_coordinates(self, coordinates):
        """
        Transforms a coordinate tuple (with respect to the board) analogously to the method recodeBlackAsWhite.
        """
        return self.size - 1 - coordinates[1], self.size - 1 - coordinates[0]

    def prolong_path(self, path):
        """
        A helper function used for board evaluation.
        """

        player = self.board_array[path[-1][0]][path[-1][1]]
        candidates = self.get_adjacent(path[-1])

        # preclude loops
        candidates = [cand for cand in candidates if cand not in path]
        candidates = [cand for cand in candidates if self.board_array[cand[0]][cand[1]] == player]

        return [path + [cand] for cand in candidates]

    def white_win(self, verbose=False):
        """
        Evaluate whether the board position is a win for 'white'. Uses breadth first search. If verbose=True a winning
        path will be printed to the standard output (if one exists). This method may be time-consuming,
        especially for larger board sizes.
        """

        paths = []
        visited = []
        for i in range(self.size):
            if self.board_array[i][0] == -1:
                paths.append([(i, 0)])
                visited.append([(i, 0)])

        while True:

            if len(paths) == 0:
                return False

            for path in paths:
                prolongations = self.prolong_path(path)
                paths.remove(path)

                for new in prolongations:
                    if new[-1][1] == self.size - 1:
                        if verbose:
                            print("A winning path for White:\n", new)
                        self.winner = -1
                        return True

                    if new[-1] not in visited:
                        paths.append(new)
                        visited.append(new[-1])

    def black_win(self, verbose=False):
        """
        Evaluate whether the board position is a win for 'black'. Uses breadth first search. If verbose=True a winning
        path will be printed to the standard output (if one exists).
        This method may be time-consuming, especially for larger board sizes.
        """

        paths = []
        visited = []
        for i in range(self.size):
            if self.board_array[0][i] == 1:
                paths.append([(0, i)])
                visited.append([(0, i)])

        while True:

            if len(paths) == 0:
                return False

            for path in paths:
                prolongations = self.prolong_path(path)
                paths.remove(path)

                for new in prolongations:
                    if new[-1][0] == self.size - 1:
                        if verbose:
                            print("A winning path for Black:\n", new)
                        self.winner = 1
                        return True

                    if new[-1] not in visited:
                        paths.append(new)
                        visited.append(new[-1])

    def __repr__(self):
        return np.array2string(np.array(self.board_array))
