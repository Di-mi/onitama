from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional

from game.game import OnitamaGame, Card, PawnPosition, BLUE_PLAYER, RED_PLAYER
MAX_DEPTH = 4

@dataclass
class TreeNode:
    move_from: Optional[PawnPosition]
    move_to: Optional[PawnPosition]
    use_card: Optional[Card]

    blue_win_count: int = 0
    red_win_count: int = 0
    tie_count: int = 0
    end_move: bool = False
    next_moves: Optional[List["TreeNode"]] = None
    parent: Optional["TreeNode"] = None


class DecisionTreeBot:

    def __init__(self, game_initial_state: OnitamaGame, player_color: str):
        self.player_color = player_color
        tree_root = TreeNode(use_card=None, move_to=None, move_from=None, parent=None)
        self._generate_decision_tree(parent=tree_root, game_state=game_initial_state, depth=1)
        self.current_state = tree_root

    def play(self, game: OnitamaGame):
        """
        This is a pubic method which is use in every move
        :param game:
        :return:
        """
        card, from_position, to_position  = self._make_decision_based_on_tree(game)

    def _generate_decision_tree(self, parent: TreeNode, game_state: OnitamaGame,depth):
        """
        Generates a N-tree which goes through all possible moves in the game
        :param parent: root node
        :param game_state: current onitama
        :return: None
        """
        game_copy = game_state
        current_pawn_positions = self._find_pawn_positions(game_copy)

        all_possible_next_positions, all_cards_used = self._find_all_possible_moves(current_pawn_positions, game_copy)

        blue_win_count = 0
        red_win_count = 0
        tie_count = 0

        for from_position, to_position_list, card_used_list in zip(current_pawn_positions,
                                                                   all_possible_next_positions,
                                                                   all_cards_used):
            for to_position, card_used in zip(to_position_list, card_used_list):

                new_game = deepcopy(game_copy)
                try:
                    result = new_game.play_card(from_x=from_position.x,
                                                from_y=from_position.y,
                                                to_x=to_position.x,
                                                to_y=to_position.y,
                                                with_card=card_used)
                except AssertionError:
                    continue
                new_node = TreeNode(use_card=card_used, move_from=from_position, move_to=to_position, parent=parent)
                if not parent.next_moves:
                    parent.next_moves = []
                parent.next_moves.append(new_node)

                if not result and depth < MAX_DEPTH:



                    self._generate_decision_tree(new_node, new_game, depth+1)

                else:
                    new_node.end_move = True
                    if result == 1:
                        new_node.red_win_count += 1
                    elif result == 2:
                        new_node.blue_win_count += 1
                    else:
                        new_node.tie_count += 1


        if parent.next_moves:
            for node in parent.next_moves:
                blue_win_count += node.blue_win_count
                red_win_count += node.red_win_count
                tie_count += node.tie_count

        parent.blue_win_count = blue_win_count
        parent.red_win_count = red_win_count
        parent.tie_count = tie_count

    def _find_pawn_positions(self, game_state) -> List[PawnPosition]:
        """
        Use this method to get all available pawns for the next playing player
        :param game_state: current state of the OnitamaGame
        :return: list of pawn positions
        """

        blue_pawns = []
        red_pawns = []

        for row in range(len(game_state.board)):
            for column in range(len(game_state.board[row])):
                if game_state.board[row][column] > 0:
                    blue_pawns.append(PawnPosition(x=column, y=row))
                elif game_state.board[row][column] < 0:
                    red_pawns.append(PawnPosition(x=column, y=row))

        if len(game_state.blue_hand) > len(game_state.red_hand):
            return blue_pawns
        else:
            return red_pawns

    def _find_all_possible_moves(self,
                                 current_pawn_positions: List[PawnPosition],
                                 game_copy: OnitamaGame) -> (List[tuple], List[Card]):
        """
        This method find all possible end positions for a given list of start positions
        :param current_pawn_positions: start positions of player pawns
        :param game_copy: onitma game instance
        :return:
        """
        possible_moves = []
        card_used = []
        if len(game_copy.blue_hand) > len(game_copy.red_hand):
            player_turn = BLUE_PLAYER

            current_cards = game_copy.blue_hand
        else:
            player_turn = RED_PLAYER
            current_cards = game_copy.red_hand

        for pawn_position in current_pawn_positions:
            end_positions = []
            with_card = []
            for card in current_cards:
                move_card = deepcopy(card)
                if player_turn == RED_PLAYER:
                    # card offsets need to be inverted
                    move_card.move_offset = [(move[0] * -1, move[1] * -1) for move in card.move_offset]

                for offset in move_card.move_offset:
                    to_x = pawn_position.x + offset[0]
                    to_y = pawn_position.y + offset[1]
                    if 0 <= to_x <= 4 and 0 <= to_y <= to_y:
                        end_positions.append(PawnPosition(to_x, to_y))
                        with_card.append(card)

            possible_moves.append(end_positions)
            card_used.append(with_card)

        return possible_moves, card_used

    # def _make_decision_based_on_tree(self, game):
    #     for
