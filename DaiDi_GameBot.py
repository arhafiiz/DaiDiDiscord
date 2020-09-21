'''
Backend GameBot functions
'''

# Framework for testing simple gameplaying bots
from DaiDi_Discord_Silent import Player, Dai_Di

# Function to return the value of a card
def card_value(card):
    suit = ["D", "C", "H", "S"].index(card[0])
    num = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"].index(card[1])
    return 10 * num + suit


# Function used to simulate a game of Dai Di
# Returns the list of players, the card_cost, the action_cost and the total_cost
# card_cost is the sum of the values of the cards remaining in a player's hand at the end of a game
# action_cost is the total cost of all the actions taken by a bot
# total_cost is the sum of the card_cost and action_cost
def game_function(play_lst, objective_fn={'play': 1, 'pass': 1, 'invalid': 1}, audible=0):
    '''
    play_lst is a list of functions that play the game
    functions outputs must output a list of valid cards and a list containing the string 'pass'

    objective_fn is a triple where the values represent the cost of a particular action
    i.e. cost_of_playing_a_hand, cost_of_skipping_turn, costof playing an invalid hand

    audible is used to select if status text is printed in the console or not
    > 0 for output and none otherwise
    '''
    # Setup variables
    cards = ([(i, j) for i in ["D", "C", "H", "S"]
              for j in ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]])

    # Game setup
    # Uses the name of the function instead of a custom name
    play_len = len(play_lst)
    p_1 = Player(nickname=play_lst[0 % play_len].__name__ + '1')
    p_2 = Player(nickname=play_lst[1 % play_len].__name__ + '2')
    p_3 = Player(nickname=play_lst[2 % play_len].__name__ + '3')
    p_4 = Player(nickname=play_lst[3 % play_len].__name__ + '4')
    Game = Dai_Di([p_1, p_2, p_3, p_4])

    # Starting game
    player_strengths = [sum(map(Game.card_value, Game.deck_list[i::4])) for i in range(4)]

    while min(player_strengths) < 650 or max(player_strengths) > 900:
        Game.shuffle_deck()
        player_strengths = [sum(map(Game.card_value, Game.deck_list[i::4])) for i in range(4)]

    Game.deal_cards()
    starter_player = Game.starting_player()
    play_order = Game.players[starter_player:] + Game.players[:starter_player]
    turn = 0

    # Playing game
    while True:
        current_player = play_order[turn]
        cards_left = len(current_player.hand)

        action = play_lst[(turn) % play_len](current_player, Game.play_area)

        if len(Game.play_area) == 0 and [('D', '3')] not in action:
            action = [('D', '3')]
            current_player.discord_id += objective_fn['play']

        if action == ['pass']:
            if Game.can_play(current_player, skip_turn=True)[0]:
            
                Game.can_play(current_player, [], skip_turn=True)
                turn = (turn + 1) % 4
                current_player.discord_id += objective_fn['pass']
    
                if audible > 0:
                    print(f'{current_player.nickname} passed')
            
            else:
                if audible > 0:
                    print(f'{current_player.nickname} failed to pass')

        elif isinstance(action, list):
            hand = [card for card in action if card in cards]
            game_success = Game.can_play(current_player, hand)
            player_success = current_player.can_play(action)

            if not game_success[0]:
                current_player.discord_id += objective_fn['invalid']

            elif not player_success[0]:
                current_player.discord_id += objective_fn['invalid']

            else:
                current_player.play_card(action)
                turn = (turn + 1) % 4
                current_player.discord_id += objective_fn['play']
                
                if audible > 0:
                    print(f'{current_player.nickname} played {action}: {cards_left}')
                
                if len(current_player.hand) == 0:
                    card_cost = [sum(map(Game.card_value, Game.players[i].hand)) for i in range(4)]
                    action_cost = [Game.players[i].discord_id for i in range(4)]
                    total_cost = [sum(values) for values in zip(*(card_cost, action_cost))]
                    
                    if audible > 0:
                        print('End')

                    break
    
    return ([player.nickname for player in play_order], card_cost, action_cost, total_cost)


