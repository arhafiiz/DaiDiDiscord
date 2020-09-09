'''
Attempting to make a neural network than can play a game of Dai Di
'''

# Framework for testing simple gameplaying bots
from random import sample, randint
from collections import Counter
from DaiDi_Discord_Silent import Player, Dai_Di


def card_value(card):
    suit = ["D", "C", "H", "S"].index(card[0])
    num = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"].index(card[1])
    return 10 * num + suit


def game_function(play_lst, objective_fn=(1,1,1), audible=0):
    '''
    play_lst is a list of functions that play the game
    functions outputs must output a list of valid cards and a list containing the string 'pass'

    objective_fn is a triple where the values represent the cost of an action
    i.e. (cost_of_playing_a_hand, cost_of_skipping_turn, costof playing an invalid hand)

    audible is used to select if status text is printed in the console or not
    > 0 for output and none otherwise
    '''
    # Setup variables
    cards = ([(i, j) for i in ["D", "C", "H", "S"]
              for j in ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]])

    # Game setup
    play_len = len(play_lst)
    p_1 = Player(nickname=play_lst[0 % play_len].__name__)
    p_2 = Player(nickname=play_lst[1 % play_len].__name__)
    p_3 = Player(nickname=play_lst[2 % play_len].__name__)
    p_4 = Player(nickname=play_lst[3 % play_len].__name__)
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
            current_player.discord_id += objective_fn[0]

        if action == ['pass']:
            if Game.can_play(current_player, skip_turn=True)[0]:
            
                Game.can_play(current_player, [], skip_turn=True)
                turn = (turn + 1) % 4
                current_player.discord_id += objective_fn[1]
    
                if audible > 0:
                    print(f'{current_player.nickname} passed')
            
            else:
                if audible > 0:
                    print(f'{current_player.nickname} failed to pass')

        elif isinstance(action, list):
            hand = [card for card in action if card in cards]
            game_success = Game.can_play(current_player, hand)
            player_success = current_player.can_play()

            if not game_success[0]:
                current_player.discord_id += objective_fn[2]

            elif not player_success[0]:
                current_player.discord_id += objective_fn[2]

            else:
                current_player.play_card(action)
                turn = (turn + 1) % 4
                current_player.discord_id += objective_fn[0]
                
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


# A bot that randomly selects one cards or passes
def random_play(player=Player(), history=[]):
    if randint(0, 1):
        return sample(player.hand, 1)

    return ['pass']

random_winner = []
for i in range(10000):
    if i % 500 == 0:
        print('#', end='')
    random_winner.append(game_function([random_play]))


position_random_win_count = dict(Counter([winner[1].index(0) for winner in random_winner]))
'''
Percent of wins with respect to turn:
First = 100%, Second, Third, Fourth = 0%
It seems that the player that starts first has a huge advantage
'''

# Visually plays a game with random bot
game_function([random_play], audible=1)


# A bot that selects a single random card that beats the last played card
# If it cannot, it passes
def stronger_play(player=Player(), history=[]):
    if not history:
        prev_str = 0
        stronger_card = player.hand
        return sample(stronger_card, 1)

    else:
        prev_str = card_value(history[-1][0][0])

        if history[-1][1] == player.nickname:
            stronger_card = player.hand
        
        else:
            hand_str = [(card, card_value(card)) for card in player.hand]
            stronger_card = [card[0] for card in hand_str if card[1] > prev_str]
    
            if not stronger_card:
                return ['pass']
    
    return sample(stronger_card, 1)

stronger_winner = []
for i in range(10000):
    if i % 500 == 0:
        print('#', end='')
    stronger_winner.append(game_function([stronger_play]))

position_stronger_win_count = dict(Counter([winner[1].index(0) for winner in stronger_winner]))
'''
Percent of wins with respect to turn:
First = 100%, Second, Third, Fourth = 0%
It seems that the player that starts first has a huge advantage
'''
# Visually plays a game with stronger_bot
game_function([random_play, stronger_play], audible=1)


# random_bot vs stronger_bot comparison
random_first = []
stronger_first = []
for i in range(10000):
    if (i+1) % 500 == 0:
        print('#', end='')
    random_first.append(game_function([random_play, stronger_play]))
    stronger_first.append(game_function([stronger_play, random_play]))

rand_first_bot_win_count = dict(Counter([winner[0][winner[1].index(0)] for winner in random_first]))
rand_first_position_win_count = dict(Counter([winner[1].index(0) for winner in random_first]))
'''
Head to head test where random_bot starts first 
Bot turns goes [random_bot, stronger_bot, random_bot, stronger_bot]

Winner by bot:
    stronger_bot: 97.82%, random_bot: 2.18%

Winner by position: 
    First: 60.35%, Second: 1.63%, Third 37.47%, Fourth: 0.55%
'''

strong_first_bot_win_count = dict(Counter([winner[0][winner[1].index(0)] for winner in stronger_first]))
strong_first_position_win_count = dict(Counter([winner[1].index(0) for winner in stronger_first]))
'''
Head to head test where stronger_bot starts first 
Bot turns goes [stronger_bot, random_bot, stronger_bot, random_bot]

Winner by bot:
    stronger_bot: 99.78%, random_bot: 0.22%

Winner by position: 
    First: 65.71%, Second: 0.11%, Third 34.07%, Fourth: 0.11%

Summary:
random_bot seems to do better when it goes first (although it still gets overwhelmed by stronger_bot)
'''

