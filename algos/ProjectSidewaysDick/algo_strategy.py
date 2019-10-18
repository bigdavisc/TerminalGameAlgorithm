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

enemyHealth = {0:30}
currentAttackingSide = "RIGHT"

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
        global enemyHealth
        global currentAttackingSide

        """
        Build the C1 logo. Calling this method first prioritises
        resources to build and repair the logo before spending them 
        on anything else.
        """
        if game_state.turn_number % 4 == 0 and game_state.turn_number > 0:
            if game_state.enemy_health < enemyHealth[game_state.turn_number-3]:
                return
            else:
                if currentAttackingSide == "LEFT": currentAttackingSide = "RIGHT"
                else: currentAttackingSide = "LEFT"

        if currentAttackingSide == "RIGHT":
            self.build_that_runway_right(game_state)
            self.build_those_encryptors_right(game_state)
            self.build_that_wall_of_filters(game_state)
            self.deploy_attackers_right(game_state)
        else:
            self.build_that_runway_left(game_state)
            self.build_those_encryptors_left(game_state)
            self.build_that_wall_of_filters(game_state)
            self.deploy_attackers_left(game_state)
        self.build_that_wall_of_destructors(game_state)

        enemyHealth[game_state.turn_number] = game_state.enemy_health



    # def build_defences(self, game_state):
    #
    #     encryptor_locations = []
    #     for i in range(0,2):
    #         new_location = [24-i,12-i]
    #         encryptor_locations.append(new_location)
    #     for location in encryptor_locations:
    #         if game_state.can_spawn(ENCRYPTOR, location):
    #             game_state.attempt_spawn(ENCRYPTOR, location)
    #
    #     destructor_locations = [[24,13], [25,13]]
    #     for location in destructor_locations:
    #         if game_state.can_spawn(DESTRUCTOR, location):
    #             game_state.attempt_spawn(DESTRUCTOR, location)
    #
    #     for i in range(2,13):
    #         new_location = [24-i,12-i]
    #         encryptor_locations.append(new_location)
    #     for location in encryptor_locations:
    #         if game_state.can_spawn(ENCRYPTOR, location):
    #             game_state.attempt_spawn(ENCRYPTOR, location)
    #
    #     for i in range(2,21,3):
    #         new_location = [i,12]
    #         destructor_locations.append(new_location)
    #     for location in destructor_locations:
    #         if game_state.can_spawn(DESTRUCTOR, location):
    #             game_state.attempt_spawn(DESTRUCTOR, location)
    #
    # def build_that_runway(self, game_state):
    #     filter_locations = []
    #
    #     for i in range(0, 12):
    #         new_location = [12+i, 1+i]
    #         filter_locations.append(new_location)
    #
    #     for location in filter_locations:
    #         if game_state.can_spawn(FILTER, location):
    #             game_state.attempt_spawn(FILTER, location)
    #
    # def build_that_wall(self, game_state):
    #     filter_locations = []
    #
    #     for i in range(1, 23, 2):
    #         new_location = [i, 12]
    #         filter_locations.append(new_location)
    #
    #     for location in filter_locations:
    #         if game_state.can_spawn(FILTER, location):
    #             game_state.attempt_spawn(FILTER, location)

    # def deploy_attackers(self, game_state):
    #     """
    #     First lets check if we have 10 bits, if we don't we lets wait for
    #     a turn where we do.
    #     """
    #     if (game_state.get_resource(game_state.BITS) <= 0):
    #         return
    #     if (game_state.turn_number > 4):
    #         if (game_state.get_resource(game_state.BITS) >= 12.0):
    #             while game_state.get_resource(game_state.BITS) >= 1.0:
    #                 game_state.attempt_spawn(PING, [13, 0])
    #         else:
    #             return
    #     else:
    #         while game_state.get_resource(game_state.BITS) >= 1.0:
    #             game_state.attempt_spawn(PING, [13, 0])
    #
    #     """
    #     NOTE: the locations we used above to spawn information units may become
    #     blocked by our own firewalls. We'll leave it to you to fix that issue
    #     yourselves.
    #
    #     Lastly lets send out Scramblers to help destroy enemy information units.
    #     A complex algo would predict where the enemy is going to send units and
    #     develop its strategy around that. But this algo is simple so lets just
    #     send out scramblers in random locations and hope for the best.
    #
    #     Firstly information units can only deploy on our edges. So lets get a
    #     list of those locations.
    #     """
    #     friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
    #
    #     """
    #     Remove locations that are blocked by our own firewalls since we can't
    #     deploy units there.
    #     """
    #     deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
    #
    #
    # def filter_blocked_locations(self, locations, game_state):
    #     filtered = []
    #     for location in locations:
    #         if not game_state.contains_stationary_unit(location):
    #             filtered.append(location)
    #     return filtered


