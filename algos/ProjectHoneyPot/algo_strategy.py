import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Build the C1 logo. Calling this method first prioritises
        resources to build and repair the logo before spending them 
        on anything else.
        """
        self.build_that_wall(game_state)

        """
        Then build additional defenses.
        """
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """

        if game_state.get_resource(game_state.BITS) >= 12:
            self.deploy_attackers(game_state)

    # # Here we make the C1 Logo!
    # def build_c1_logo(self, game_state):
    #     """
    #     We use Filter firewalls because they are cheap
    #
    #     First, we build the letter C.
    #     """
    #     firewall_locations = [[8, 11], [9, 11], [7,10], [7, 9], [7, 8], [8, 7], [9, 7]]
    #     for location in firewall_locations:
    #         if game_state.can_spawn(FILTER, location):
    #             game_state.attempt_spawn(FILTER, location)
    #
    #     """
    #     Build the number 1.
    #     """
    #     firewall_locations = [[17, 11], [18, 11], [18, 10], [18, 9], [18, 8], [17, 7], [18, 7], [19,7]]
    #     for location in firewall_locations:
    #         if game_state.can_spawn(FILTER, location):
    #             game_state.attempt_spawn(FILTER, location)
    #
    #     """
    #     Build 3 dots with destructors so it looks neat.
    #     """
    #     firewall_locations = [[11, 7], [13, 9], [15, 11]]
    #     for location in firewall_locations:
    #         if game_state.can_spawn(DESTRUCTOR, location):
    #             game_state.attempt_spawn(DESTRUCTOR, location)

    def build_defences(self, game_state):
        """
        First lets protect ourselves a little with destructors:
        """
        firewall_locations = [[0,13],[27,13],[20,10],[1,12],[26,12],[2,11],[25,11],[23,10],[13,10],[6,10],[1,13],[26,13]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        firewall_locations = [[24,10]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

        firewall_locations = [[25,12], [2,12], [18,4], [9,4]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)


        destructor_wall = []

        for i in range(4,21):
            new_location = [i, 10]
            destructor_wall.append(new_location)

        for location in destructor_wall:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)



        all_locations = []
        for i in range(game_state.ARENA_SIZE):
            for j in range(math.floor(game_state.ARENA_SIZE / 2)):
                if (game_state.game_map.in_arena_bounds([i, j])):
                    all_locations.append([i, j])
        
        """
        Then we remove locations already occupied.
        """
        possible_locations = self.filter_blocked_locations(all_locations, game_state)

    def build_that_wall(self, game_state):
        filter_locations = []

        for i in range(3, 21):
            new_location = [i, 11]
            filter_locations.append(new_location)
        for i in range(23, 25):
            new_location = [i, 11]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

    def deploy_attackers(self, game_state):
        """
        First lets check if we have 10 bits, if we don't we lets wait for
        a turn where we do.
        """
        if (game_state.get_resource(game_state.BITS) < 12):
            return
        if (game_state.get_resource(game_state.BITS) <= 0):
            return
        """
        First lets deploy an EMP long range unit to destroy firewalls for us.
        """
        while game_state.get_resource(game_state.BITS) >= 3.0:
            game_state.attempt_spawn(EMP, [4, 9])

        while game_state.get_resource(game_state.BITS) >= 1.0:
            game_state.attempt_spawn(SCRAMBLER, [5, 8])

        """
        NOTE: the locations we used above to spawn information units may become 
        blocked by our own firewalls. We'll leave it to you to fix that issue 
        yourselves.

        Lastly lets send out Scramblers to help destroy enemy information units.
        A complex algo would predict where the enemy is going to send units and 
        develop its strategy around that. But this algo is simple so lets just 
        send out scramblers in random locations and hope for the best.

        Firstly information units can only deploy on our edges. So lets get a 
        list of those locations.
        """
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        """
        Remove locations that are blocked by our own firewalls since we can't 
        deploy units there.
        """
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