# Function to check if hand is valid
import numpy as np
Game = Dai_Di()

def is_valid(hand):
    while None in hand:
        hand.remove(None)
    # Returns bool value of whether hand is valid or not
    return Game.hand_type(hand)

playing_cards = [(i, j) for i in ["D", "C", "H", "S"]
                 for j in ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]]

# Function to create dummy variable
# Also adds is_valid bool value at the end
def card_dummy(hand):
    hand = list(hand)
    while None in hand:
        hand.remove(None)
    dummies = np.zeros(53)
    for card in hand:
        dummies[playing_cards.index(card)] = 1
    dummies[52] = is_valid(hand)[0] > 0
    return dummies


# Checks if hand1 beats hand2
# Returns False when the hands are different types
# Returns False when the hands share cards in common
def hand_compare(hand1, hand2):
    if not set.isdisjoint(set(hand1), set(hand2)):
        return False
    
    current_play_type = Game.hand_type(hand1)
    current_suits = [Game.index_func(card[0]) for card in hand1]
    if ({card[1] for card in hand1} == {'A', '2', '3', '4', '5'}
        or {card[1] for card in hand1} == {'2', '3', '4', '5', '6'}):

        current_numbers = [Game.index_func(card[1], small_aces=True) for card in hand1]

    else:
        current_numbers = [Game.index_func(card[1]) for card in hand1]

    previous_play_type = Game.hand_type(hand2)
    previous_suits = [Game.index_func(card[0]) for card in hand2]
    if ({card[1] for card in hand2} == {'A', '2', '3', '4', '5'}
        or {card[1] for card in hand1} == {'2', '3', '4', '5', '6'}):

        previous_numbers = [Game.index_func(card[1], small_aces=True) for card in hand2]

    else:
        previous_numbers = [Game.index_func(card[1]) for card in hand2]

    if previous_play_type[0] > 3:
        if current_play_type[0] > previous_play_type[0]:
            return True

        elif (current_play_type[0] == previous_play_type[0] and
              current_play_type[0] in [4, 5, 8, 9]):

            if (current_play_type[0] == 9 and
                max(current_suits) > max(previous_suits)):
                return True

            elif max(current_numbers) > max(previous_numbers):
                return True

            elif (max(current_numbers) == max(previous_numbers) and
                max(current_suits) > max(previous_suits)):
                return True

            return False

        elif (current_play_type[0] == previous_play_type[0] and
            current_play_type[0] in [6, 7]):

            current_main = [card for card in hand1 if card[1] == hand1[0][1]]
            current_kicker = [card for card in hand1 if card[1] == hand1[-1][1]]

            previous_main = [card for card in hand2 if card[1] == hand2[0][1]]
            previous_kicker = [card for card in hand2 if card[1] == hand2[0][1]]

            if len(current_kicker) > len(current_main):
                current_main = [card for card in hand1 if card[1] == hand1[-1][1]]

            if len(previous_kicker) > len(previous_main):
                previous_main = [card for card in hand2 if card[1] == hand2[-1][1]]

            current_main_numbers = Game.index_func(current_main[0])
            previous_main_numbers = Game.index_func(current_main[0])

            if current_main_numbers > previous_main_numbers:
                return True

            else:
                return False

    elif (previous_play_type[0] <= 3 and 
          current_play_type[0] == previous_play_type[0]):

        if max(current_numbers) > max(previous_numbers):
            return True

        elif (max(current_numbers) == max(previous_numbers) and
              max(current_suits) > max(previous_suits)):
            return True

        else:
            return False
    
    return False


# Function to display all valid hands given a player's current hand
# The function is used a brute force method to generate all possible hands since there is only 1664
# possible combinations
from itertools import combinations
def possible(lst):
    all_comb = [list(card) for i in [1, 2, 3, 5] for card in combinations(lst, r=i)]
    valid_comb = [card for card in all_comb if is_valid(card)[0] > 0]
    pair = [card for card in valid_comb if len(card) == 2]
    triple = [card for card in valid_comb if len(card) == 3]
    fives = [card for card in valid_comb if len(card) == 5]
    
    return (lst, pair, triple, fives)
