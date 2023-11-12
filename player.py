#!/usr/bin/env python3
from typing import List, Tuple, Optional

import random

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

        depth: int = 5
        best_value, best_move = self.minimax(initial_tree_node, True, depth)

        return ACTION_TO_STR[best_move]

    def minimax(self, node: Node, player: bool, depth: int) -> Tuple[float, int]:
        """
        node contains state
        player = True/False (max/min)
        returns value
        """

        children: List[Node] = node.compute_and_get_children()
        best_value: float = float('-inf') if player else float('inf')
        best_move: int = 0

        if depth == 0:  # or no fish positions
            return self.heuristic(node), best_move

        if player:
            for child in children:
                tmp_value, tmp_move = self.minimax(child, not player, depth-1)
                if tmp_value > best_value:  # cant do max cus we need the move
                    best_value = tmp_value
                    best_move = child.move
                # best_value = max(best_value, tmp_value)
        else:
            for child in children:
                tmp_value, tmp_move = self.minimax(child, not player, depth-1)
                if tmp_value < best_value:  # cant do min cus we need the move
                    best_value = tmp_value
                    best_move = child.move

        return best_value, best_move

    def heuristic(self, node: Node) -> float:
        """
        does not need to account for player, it's done in minmax
        returns value
        """
        player0, player1 = node.state.get_player_scores()
        score: float = player0 - player1

        return score
