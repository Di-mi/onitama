import operator
import random
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import starmap
from typing import List, Tuple

from game.default_deck import DEFAULT_DECK

BLUE_KING = 2
BLUE_PAWN = 1
RED_KING = -2
RED_PAWN = -1
EMPTY_CELL = 0

BLUE_PLAYER = 'blue'
RED_PLAYER = 'red'


@dataclass
class Card:
    name: str
    move_offset: List[Tuple]
    color: str


@dataclass
class PawnPosition:
    x: int  # horizontal axis
    y: int  # vertical axis


class OnitamaGame:

    def __init__(self, cards=None):
        if cards is None:
            self.cards = self.__pick_random_cards(num_of_cards=5)
        else:
            self.cards = cards

        fifth_card = random.sample(self.cards, 1)[0]

        self.cards.remove(fifth_card)

        self.blue_hand = self.cards[:2]
        self.red_hand = self.cards[2:]

        if fifth_card.color == BLUE_PLAYER:
            self.blue_hand.append(fifth_card)
        else:
            self.red_hand.append(fifth_card)

        self.board = self.__init_board()
        self.blue_king = PawnPosition(x=2, y=0)
        self.red_king = PawnPosition(x=2, y=4)

        self.winner = 0

    def play_card(self, from_x: int, from_y: int, to_x: int, to_y: int, with_card: Card) -> int:
        """
          :return: Integer indicator: 0 - no winners 1 - blue player wins, 2 -  red player wins, 3 - draw
        """
        if self.winner:
            return self.winner

        if len(self.blue_hand) > len(self.red_hand):
            player_color = BLUE_PLAYER
        else:
            player_color = RED_PLAYER

        self.check_validity(player_color, from_x, from_y, to_x, to_y, with_card)
        self.move_pawn(from_x, from_y, to_x, to_y)
        self.winner = self.check_end_game_condition()
        self.rotate_cards(player_color, with_card)

        return self.winner

    def rotate_cards(self, player_color: str, card: Card):
        """
        Use this method to rotate the card after a move
        :param player_color:
        :param card:
        :return:
        """

        from_hand = self.blue_hand
        to_hand = self.red_hand

        if player_color == RED_PLAYER:
            from_hand = self.red_hand
            to_hand = self.blue_hand

        from_hand.remove(card)
        to_hand.append(card)

    def move_pawn(self, from_x, from_y, to_x, to_y) -> None:
        """
        Use this method to move pawn on the board
        :param from_x: x coordinate of the source cell
        :param from_y: y coordinate of the source cell
        :param to_x: x coordinate of the destination cell
        :param to_y: y coordinate of the destination cell
        :return: None
        """

        pawn_value = self.board[from_y][from_x]
        target_value = self.board[to_y][to_x]

        if target_value == BLUE_KING:
            self.blue_king = None

        if target_value == RED_KING:
            self.red_king = None

        if pawn_value == BLUE_KING:
            self.blue_king.x = to_x
            self.blue_king.y = to_y

        elif pawn_value == RED_KING:
            self.red_king.x = to_x
            self.red_king.y = to_y


        self.board[to_y][to_x] = pawn_value
        self.board[from_y][from_x] = EMPTY_CELL

    def check_end_game_condition(self) -> int:
        """
        Use to determine if the game has ended
        :return: Integer indicator: 0 - no winners 1 - blue player wins, 2 -  red player wins, 3 - draw
        """
        if (self.blue_king.x == 2 and self.blue_king.y == 4) or self.red_king is None:
            return 1
        if (self.red_king.x == 2 and self.blue_king == 0) or self.blue_king is None:
            return 2

        board_list = []
        [board_list.extend(row) for row in self.board]

        absolute_sum = reduce(lambda a, b: a + abs(b), board_list)

        if absolute_sum == 4:
            return 3

        return 0

    def check_validity(self, player_color: str, from_x: int, from_y: int, to_x: int, to_y: int,
                       with_card: Card) -> None:
        """
        Use to check validity of a move
        :param player_color: 'blue' or RED_PLAYER
        :param from_x: starting x coordinate
        :param from_y: starting y coordinate
        :param to_x: ending x coordinate
        :param to_y: ending y coordinate
        :param with_card: Card object
        :return: None
        """
        coordinates = [from_x, from_y, to_x, to_y]

        check_coordinates_limits = lambda x: 0 <= x <= 4
        assert all(map(check_coordinates_limits, coordinates)), "Incorrect coordinates provided"

        from_cell = self.board[from_y][from_x]
        to_cell = self.board[to_y][to_x]

        assert from_cell != 0, "Incorrect Coordinates"
        if player_color == BLUE_PLAYER:
            expected_pawn_operator = operator.gt
            player_hand = self.blue_hand
        else:
            expected_pawn_operator = operator.lt
            player_hand = self.red_hand

        assert len(player_hand) == 3, "Incorrect player order"
        assert expected_pawn_operator(from_cell, 0), "Incorrect pawn"
        assert with_card in player_hand[:2], "The player does not have that card available"
        assert ((not expected_pawn_operator(to_cell, 0) or to_cell == 0)), "Destination cell contains attacker pawn"

        move_card = deepcopy(with_card)

        if player_color == RED_PLAYER:
            # card offsets need to be inverted
            move_card.move_offset = [(move[0] * -1, move[1] * -1) for move in with_card.move_offset]

        is_move_valid_with_card = any(
            starmap(lambda x, y: (x + from_x) == to_x and (y + from_y) == to_y, move_card.move_offset))

        assert is_move_valid_with_card, "Invalid move with given pawn and card"

    def __init_board(self):
        """
        Use to initialize starting state of the board
        The blue player starts in row 0, the red player starts in row 4.
        Blue player pawn value: 1
        Red player pawn value: -1
        Blue player king value: 2
        Red player king value: -2
        Empty cell: 0
        :return:
        """

        board = []
        board.append([1] * 5)  # blue player row
        board.append([0] * 5)  # empty cells
        board.append([0] * 5)
        board.append([0] * 5)
        board.append([-1] * 5)  # red player row
        board[0][2] = BLUE_KING  # place king player blue
        board[4][2] = RED_KING  # place king player red

        return board

    def __pick_random_cards(self, deck: list = None, num_of_cards: int = 5) -> List[Card]:
        if deck is None:
            deck = self.__load_all_cards()

        random.shuffle(deck)

        return deck[:num_of_cards]

    def __load_all_cards(self):
        return [Card(**card) for card in DEFAULT_DECK]
