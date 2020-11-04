from bots.tree_bot import DecisionTreeBot
from game.game import Card, OnitamaGame

import sys
sys.setrecursionlimit(1500)


def test__tree_generation__should_be_succeful():
    card = Card('TestCard', [(1, 1), (-1, 0), (1, 0)], color='blue')
    cards = [card] * 5
    game = OnitamaGame(cards=cards)
    bot = DecisionTreeBot(game_initial_state=game, player_color='blue')
    assert bot.current_state is not None
