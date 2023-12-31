#!/usr/bin/env python3
from typing import List, Tuple, Optional, Dict
import time

import random
import math

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def search_best_next_move(self, initial_tree_node):
        """
        Use minimax (and extensions) to find best possible next move for player 0 (green boat)
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE USING MINIMAX ###

        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!

        depth: int = 12  # higher number means more time to search deeper depths
        self.end_condition: float = time.time() + 55 * 1e-3
        self.transposition_table: Dict[str, Tuple[float, int]] = {}

        # iterative deepening search
        while not self.cutoff_test(depth):
            best_value, best_move = self.minimax(initial_tree_node, True, depth)
            depth += 1
            #  maybe cutoff if depth is too high, or score is too high if good enough.
            #  1000 not necessary since it is already so restrictive. 10 is enough tbh, or not even needed to be honest
            #  nvm it is score + max distance so higher number is necesarry
            #  however it should be - quisence search
            #  nvm that is not quiscence search, it is not applicable to this assignment
            #  or maybe i dont knnow
        # print(best_value)
        # print(depth)
        return ACTION_TO_STR[best_move]

    def minimax(self, node: Node, player: bool, depth: int,
                alpha: float = float('-inf'), beta: float = float('inf')) -> Tuple[float, int]:
        """
        node contains state
        player = True/False (max/min)
        returns value
        """

        if self.cutoff_test(depth):
            return self.heuristic(node), 0

        key: str = str(node.state.get_fish_positions()) + str(node.state.get_hook_positions()) + str(depth)
        if key in self.transposition_table:
            return self.transposition_table[key]

        children: List[Node] = node.compute_and_get_children()

        # Move ordering based on heuristic score
        children.sort(reverse=True, key=lambda x: self.heuristic(x))

        # Forward pruning with beam search
        # if len(children) == 5:
        #    children = children[:3]

        best_value: float = float('-inf') if player else float('inf')
        best_move: int = 0

        if player:
            # look for max value
            for child in children:
                tmp_value, tmp_move = self.minimax(child, not player, depth - 1,
                                                   alpha, beta)
                if tmp_value > best_value:  # cant do max cus we need the move
                    best_value = tmp_value
                    best_move = child.move

                # prune if possible
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
        else:
            # look for min value
            for child in children:
                tmp_value, tmp_move = self.minimax(child, not player, depth - 1,
                                                   alpha, beta)
                if tmp_value < best_value:  # cant do min cus we need the move
                    best_value = tmp_value
                    best_move = child.move

                # prune if possible
                beta = min(beta, best_value)
                if beta <= alpha:
                    break

        # add best value and move to transposition table
        self.transposition_table[key] = (best_value, best_move)
        return best_value, best_move

    def heuristic(self, node):

        # Get information from current game state
        gameboard_size = 20
        green_hook, fish_positions, fish_scores, boat_scores = (
            node.state.get_hook_positions()[0],
            node.state.get_fish_positions(),
            node.state.get_fish_scores(),
            node.state.get_player_scores(),
        )

        score: float = boat_scores[0] - boat_scores[1]

        # Calculate the maximum distance between the hook and the fish using functional programming
        fish_distances = (fish_scores[fish_id] * math.exp(-1 * (min(abs(green_hook[0] - fish_coord[0]),
                                                                    gameboard_size - abs(
                                                                        green_hook[0] - fish_coord[0])) + abs(
            green_hook[1] - fish_coord[1])))
                          for fish_id, fish_coord in fish_positions.items()
                          )

        max_distance = max(fish_distances, default=0)

        return score + max_distance

    def cutoff_test(self, depth: int) -> bool:
        """
        return True if cutoff
        """
        return depth == 0 or time.time() >= self.end_condition
