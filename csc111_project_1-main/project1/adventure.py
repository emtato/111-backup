"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional
import random

from game_entities import Location, Item, Player
from proj1_event_logger import Event, EventList


class AdventureGame:
    """A text adventure game class storing all location, item, player and map data.

    Instance Attributes:
        - # TODO add descriptions of public instance attributes as needed

    Representation Invariants:
        - # TODO add any appropriate representation invariants as needed
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: dict[int, tuple]
    player: Player
    ongoing: bool

    def __init__(self, game_data_file: str) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items, self.player = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.ongoing = True  # whether the game is ongoing

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], dict[int, tuple], Player]:
        """Load locations, items, and player data from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        (2) a list of all Item objects, and (3) a Player object"""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['name'], loc_data['brief_description'],
                                    loc_data['long_description'], loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = {}
        for item in data['items']:
            items[item['name']] = (
                item['description'], item['start_position'], item['target_position'], item['target_points'])

        player_data = data['player']
        player = Player(player_data['name'], player_data['score'], player_data['current_location'],
                        player_data['time_remaining'], 0, player_data['items'])
        return locations, items, player

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the player's current location.
        """
        return self._locations[loc_id] if loc_id else self._locations[self.player.current_location]


# Helper functions
def display_summary() -> None:
    """Print a summary of the current status of the player, including a description of the location,
    items at the location, remaining time, and next possible moves

    Preconditions:
        - :)
    """
    # print information about the current location
    print()
    print("========")
    if location.visited:
        print(location.brief_description)
    else:
        print(location.long_description)
        location.visited = True

    # print information about time remaining
    print(f'You have {game.player.time_remaining} minutes remaining, and ur brokeness level is {game.player.balance}')

    # Display possible actions at this location
    print("========")
    print(f"\033[38;5;250mWhat to do? Choose from: look, inventory, score, undo, log, quit")
    print("At this location, you can also:")
    for action in location.available_commands:
        print("-", action)
    if len(location.items) > 0:
        print('- pick up\033[0m')


def get_user_choice(location: Location) -> str:
    """Gets and returns the user's choice of next command

    Preconditions:
        - preconditions so cute!
    """
    # command shortcuts to make operating easier
    shortcuts = {"l": "look", "i": "inventory", "sc": "score", "u": "undo", "q": "quit", "lo": "log", "p": "pick up",
                 "n": "go north", "s": "go south", "e": "go east", "w": "go west"}
    # Validate choice
    user_choice = input(f"\033[0m\nEnter action: ").lower().strip()
    while user_choice not in location.available_commands and user_choice not in menu and user_choice not in shortcuts:
        print("That was an invalid option; try again.")
        user_choice = input("\nEnter action: ").lower().strip()
    if user_choice.__len__() < 3:
        user_choice = shortcuts[user_choice]
    return user_choice


# TODO: finish implementing this function
def handle_menu_action(choice: str) -> None:
    """Perform an action based on the user's choice of command, where the command is one of the menu options

    Preconditions:
        - hii
    """
    if choice == "log":
        game_log.display_events()
    elif choice == "look":
        print(location.long_description)
    elif choice == "inventory":
        print(f'Your inventory contains:')
        for item in game.player.inventory:
            print(item)
    elif choice == "score":
        print(f'Your score is {game.player.score} points')
    elif choice == "undo":
        # TODO: finish this undo command to account for undoing non-movement actions
        # if the event removed is a 'Go [direction]' type event
        if game_log.last.prev is None:
            print("what r u trying to undo launching the game?? 💀")
        else:
            if 'picked up' in game_log.last.prev.next_command:
                s = game_log.last.prev.next_command[10:]
                if 'loonie' in s:
                    game.player.balance -= 1
                elif 'toonie' in s:
                    game.player.balance -= 2
                else:
                    game.player.inventory.remove(game._items[s])
            loc = game_log.last.id_num

            game.get_location(loc).items.append(s)
            game_log.remove_last_event()

            game.player.current_location = game_log.last.id_num
            game.player.time_remaining += 1

    else:
        game.ongoing = False


# TODO: implement and use this function
def handle_event_action(choice: str) -> None:
    """player said move somewhere fucking MOVE

    Preconditions:
        - c:
    """
    loc = game.get_location()
    if choice in loc.available_commands:
        result = location.available_commands[choice]
        game.player.current_location = result

        event = Event(result, game.get_location().name)
        game_log.add_event(event, choice)
        game.player.time_remaining -= 1
    elif choice == 'pick up':
        if len(loc.items) > 0:

            print(f'\033[91mur not getting {loc.items[-1]} buddy\033[0m')
            if loc.items[-1] == 'loonie' or loc.items[-1] == 'toonie':
                game.player.balance += 1 if loc.items[-1] == 'loonie' else 2
                event = Event(loc.id_num, game.get_location().name)
                game_log.add_event(event, f'picked up {loc.items[-1]}')
                loc.items.pop(-1)  # cry about the inneficiency

            else:
                items = game._items  # dic
                #game.player.inventory.append(items[loc.items[-1]])
                game.player.inventory.append(loc.items[-1])
                event = Event(loc.id_num, game.get_location().name)
                game_log.add_event(event, f'picked up {loc.items[-1]}')
                loc.items.pop(-1)
            game.player.time_remaining -= 1
        else:
            print('maybe sleep deprivation is getting to you')
    else:
        with open('silly.txt') as file:
            file.readline()
            lines = []
            for i in range(6):
                line = file.readline()
                lines.append(line)
            randomnum = random.randint(0, 5)
            chosen = lines[randomnum]
            chosen = chosen.split(' ')
            chosen[4] = choice[3:]
            chosen[4] += '.' if randomnum == 1 else ''
            print(' '.join(chosen))


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json')  # load data
    menu = ["look", "inventory", "score", "undo", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # add event to the log of events
    location = game.get_location()
    new_event = Event(location.id_num, location.name)
    game_log.add_event(new_event, choice)

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your marks will be based on how well-organized your code is.

        # Location object of the player's current location
        location = game.get_location()

        # print a summary of the current status of the player
        display_summary()

        # user makes a new choice
        choice = get_user_choice(location)

        print("========")
        print("You decided to", choice)

        # handle menu actions
        if choice in menu:
            handle_menu_action(choice)

        # handle non-menu actions
        else:
            # handle 'Go [direction]' actions
            handle_event_action(choice)

            # TODO: Add in code to deal with actions which do not change the location (e.g. taking or using an item)
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game

    # after game ends
    print("Thank you for playing! \nSkibidi toilet ohio :p")
