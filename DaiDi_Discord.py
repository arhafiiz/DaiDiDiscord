'''
Class for player and the game
Functions generally return True for 'successful' runs and False otherwise

When possible functions both print status text to console and return status text as output

How to play: https://www.pagat.com/climbing/bigtwo.html
Note: for the hands A2345 and 23456, the A and the 2 are considered "small"
2AKQJ is not considered a valid hand
'''

from random import shuffle
from collections import Counter
from itertools import product


# Class of player
class Player:
    def __init__(self, nickname="", discord_name="", discord_id=0):
        self.nickname = nickname
        self.discord_name = discord_name # Discord name and id are not necessary
        self.discord_id = discord_id # Only used by discord bot
        self.hand = []
        self.diamonds = []
        self.clubs = []
        self.hearts = []
        self.spades = []


    # Function to return the value of a card
    # Follows the convention of Dai Di (2 being the highest value )
    def card_value(self, card):
        suit = ["D", "C", "H", "S"].index(card[0])
        num = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"].index(card[1])

        return 10*num + suit


    # Function to sort hands according to value
    # Also fills in the suited lists
    def sort_hand(self):
        if self.hand == []:
            return False

        self.hand.sort(key=self.card_value)

        self.diamonds = [card for card in self.hand if card[0] == 'D']
        self.clubs = [card for card in self.hand if card[0] == 'C']
        self.hearts = [card for card in self.hand if card[0] == 'H']
        self.spades = [card for card in self.hand if card[0] == 'S']

        self.hand.sort(key=self.card_value)
        return True


    # Function to check if hand is playable
    def can_play(self, cards=None):
        if self.hand == []: # First checks if hand is empty
            print("No cards to play")
            return (False, "No cards to play")

        elif len(cards) > 5: # Checks if tried to play more than five cards
            print("You can only play five cards or less")
            return (False, "You can only play five cards or less")
        
        elif len(cards) > len(set(cards)):
            print("You cannot play duplicate cards")
            return (False, "You cannot play duplicate cards")

        else:
            # Checks if cards played belong to hand
            cards_check = sum(map(lambda x: int(x in self.hand), cards))
            cards_len = len(cards)

            if cards_check == cards_len:
                return (True, f"Played the cards: {cards}")

            else:
                print(f"You don't have these cards:\n{[card for card in cards if card not in self.hand]}")
                return (False, f"You don't have these cards:\n{[card for card in cards if card not in self.hand]}")


    # Plays the card and returns card(s) if card(s) is in hand
    # Played card(s) removed from hand
    def play_card(self, cards=None):
        # First checks if card(s) can be played
        cards_status = self.can_play(cards)

        if cards_status[0] == True:
            for card in cards:
                self.hand.remove(card) # Removes cards from hand

            self.sort_hand() # Resorts hand
        return (True, cards_status[1]) # Status text is returned


