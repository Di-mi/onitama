import pytest

from game.game import OnitamaGame, Card


def test_initial_game_state():
    game = OnitamaGame()
    assert sum(sum(row) for row in game.board) == 0
    assert len(game.red_hand) + len(game.blue_hand) == 5


def test_move_validation__should_not_be_able_to_move():
    card = Card('TestCard', [(1, 1), (-1, 0), (1, 0)], color='blue')
    cards = [card] * 5
    game = OnitamaGame(cards=cards)
    with pytest.raises(AssertionError):
        game.play_card(from_x=2, from_y=0, to_x=1, to_y=0, with_card=game.blue_hand[0])
        game.play_card(from_x=2, from_y=0, to_x=2, to_y=1, with_card=game.blue_hand[0])


def test_move_validation__should_be_successful():
    card = Card('TestCard', [(1, 1), (-1, 0), (1, 0)], color='blue')
    cards = [card] * 5
    game = OnitamaGame(cards=cards)
    game.play_card(from_x=2, from_y=0, to_x=3, to_y=1, with_card=game.blue_hand[0])

def test_move_red_validation__should_be_successful():
    card = Card('TestCard', [(1, 1), (-1, 0), (1, 0)], color='red')
    cards = [card] * 5
    game = OnitamaGame(cards=cards)
    game.play_card(from_x=2, from_y=4, to_x=1, to_y=3, with_card=game.red_hand[0])