#==========================================================================================================


'''
Simple Neural Network to check if hand is valid

Next attempt: Try to use stratified random sampling based on the number of cards in hand
              Otherwise data is skewed towards invalid 5-card hands
'''

import numpy as np
import pandas as pd

# Creating suitable dataset
Game = Dai_Di()

def is_valid(hand):
    # Returns bool value of whether hand is valid or not
    return Game.hand_type(hand)

playing_cards = [(i, j) for i in ["D", "C", "H", "S"]
                 for j in ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]]

# Function to create dummy variable
# Also adds is_valid bool value at the end
def card_dummy(hand):
    dummies = np.zeros(53)
    for card in hand:
        dummies[playing_cards.index(card)] = 1
    dummies[52] = is_valid(hand)[0] > 0
    return dummies

from itertools import combinations
from random import seed
from sklearn.model_selection import train_test_split


# There are only a finite and relatively small number of valid poker hands, so we can list them all here
all_card_combinations = [list(card) for i in range(1, 6) for card in combinations(playing_cards, r=i)]
valid_hands = [card for card in all_card_combinations if is_valid(card)[0] > 0]
invalid_hands = [card for card in all_card_combinations if not is_valid(card)[0]]


len(valid_hands)*5 # We will undersample the invalid hands to obtain a 1:5 ratio of valid to invalid hands
valid_dummies = list(map(card_dummy, valid_hands))
invalid_dummies = list(map(card_dummy, invalid_hands))

seed(32142698) # to keep data samples consistent
cards_data = valid_dummies + sample(invalid_dummies, k=89290)
card_df = pd.DataFrame(data=cards_data, columns=(playing_cards + ['is_valid']))

# Use a 75:12.5:12.5 train:test:validate data ratio
x, y = card_df.iloc[:,:-1], card_df.iloc[:,-1]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=912032)
x_test, x_validate, y_test, y_validate = train_test_split(x, y, test_size=0.5, random_state=6510123)

# Creating NN
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

inputs = keras.Input(shape=(52,))

dense = layers.Dense(64, activation='relu')
x = dense(inputs)
x = layers.Dense(64, activation='relu')(x)
x = layers.Dense(64, activation='relu')(x)
x = layers.Dense(64, activation='relu')(x)
outputs = layers.Dense(1)(x)

model = keras.Model(inputs=inputs, outputs=outputs, name='valid_hands')
model.summary()

# Model will use Binary Cross entropy loss metric and Binary Accuracy metric since the problem is Binary Classification
model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=False, label_smoothing=0,
                                            reduction="auto", name="binary_crossentropy"),
    optimizer=keras.optimizers.RMSprop(),
    metrics=['BinaryAccuracy'],
)

history = model.fit(
    x_train, y_train,
    batch_size=64, epochs=5,
    validation_split=0, validation_data=(x_test, y_test))

test_scores = model.evaluate(x_test, y_test, verbose=2)
# Test loss: 0.11602626740932465
# Test accuracy: 0.9851980209350586

model.save('E:\Programming\Python\ANN\Models\Valid_Hand_Checker')
del model

model = keras.models.load_model('E:\Programming\Python\ANN\Models\Valid_Hand_Checker')

# Confusion matrix
from sklearn.metrics import confusion_matrix

def accuracy_fn(ann_model, validate_data):
    predicted_y = list(map(lambda x: x > 0, ann_model.predict(validate_data)))
    predicted_y = [pred[0] for pred in predicted_y]

    err_mat = confusion_matrix(y_true=y_validate, y_pred=predicted_y, labels=[1, 0])
    tp, fp, fn, tn  = err_mat.ravel()

    accuracy = (tp + tn)/(tp + tn + fp+ fn)
    tp_rate =  tp/(tp + fn)
    tn_rate = tn/(tn + fp)
    precision = tp/(tp + fp)
    
    print(f'''Accuracy:\t\t\t{accuracy}\nTrue Positive Rate: {tp_rate}\nTrue Negative Rate: {tn_rate}\nPrecision:\t\t\t{precision}
Confusion Matrix:\n{err_mat}''')
    return (err_mat, accuracy, tp_rate, tn_rate, precision)

err_mat, accuracy, tp_rate, tn_rate, precision = accuracy_fn(model, x_validate)

# High accuracy (96.59%), very high true negative rate and precision (99.92%, 99.96%)
# Acceptable true positive rate (83.19%)


'''
To do:
Simple neural network to check if first hand beats the second one

Criteria:
    1) Must return False if either of the hands are invalid hands
    2) Must return False if both hands are equal since this scenario is not possible during a game of Dai Di

Considerations:
    1) Huge number of paired hands possible (1,275,596,940 using all valid hands + equal number of invalid hands)
    2) How to handle different types of hands
        a) e.g. Flush obviously beats Pair but normally cannot be played after a Pair
        b) How to deal with reverse matchups. Are they worth running or can they be replaced with code?
            (i.e. does Straight vs Quads result renders Quads vs Straight result moot?)
'''



