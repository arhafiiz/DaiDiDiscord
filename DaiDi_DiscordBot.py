'''
Discord API for running Dai Di game
Also called Da Lao Er or Deuces

How to play: https://www.pagat.com/climbing/bigtwo.html
Note: for the hands A2345 and 23456, the A and the 2 are considered "small"
2AKQJ is not considered a valid hand
'''

# Dependencies
import json
from Big2 import Dai_Di, Player
from numpy import inf
from random import randint

# Discord authentication details and server ids
try:
    with open('auth.txt', 'r') as json_file:
        auth = json.load(json_file)

except FileNotFoundError:
    '''
    Fill in your discord server and discord bot details
    '''
    auth = {'client_id': fill with int, 'client_secret': fill with str, 'server_id': fill with int, 'token': fill with str}
    with open('auth.txt', 'w') as json_file:
        json.dump(auth, json_file)

try:
    with open('elo.txt', 'r') as elo_file:
        all_elo = json.load(elo_file)

except FileNotFoundError:
    '''
    Entries are based on the discord id of players, so elo is not reset when changing names
    '''
    player_data = {'player_name': 10000}
    with open('elo.txt', 'w') as elo_file:
        json.dump(player_data, elo_file)
    
    with open('elo.txt', 'r') as elo_file:
        all_elo = json.load(elo_file)

# Discord channels where game is played/tested
discord_channels = {'game_channel': channel ids here,'test_channel': channel ids here}


# String of name of the game admin role
# Admins can reset onging games and kill the bot
# Is case sensitive
admin_tier = {'Admin',}

# Game object and misc details
Game = {'game': Dai_Di(), 'ongoing': (False, False), 'order': [], 'turn': 0}
delimiter_string = '\_' * 20

# Bot code body
import discord

client = discord.Client()

# Checks if bot is ready
@client.event
async def on_ready():
    print('All clear')