# Class of Game
class Dai_Di:
    def __init__(self, player_list=None):
        self.suits = ["D", "C", "H", "S"]
        self.number = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
        self.deck_list = list(product(self.suits, self.number))
        self.play_area = []
        if isinstance(player_list, (list,)):
            self.players = player_list
        else:
            self.players = []


    # Prints out deck
    def show_deck(self):
        for i in self.deck_list:
            print(i)


    # Shuffles deck
    def shuffle_deck(self):
        shuffle(self.deck_list)

        # Checks if one player has 3 or more '2' cards
        # If so, reshuffles deck
        for i in range(4):
            if len([card[1] if card[1] == '2' else None for card in self.deck_list[i::4]]) > 2:
                shuffle(self.deck_list)

        return self.deck_list


    # Returns index of suit or number
    def index_func(self, string, small_aces=False):
        # Checks if string is in suits
        if string in self.suits:
            return self.suits.index(string)

        # Checks if string is in number
        elif string in self.number:
            if small_aces and string in ['A', '2']:
                return ['0', 'A', '2'].index(string)
            return self.number.index(string)

        else:
            return False


    # Returns the starting player i.e. the player with the Diamond 3 (D, 3) card
    def starting_player(self):
        for plyr in self.players:
            if ('D', '3') in plyr.hand:
                return self.players.index(plyr)

        return False


    # Deals cards to players and sorts their hands
    # Does nothing if there isn"t four players
    def deal_cards(self):
        if len(self.players) == 4:

            self.players[0].hand = self.deck_list[0::4]
            self.players[1].hand = self.deck_list[1::4]
            self.players[2].hand = self.deck_list[2::4]
            self.players[3].hand = self.deck_list[3::4]
            self.deck_list = []

            self.players[0].sort_hand()
            self.players[1].sort_hand()
            self.players[2].sort_hand()
            self.players[3].sort_hand()

            print(f"""Player 1: {self.players[0].hand}\n\n
Player 2: {self.players[1].hand}\n\n
Player 3: {self.players[2].hand}\n\n
Player 4: {self.players[3].hand}\n\n""")
            return True

        else:
            print("You need 4 players.")
            return False


    # Assigns values to differentiate cards
    # Outputs the same value as the Player.card_value function
    def card_value(self, card):
        suit = self.index_func(card[0])
        num = self.index_func(card[1])

        return 10*num + suit


    # Function to check if cards form a straight
    def isstraight(self, lst):
        # Checks if list can be sorted
        try:
            lst.sort(key=self.card_value)

        except ValueError:
            print("Select correct card(s)")
            return False

        # List of index of the cards' numbers
        lst = [self.index_func(card[1]) for card in lst]
        lst.sort()
        # Range from the lowest number to the highest number
        checker = list(range(lst[0], lst[-1] + 1))

        return lst == checker


    # Function to check type of hand
    # Only checks for hand type, whether hand is playable or not is checked seperately
    # Order of input does not affect result
    def hand_type(self, cards=None):
        length = len(cards) # Number of cards being played
        number_checker = len({card[1] for card in cards}) # The set of unique card number
        suit_checker = len({card[0] for card in cards}) # The set of unique card suits
        cards.sort(key=self.card_value)

        # The hands are ranked as:
        # Single, pair, three of a kind, straight, flush, full house, four of a kind, straight flush
        # Royal flushes are not significantly different from other straight flushes but they are still highlighted
        # [J, Q, K, A, 2] and [2, 3, 4, 5, 6] are NOT counted as proper Straights

        if length == 0:
            txt_blurb = "No cards played"
            return (False, txt_blurb)

        elif length == 1:
            txt_blurb = f"played the Single Card: {cards[0]}"
            return (1, txt_blurb)

        elif length == 2:

            if number_checker == 1 and suit_checker == 2: # 1 unique card number and 2 unique suits
                txt_blurb = f"played the Pair: {cards[0]} {cards[1]}"
                return (2, txt_blurb)

            else:
                txt_blurb = "That is not a pair"
                return (False, txt_blurb)

        elif length == 3:

            if number_checker == 1 and suit_checker == 3: # 1 unique card number and 3 unique suits
                txt_blurb = f"played the Three of a Kind: {cards[0]}, {cards[1]} {cards[2]}"
                return (3, txt_blurb)

            else:
                txt_blurb = "That is not a Three of a Kind"
                return (False, txt_blurb)

        elif length == 5:
            card_numbers = [card[1] for card in cards] # Only need the number of the cards to determine the hand type

            # Checks if cards form a "proper" straight
            if (self.isstraight(cards) and
                card_numbers != ["J", "Q", "K", "A", "2"]):

                # Checks if cards form a Royal Flush
                # Checks for the appropriate card numbers and if cards are of only one suit
                if (card_numbers == ["10", "J", "Q", "K", "A"]
                    and len(set([card[0] for card in cards])) == 1):
                    txt_blurb = f"played the Royal Flush: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"

                    # The digit in output is used to check if current hand beats previous hand
                    return (9, txt_blurb)

                # Checks if straight cards only have one suit (Straight Flush)
                elif suit_checker == 1:
                    txt_blurb = f"played the Straight Flush: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"
                    return (8, txt_blurb)

                # Otherwise cards form a normal Straight
                else:
                    txt_blurb = f"played the Straight: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"
                    return (4, txt_blurb)

            else: # Cards do not form a "proper" Straight
                if suit_checker == 1: # Checks if cards form a Flush
                    txt_blurb = f"played the Flush: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"
                    return (5, txt_blurb)

                # Move on to check more 'unusual' hands
                # Cards have at 2 unique numbers
                elif number_checker == 2:
                    cards_content = Counter([card[1] for card in cards]) # Counts number of cards with the same number
                    cards_counter = list(cards_content.items()) # Converts counter into list
                    cards_checker = {ind[1] for ind in cards_counter} # Set of count values

                    if cards_checker == {2, 3}: # 1 Pair + 1 Three of a Kind
                        txt_blurb = f"played the Full House: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"
                        return (6, txt_blurb)

                    elif cards_checker == {1, 4}: # Four of a Kind + 1 Kicker
                        txt_blurb = f"played the Four of a Kind: {cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]}"
                        return (7, txt_blurb)

                    else: # Cards don't form a Full House or a Four of a Kind
                        txt_blurb = "Invalid combination of cards"
                        return (False, txt_blurb)

                else: # Cards are not one of the five five-card combinations
                    txt_blurb = "Invalid combination of cards"
                    return (False, txt_blurb)

        else: # Tried to play more than five cards
            txt_blurb = "Invalid combination of cards"
            return (False, txt_blurb)


    # Function to check if current played hand is valid
    def can_play(self, player=Player(), cards=None, skip_turn=False):
        turn = len(self.play_area)

        # Checks if player wants to skip turn
        if skip_turn:
            # Cannot skip turn if you are the first to play
            if len(self.play_area) == 0:
                return (False, 'You cannot pass, you must play a card to start')

            # Cannot skip turn if everyone else has skipped their turns and you were the last person to play
            elif player.nickname == self.play_area[-1][1]:
                return (False, 'You cannot pass, you must play a card')

            # Skips turn
            print("Skipped turn")
            return (True, "Skipped turn")

        elif cards == []:
            print("Please select cards to play.")
            return (False, "Please select cards to play.")

        # Checks if cards form a valid hand
        elif self.hand_type(cards)[0] is False:
            print("Please play a valid hand")
            return (False, "Please play a valid hand")

        # Start of the game
        if turn == 0:
            if ("D", "3") in cards: # Diamond 3 must be played first

                if player.can_play(cards)[0] is False: # Checks if cards can be played
                    return (False, player.can_play(cards)[1]) # Outputs status text

                # Appends relevant information to the play_area
                play_type = self.hand_type(cards)
                self.play_area.append((cards, player.nickname, play_type))

                print(f"{player.nickname} {play_type[1]}")
                return (True, f"{player.nickname} {play_type[1]}")

            else:
                print("You must play the Diamond 3 at the start")
                return (False, "You must play the Diamond 3 at the start")

        # Checks if current player and last player is the same
        # If true, any valid hand is playable
        elif self.play_area[-1][1] == player.nickname:

            if player.can_play(cards)[0] is False:
                return (False, player.can_play(cards)[1])

            # Appends relevant information to the play_area
            current_play_type = self.hand_type(cards)
            self.play_area.append((cards, player.nickname, current_play_type))
            print(f"{player.nickname} {current_play_type[1]}")

            return (True, f"{player.nickname} {current_play_type[1]}")


        else:
            # Has seperate cases for the hands A2345 and 23456#
            # Type, suits and numbers of the cards in the current hand
            current_play_type = self.hand_type(cards)
            current_suits = [self.index_func(card[0]) for card in cards]
            if ({card[1] for card in cards} == {'A', '2', '3', '4', '5'}
                or {card[1] for card in cards} == {'2', '3', '4', '5', '6'}):

                current_numbers = [self.index_func(card[1], small_aces=True) for card in cards]

            else:
                current_numbers = [self.index_func(card[1]) for card in cards]

            # Type, suits and numbers of the cards in the last played hand
            previous_play_type = self.play_area[-1][2]
            previous_suits = [self.index_func(card[0]) for card in self.play_area[-1][0]]
            if ({card[1] for card in self.play_area[-1][0]} == {'A', '2', '3', '4', '5'}
                or {card[1] for card in cards} == {'2', '3', '4', '5', '6'}):

                current_numbers = [self.index_func(card[1], small_aces=True) for card in self.play_area[-1][0]]

            else:
                previous_numbers = [self.index_func(card[1]) for card in self.play_area[-1][0]]

            # Checks if last played hand is a five-card combination
            if previous_play_type[0] > 3:
                # Checks if current hand beats last played hand
                if current_play_type[0] > previous_play_type[0]:
                    # Checks if currnet hand is playable
                    if player.can_play(cards)[0] is False:
                        return (False, player.can_play(cards)[1])

                    # Appends relevant information to the play_area
                    self.play_area.append((cards, player.nickname, current_play_type))
                    print(f"{player.nickname} {current_play_type[1]}")

                    return (True, f"{player.nickname} {current_play_type[1]}")

                # Straight, flush and straight flush superiority is calculated using standard number then suit
                # Comparing numers is bypassed for Royal Flushes

                # Checks if current play type and last played type are the same
                # Focuses on hand types where 'highest card wins'
                elif (current_play_type[0] == previous_play_type[0] and
                      current_play_type[0] in [4, 5, 8, 9]):

                    # For Royal Flushes only checking suits is necessary
                    if (current_play_type[0] == 9 and
                        max(current_suits) > max(previous_suits)):

                        if player.can_play(cards)[0] is False:
                            return (False, player.can_play(cards)[1])

                        # Appends relevant information to the play_area
                        self.play_area.append((cards, player.nickname, current_play_type))
                        print(f"{player.nickname} {current_play_type[1]}")

                        return (True, f"{player.nickname} {current_play_type[1]}")

                    # Checks if current highest card is higher than last played highest card
                    elif max(current_numbers) > max(previous_numbers):

                        if player.can_play(cards)[0] is False:
                            return (False, player.can_play(cards)[1])

                        # Appends relevant information to the play_area
                        self.play_area.append((cards, player.nickname, current_play_type))
                        print(f"{player.nickname} {current_play_type[1]}")

                        return (True, f"{player.nickname} {current_play_type[1]}")

                    # In case the highest cards are equal, check suits instead
                    elif (max(current_numbers) == max(previous_numbers) and
                        max(current_suits) > max(previous_suits)):

                        if player.can_play(cards)[0] is False:
                            return (False, player.can_play(cards)[1])

                        # Appends relevant information to the play_area
                        self.play_area.append((cards, player.nickname, current_play_type))
                        print(f"{player.nickname} {current_play_type[1]}")

                        return (True, f"{player.nickname} {current_play_type[1]}")

                    else:
                        print(f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

                        return (False, f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

                # Checking Full Houses or Four of a Kinds
                elif (current_play_type[0] == previous_play_type[0] and
                    current_play_type[0] in [6, 7]):
                    previous_cards = self.play_area[-1][0]

                    # Looks for the 'main body' and the 'kicker' of the current hand
                    current_main = [card for card in cards if card[1] == cards[0][1]]
                    current_kicker = [card for card in cards if card[1] == cards[-1][1]]

                    # Looks for the 'main body' and the 'kicker' of the last played hand
                    previous_main = [card for card in previous_cards if card[1] == previous_cards[0][1]]
                    previous_kicker = [card for card in previous_cards if card[1] == previous_cards[0][1]]

                    # If 'kicker' is longer than the 'main body', swap the two
                    if len(current_kicker) > len(current_main):
                        current_main = [card for card in cards if card[1] == cards[-1][1]]
                        del current_kicker

                    if len(previous_kicker) > len(previous_main):
                        previous_main = [card for card in self.play_area[-1][0] if card[1] == self.play_area[-1][0][-1][1]]
                        del previous_kicker

                    # Comparing the number of the current and last played 'main bodies'
                    current_main_numbers = self.index_func(current_main[0])
                    previous_main_numbers = self.index_func(current_main[0])

                    if current_main_numbers > previous_main_numbers:

                        if player.can_play(cards)[0] is False:
                            return (False, player.can_play(cards)[1])

                        # Appends relevant information to the play_area
                        self.play_area.append((cards, player.nickname, current_play_type))
                        print(f"{player.nickname} {current_play_type[1]}")

                        return (True, f"{player.nickname} {current_play_type[1]}")

                    else:
                        print(f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

                        return (False, f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

            # Dealing with the case of Single Cards, Pairs and Triples
            elif (previous_play_type[0] <= 3 and 
                  current_play_type[0] == previous_play_type[0]):

                # Number of current hand is higher than the number of the last played hand
                if max(current_numbers) > max(previous_numbers):

                    if player.can_play(cards)[0] is False:
                        return (False, player.can_play(cards)[1])

                    # Appends relevant information to the play_area
                    self.play_area.append((cards, player.nickname, current_play_type))
                    print(f"{player.nickname} {current_play_type[1]}")

                    return (True, f"{player.nickname} {current_play_type[1]}")

                # If numbers are equal, check suits instead
                elif (max(current_numbers) == max(previous_numbers) and
                      max(current_suits) > max(previous_suits)):

                    if player.can_play(cards)[0] is False:
                        return (False, player.can_play(cards)[1])

                    # Appends relevant information to the play_area
                    self.play_area.append((cards, player.nickname, current_play_type))
                    print(f"{player.nickname} {current_play_type[1]}")

                    return (True, f"{player.nickname} {current_play_type[1]}")

                else:
                    print(f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

                    return (False, f"{current_play_type[1][11:]} does not beat {previous_play_type[1][11:]}")

            else:
                return (False, "Invalid hand")
