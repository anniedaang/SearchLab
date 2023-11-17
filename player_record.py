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

        depth: int = 7  # higher number means more time to search deeper depths

        self.end_condition: float = time.time() + 1*60e-3
        self.transposition_table: Dict = {}
        self.transposition_table['timeout'] = False

        best_value: float = float('-inf')
        best_move: int = 0

        # iterative deepening search
        while not self.cutoff_test(depth):
            tmp_value, tmp_move = self.minimax(initial_tree_node, True, depth, 0)
            if self.transposition_table['timeout']:
                break
            if tmp_value > best_value:
                best_value = tmp_value
                best_move = tmp_move
            depth += 1
            #print()

            #  maybe cutoff if depth is too high, or score is too high if good enough.
            #  1000 not necessary since it is already so restrictive. 10 is enough tbh, or not even needed to be honest
            #  nvm it is score + max distance so higher number is necesarry
            #  however it should be - quisence search
            #  nvm that is not quiscence search, it is not applicable to this assignment
            #  or maybe i dont knnow
        # print(best_value)
        # print(depth)
        #print(depth)
        #print('MOVE', ACTION_TO_STR[best_move])
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
        children.sort(reverse=player, key=lambda x: self.heuristic(x))

        # Forward pruning with beam search
        #if len(children) == 5:
        #    children = children[:1]

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
        """
        does not need to account for player, it's done in minmax
        returns value
        """

        fish_scores: dict = node.state.get_fish_scores()
        green_score, red_score = node.state.get_player_scores()
        score: float = green_score - red_score
        max_value: float = 0

        for fish_id, coords in node.state.get_fish_positions().items():
            fish_score: int = fish_scores[fish_id]
            fish_distance: float = self.calculate_distance(node, coords)
            if fish_distance == 0:
                max_value = fish_score
            tmp_value: float = fish_score * math.exp(-fish_distance)
            max_value = max(max_value, tmp_value)

        value = 5*score + max_value
        #1 score
        #2kolla på om fisken är på kroken för de är snart score
        #3 fiskar längre bort
        #print(value)
        #vikta fisken på kroken högre om den är längre upp
        # kolla stay sist, eller om stay och en annan väg har samma värde så välj inte stay
        return value

    def calculate_distance(self, node: Node, fish_coords: Tuple[int, int]) -> float:
        fish_x, fish_y = fish_coords
        green_x, green_y = node.state.get_hook_positions()[0]
        red_x, _ = node.state.get_hook_positions()[1]
        y_distance: int = abs(green_y - fish_y)
        x_distance: int = abs(green_x - fish_x)
        # TODO need to check which player it is
        if green_x < red_x < fish_x or fish_x < red_x < green_x:
            x_distance = (20 - x_distance)
        return x_distance + y_distance


    def cutoff_test(self, depth: int) -> bool:
        """
        return True if cutoff
        """
        if depth == 0:
            return True
        if time.time() > self.end_condition:
            self.transposition_table['timeout'] = True
            return True