@client.event
async def on_message(message):
    global Game, all_elo
    
    # Command to force logout the bot
    # Only users with tiernames in admin_tier set can use this command
    if message.content.lower() == '!stop' and list(admin_tier & Tier(message.author)): 
        
        with open('elo.txt', 'w') as outfile:
            json.dump(all_elo, outfile)
        
        await message.channel.send('I go to sleep now :sleepy:')
        await client.logout()
    
    # Checks if message is in the appropriate discord channels
    if message.channel == client.get_channel(discord_channels['game_channel']) or message.channel == client.get_channel(discord_channels['test_channel']):
        if message.author == client.user: # Bot does not reply to itself
            return
        
        # Bot ignores vociferously verbose verbiage
        if len(message.content) > 100:
            return
        
        # Gets the tier of the user.
        tier = Tier(message.author)
        
        if message.content.lower().startswith() == '!gamesetup': # Setting up game
            
            # Cannot setup game if game is already setup and game is ongoing
            if Game['ongoing'] == (False, False):

                await message.channel.send('Loading game: Dai Di')
                Game['game'] = Dai_Di() # Sets up game
                Game['ongoing'] = (True, False) # Sets ongoing_game to true
                Game['order'] = [] # Sets up player order
                Game['turn'] = 0 # Sets game turn to 0
                
                # Shuffles deck
                Game['game'].shuffle_deck()
                
                await message.channel.send('Game loaded')
                await message.channel.send('Player lobby is open')
                return
            
            # Allows admins to reset the game and set up a new game
            # Can be done at any point, even during games
            # Try not to be a jerk
            elif (Game['ongoing'][0] ==  True and
                  list(admin_tier & tier)):
                
                await message.channel.send('Restarting game')
                Game['game'] = Dai_Di()
                Game['ongoing'] = (True, False)
                Game['order'] = []
                Game['turn'] = 0
                return
            
            # Non admin users cannot start new games
            else:
                await message.channel.send('There is a game in progress')
                return
        
        # Message to join game, the semicolon is necessary
        # Format is `!joingame; nickname`
        elif message.content.lower().startswith('!joingame'):
            if Game['ongoing'][0] == False:
                await message.channel.send('The game lobby has not opened')
                return
        
            discord_name = message.author
            discord_id = message.author.id
            nickname = ' '.join(message.content.split(';')[1:])
            
            elo_check = has_elo(discord_id, all_elo)
            
            # If the semicolon is left out user will be mocked
            if message.content.find(':') is None or nickname == '':
                if randint(0,999) == 0:
                    nickname = str(message.author)[:-5] + " can't follow instructions"
                else:
                    nickname = str(message.author)[:-5] + ' forgot about the semicolon'

            player_names = [player.discord_name for player in Game['game'].players]
            
            # Game can only be played by 4 people exactly
            if len(player_names) >= 4:
                await message.channel.send('The game is full')
                return
            
            # Players must be unique users
            if discord_name in player_names:
                await message.channel.send('You are already in the game')
                return

            # Adds players to game object and returns status text
            Game['game'].players.append(Player(f'{nickname}', f'{discord_name}', discord_id))
            await message.channel.send(f'{nickname} joined the game\n{nickname} {elo_check[1]}\n{nickname} has a rating of {elo_check[0]}')
            return
        
        # Message to start game
        elif message.content.lower().startswith('!startgame'):
            # Can't start a game with less than 4 players
            if len(Game['game'].players) < 4:
                await message.channel.send('You need 4 players to play')
                return
            
            # Checks if there is an available game
            elif Game['ongoing'][0] == False:
                await message.channel.send('You need to setup a game first')
            
            # Checks if there is an ongoing game
            elif Game['ongoing'][1] == True:
                await message.channel.send('There is an ongoing game')
                return
            
            # Balances hand
            # The shuffle_deck function already checks for unbalanced number of 2's
            # Average player hand should have a strength of 800 (799.5)
            # Uses a player strength range of 650 (-150) to 900 (+100)
            # Range is completely arbitrary, feel free to change values or remove altogether
            balance_message = await message.channel.send('Balancing hands')
            player_strengths = [sum(map(Game['game'].card_value, Game['game'].deck_list[i::4])) for i in range(4)]

            # Hand is reshuffled until all hands strength are within the set range
            while min(player_strengths) < 650 or max(player_strengths) > 900:
                Game['game'].shuffle_deck()
                player_strengths = [sum(map(Game['game'].card_value, Game['game'].deck_list[i::4])) for i in range(4)]
            
            
            await balance_message.edit(content='Balancing hands.')
            await balance_message.edit(content='Balancing hands..')
            await balance_message.edit(content='Balancing hands...')
            await balance_message.edit(content='Hands balanced')
            
            # Sets game status to ongoing, deals out cards and finds the starting player (player with diamond 3 card)
            Game['ongoing'] = (True, True)
            Game['game'].deal_cards()
            starter_player = Game['game'].starting_player()
            print(starter_player)

            play_order = (Game['game'].players[starter_player:] +
                          Game['game'].players[:starter_player])
            
            Game['order'] = play_order
            
            # Setting up player hand display
            # _suit_sorted displays the cards sorted by suits (left to right, diamond, clubs, hearts, spades)
            # The suit sorted cards are displayed in the same line to avoid revealing information on a player's hand
            player1_suit_sorted = play_order[0].diamonds + play_order[0].clubs + play_order[0].hearts + play_order[0].spades
            
            player1_hands_suit = f'{play_order[0].nickname}\'s Hand\nBy suits:\n||{player1_suit_sorted}||\n'
            player1_hands_normal = f'By value:\n||{play_order[0].hand}||\n{delimiter_string}'
            player1_all_hand = player1_hands_suit + player1_hands_normal
            
            player2_suit_sorted = play_order[1].diamonds + play_order[1].clubs + play_order[1].hearts + play_order[1].spades
            
            player2_hands_suit = f'{play_order[1].nickname}\'s Hand\nBy suits:\n||{player2_suit_sorted}||\n'
            player2_hands_normal = f'By value:\n||{play_order[1].hand}||\n{delimiter_string}'
            player2_all_hand = player2_hands_suit + player2_hands_normal


            player3_suit_sorted = play_order[2].diamonds + play_order[2].clubs + play_order[2].hearts + play_order[2].spades
            
            player3_hands_suit = f'{play_order[2].nickname}\'s Hand\nBy suits:\n||{player3_suit_sorted}||\n'
            player3_hands_normal = f'By value:\n||{play_order[2].hand}||\n{delimiter_string}'
            player3_all_hand = player3_hands_suit + player3_hands_normal

    
            player4_suit_sorted = play_order[3].diamonds + play_order[3].clubs + play_order[3].hearts + play_order[3].spades
            
            player4_hands_suit = f'{play_order[3].nickname}\'s Hand\nBy suits:\n||{player4_suit_sorted}||\n'
            player4_hands_normal = f'By value:\n||{play_order[3].hand}||\n{delimiter_string}'
            player4_all_hand = player4_hands_suit + player4_hands_normal
            
            await message.channel.send(f'The player order is {play_order[0].nickname}, {play_order[1].nickname}, {play_order[2].nickname}, {play_order[3].nickname}')

            await message.channel.send(player1_all_hand)
            await message.channel.send(player2_all_hand)
            await message.channel.send(player3_all_hand)
            await message.channel.send(player4_all_hand)
            await message.channel.send('No peeking :angry:')
            return
        
        # Message to play cards
        # Format is !playcard; card1, card2, card3, card4, card5
        # Again, semicolon and comma are necessary
        # Can can only be played when game is ongoing
        # Card format should be: suits, number
        # Number must be a number, don't type the number as words
        elif (message.content.lower().startswith('!playcard') and
              Game['ongoing'][1] == True):

            string = message.content.lower().split(';')
            cards = string[1]
            
            # Gets current game turn and current player
            game_turn = Game['turn']
            current_player = Game['order'][game_turn]
            
            # Checks if it is the message author's turn
            if str(message.author) != str(current_player.discord_name):
                await message.channel.send(f'It is{current_player.nickname}\'s turn')
                return
            
            # Converts text to cards for processing
            real_cards = text_to_cards(cards)
            print(real_cards)
            
            # Checks if cards form a valid hand and if player can play them
            game_success = Game['game'].can_play(current_player, real_cards)
            player_success = current_player.can_play(real_cards)

            if game_success[0] == False:
                await message.channel.send(f'{game_success[1]}')
                return
            
            elif player_success[0] == False:
                await message.channel.send(f'{player_success[1]}')
                return
            
            else:
                # Plays card and status text
                current_player.play_card(real_cards)
                print(f'text_to_cards: {real_cards}\ncurrent player: {current_player.nickname}\ntype of hand: {game_success[1]}')

                # Checks if player has any cards left in hand
                cards_left = len(current_player.hand)
                Game['turn'] = (Game['turn'] + 1) % 4

                # End of game
                # Announces winner, changes elo
                if cards_left == 0:
                    Game['ongoing'] = (False, False)
                    elo_string = ''
                    
                    for player in Game['game'].players:
                        if player.discord_id == message.author.id:
                            if all_elo[str(player.discord_id)] == float(inf):
                                elo_string += f'{player.nickname} is still a god :sunglasses:\n'
                            
                            else:
                                all_elo[str(player.discord_id)] = int(all_elo[str(player.discord_id)] * 1.2)
                                elo_string += f'{player.nickname} raised their elo to {all_elo[str(player.discord_id)]}\n'

                        else:
                            if all_elo[str(player.discord_id)] == float(inf):
                                elo_string += f'{player.nickname} was taking it easy :sunglasses:\n'

                            elif all_elo[str(player.discord_id)] <= 5:
                                all_elo[str(player.discord_id)] = 5
                                elo_string += f'{player.nickname}\'s elo is too small to change :cry:\n'

                            else:
                                all_elo[str(player.discord_id)] = int(all_elo[str(player.discord_id)] * 0.85)
                                elo_string += f'{player.nickname}\'s elo dropped to {all_elo[str(player.discord_id)]}\n'
                    
                    with open('elo.txt', 'w') as outfile:
                        json.dump(all_elo, outfile)
                    
                    await message.channel.send(f'{game_success[1]}\n{current_player.nickname} has won!\n{elo_string}')
                    return
               
                # Not end of game
                else:
                    new_current = Game['order'][(game_turn + 1) % 4]
                    await message.channel.send(f'{game_success[1]}\n{new_current.nickname} turn now')
                    return

            # Displays cards every four turns
            if Game['turn'] == 0:
                play_order = Game['order']
                
                player1_suit_sorted = play_order[0].diamonds + play_order[0].clubs + play_order[0].hearts + play_order[0].spades
                
                player1_hands_suit = f'{play_order[0].nickname}\'s Hand\nBy suits:\n||{player1_suit_sorted}||\n'
                player1_hands_normal = f'By value:\n||{play_order[0].hand}||\n{delimiter_string}'
                player1_all_hand = player1_hands_suit + player1_hands_normal
                
                player2_suit_sorted = play_order[1].diamonds + play_order[1].clubs + play_order[1].hearts + play_order[1].spades
                
                player2_hands_suit = f'{play_order[1].nickname}\'s Hand\nBy suits:\n||{player2_suit_sorted}||\n'
                player2_hands_normal = f'By value:\n||{play_order[1].hand}||\n{delimiter_string}'
                player2_all_hand = player2_hands_suit + player2_hands_normal
                
                player3_suit_sorted = play_order[2].diamonds + play_order[2].clubs + play_order[2].hearts + play_order[2].spades
                
                player3_hands_suit = f'{play_order[2].nickname}\'s Hand\nBy suits:\n||{player3_suit_sorted}||\n'
                player3_hands_normal = f'By value:\n||{play_order[2].hand}||\n{delimiter_string}'
                player3_all_hand = player3_hands_suit + player3_hands_normal
                
                player4_suit_sorted = play_order[3].diamonds + play_order[3].clubs + play_order[3].hearts + play_order[3].spades
                
                player4_hands_suit = f'{play_order[3].nickname}\'s Hand\nBy suits:\n||{player4_suit_sorted}||\n'
                player4_hands_normal = f'By value:\n||{play_order[3].hand}||\n{delimiter_string}'
                player4_all_hand = player4_hands_suit + player4_hands_normal
                
                await message.channel.send(f'The player order is {play_order[0].nickname}, {play_order[1].nickname}, {play_order[2].nickname}, {play_order[3].nickname}')

                await message.channel.send(player1_all_hand)
                await message.channel.send(player2_all_hand)
                await message.channel.send(player3_all_hand)
                await message.channel.send(player4_all_hand)
                return
                
        # Message to pass on turn, only works when game is setup and ongoing
        elif (message.content == '!pass' and Game['ongoing'] == (True, True)):
            
            # Cannot pass at the start of game
            if len(Game['game'].play_area) == 0:
                await message.channel.send('You cannot pass, you must play a card to start')
                return
            
            game_turn = Game['turn']
            current_player = Game['order'][game_turn]
            last_player = Game['game'].play_area[-1][1]
            
            # Cannot pass if everyone else has passed and you played the last hand
            if current_player.nickname == last_player:
                await message.channel.send('You cannot pass, you must play a card')
                return
            
            # It's not your turn
            if str(message.author) != str(current_player.discord_name):
                await message.channel.send(f'It is{current_player.nickname}\'s turn')
                return
            
            # Status message and increments turn
            Game['game'].can_play(current_player, [], skip_turn=True)
            Game['turn'] = (Game['turn'] + 1) % 4
            
            await message.channel.send(f'{current_player.nickname} has passed')
            return
            
        # Message to show the last played hands if possible
        # Displays player nickname next to hand played
        elif message.content == '!lasthands':
            num_of_hands = min(len(Game['game'].play_area), 5)
            last_five_hands = [(cards[1], cards[0]) for cards in Game['game'].play_area[-num_of_hands:]]

            last_five_str = '\n\n'.join([hand for hand in last_five_hands])

            await message.channel.send(f'The last hands are:\n\n{last_five_str}')
            return

        # Displays all players hands
        elif message.content == '!checkhands':
            play_order = Game['order']
            game_turn = Game['turn']
            current_player = Game['order'][game_turn]

            
            player1_suit_sorted = play_order[0].diamonds + play_order[0].clubs + play_order[0].hearts + play_order[0].spades
            
            player1_hands_suit = f'{play_order[0].nickname}\'s Hand\nBy suits:\n||{player1_suit_sorted}||\n'
            player1_hands_normal = f'By value:\n||{play_order[0].hand}||\n{delimiter_string}'
            player1_all_hand = player1_hands_suit + player1_hands_normal

            
            player2_suit_sorted = play_order[1].diamonds + play_order[1].clubs + play_order[1].hearts + play_order[1].spades
            
            player2_hands_suit = f'{play_order[1].nickname}\'s Hand\nBy suits:\n||{player2_suit_sorted}||\n'
            player2_hands_normal = f'By value:\n||{play_order[1].hand}||\n{delimiter_string}'
            player2_all_hand = player2_hands_suit + player2_hands_normal

            
            player3_suit_sorted = play_order[2].diamonds + play_order[2].clubs + play_order[2].hearts + play_order[2].spades
            
            player3_hands_suit = f'{play_order[2].nickname}\'s Hand\nBy suits:\n||{player3_suit_sorted}||\n'
            player3_hands_normal = f'By value:\n||{play_order[2].hand}||\n{delimiter_string}'
            player3_all_hand = player3_hands_suit + player3_hands_normal

            
            player4_suit_sorted = play_order[3].diamonds + play_order[3].clubs + play_order[3].hearts + play_order[3].spades
            
            player4_hands_suit = f'{play_order[3].nickname}\'s Hand\nBy suits:\n||{player4_suit_sorted}||\n'
            player4_hands_normal = f'By value:\n||{play_order[3].hand}||\n{delimiter_string}'
            player4_all_hand = player4_hands_suit + player4_hands_normal
            
            last_hand = (Game['game'].play_area[-1][1], Game['game'].play_area[-1][0])
            
            await message.channel.send(f'The player order is {play_order[0].nickname}, {play_order[1].nickname}, {play_order[2].nickname}, {play_order[3].nickname}\nIt is{current_player.nickname}\'s turn')

            await message.channel.send(player1_all_hand)
            await message.channel.send(player2_all_hand)
            await message.channel.send(player3_all_hand)
            await message.channel.send(player4_all_hand)
            await message.channel.send(f'Last played hand is:\n{last_hand}')
            return
        
        # Message to check skill rating
        elif message.content.startswith('!checkskill'):
            player_id = message.author.id
            
            if str(player_id) in all_elo.keys():
                if all_elo[str(player_id)] == float('inf'):
                    await message.channel.send('You have a rating of :infinity::sunglasses:')
                    return
                
                else:
                    await message.channel.send(f'You have a rating of {all_elo[str(player_id)]}')
                    return
            
            else:
                await message.channel.send('You don\'t have a rating\nJoin a game to get started')
                return