#----------------------LEFT SIDE RUNWAY-----------------------
    def build_that_runway_left(self,game_state):

        removal_locations = [[12,1],[13,2]]
        for i in range(0, 10):
            new_location = [24 - i, 12 - i]
            removal_locations.append(new_location)
        for location in removal_locations:
            game_state.attempt_remove(location)

        filter_locations = []
        for i in range(0, 12):
            new_location = [15-i, 1+i]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        destructor_locations = [[2,13], [3,13]]
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        encryptor_locations = []
        for i in range(0,2,2):
            new_location = [3+i,12-i]
            encryptor_locations.append(new_location)
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def build_those_encryptors_left(self, game_state):
        encryptor_locations = []
        for i in range(2,10,2):
            new_location = [3+i,12-i]
            encryptor_locations.append(new_location)
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
# ------------------------------------------------------------


# ----------------------RIGHT SIDE RUNWAY---------------------
    def build_that_runway_right(self, game_state):

        removal_locations = [[15,1],[14,2]]
        for i in range(0,10):
            new_location = [3+i,12-i]
            removal_locations.append(new_location)
        for location in removal_locations:
            game_state.attempt_remove(location)

        filter_locations = []
        for i in range(0, 12):
            new_location = [12 + i, 1 + i]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        destructor_locations = [[24, 13], [25, 13]]
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        encryptor_locations = []
        for i in range(0, 2):
            new_location = [24 - i, 12 - i]
            encryptor_locations.append(new_location)
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def build_those_encryptors_right(self, game_state):
        encryptor_locations = []
        for i in range(2, 10, 2):
            new_location = [24 - i, 12 - i]
            encryptor_locations.append(new_location)
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
# ------------------------------------------------------------


# -------------------------FRONT WALL-------------------------
    def build_that_wall_of_filters(self, game_state):
        filter_locations = []

        for i in range(4, 23, 2):
            new_location = [i, 12]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

    def build_that_wall_of_destructors(self, game_state):
        destructor_locations = []

        for i in range(5, 23, 2):
            new_location = [i, 12]
            destructor_locations.append(new_location)

        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
# ------------------------------------------------------------


# -----------------------DEPLOY ATTACKERS---------------------
    def deploy_attackers_right(self, game_state):
        if (game_state.get_resource(game_state.BITS) <= 0):
            return
        if (game_state.turn_number > 4):
            if (game_state.get_resource(game_state.BITS) >= 12.0):
                while game_state.get_resource(game_state.BITS) >= 1.0:
                    game_state.attempt_spawn(PING, [13, 0])
            else:
                return
        else:
            while game_state.get_resource(game_state.BITS) >= 1.0:
                game_state.attempt_spawn(PING, [13, 0])

    def deploy_attackers_left(self, game_state):
        if (game_state.get_resource(game_state.BITS) <= 0):
            return
        if (game_state.turn_number > 4):
            if (game_state.get_resource(game_state.BITS) >= 12.0):
                while game_state.get_resource(game_state.BITS) >= 1.0:
                    game_state.attempt_spawn(PING, [14, 0])
            else:
                return
        else:
            while game_state.get_resource(game_state.BITS) >= 1.0:
                game_state.attempt_spawn(PING, [14, 0])
# ------------------------------------------------------------


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