# Function to convert string to cards
def text_to_cards(string):
    # Text format is "Suit" + "Number
    # E.g Diamond King, Spade Ace, Club Six
    # It's not necessary to type out the entire card: D K, S 3 will be recognised
    try:
        try:
            assert type(string) == str
            
        except AssertionError:
            return 'Please input a string'
        
        true_cards = list(map(lambda x: x.split(), string.split(', ')))
        true_cards = [card for singular in true_cards for card in singular]
        length = len(true_cards)
        
        for i in range(length):
            if true_cards[i] == '10':
                continue
            
            else:
                true_cards[i] = true_cards[i][:1].upper()
    
        even = true_cards[::2]
        odd = true_cards[1::2]
        
        try:
            assert len(even) == len(odd)
            
        except AssertionError:
            return 'Please enter cards correctly'
            
        return list(zip(even, odd))
    
    except IndexError:
        return False


# Function to convert cards to a readable form
def cards_to_text(lst):
    # Text format is "Suit" + "Number
    # E.g Diamond King, Spade Ace, Club Six
    suits = ['D', 'C', 'H', 'S']
    numbers = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
    
    full_suits = ['Diamond', 'Club', 'Heart', 'Spade']
    full_numbers = ['3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace', '2']

    try:
        card_string = []
        length = len(lst)
    
        for i in range(length):
            suit_string = full_suits[suits.index(lst[i][0])] # Matches suit index with full suit index
            number_string = full_numbers[numbers.index(lst[i][1])] # Matches suit number with full number index
            card_name = suit_string + ' ' + number_string
            
            card_string.append(card_name)
    
    except IndexError:
        return False
    
    return card_string


# Function to return all the roles of a member
# Is case sensitive
def Tier(member):
    server_member = server_user(member)
    if server_member is False:
        return 'Not in server'
    
    else:
        tier = set(map(lambda x: x.name, server_member.roles))
        tier.remove('@everyone')
        return tier


# Function to check a member is in the server
def server_user(member):
    server_members = client.get_guild(auth['server_id'])
    
    if member in server_members.members:
        return server_members.get_member(member.id)
    return False


# Function to check and add person to skill pool
def has_elo(user_id, dictionary):
    if str(user_id) in dictionary.keys(): # Checks if user has an skill rating 
        text_blurb = 'has some skill'
        
        if dictionary[str(user_id)] == float('inf'):
            return (':infinity:', 'is a champ :sunglasses:')

        else:
            return (dictionary[str(user_id)], text_blurb)
    
    else:
        text_blurb = 'has been added to the elo pool'
        dictionary[str(user_id)] = 10000
        return (10000, text_blurb)

# Runs the bot
client.run(auth['token'])
