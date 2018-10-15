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

whatHasBeenBuilt = {"DESTRUCTOR": [],
                   "ENCRYPTORS": [],
                   "FILTERS": []
                   }

whatShouldBeOnTheBoard = {"DESTRUCTOR": [],
                   "ENCRYPTORS": [],
                   "FILTERS": []
                   }

damageWeightings = {"LEFT": 0,
                   "MIDDLE": 0,
                   "RIGHT": 0
                   }

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
        global whatHasBeenBuilt
        global whatShouldBeOnTheBoard
        global damageWeightings

        self.build_that_wall(game_state)

        highestDamage = 0
        highestDamageSide = ""
        for i in damageWeightings:
            if damageWeightings[i] > highestDamage:
                highestDamageSide = i
                highestDamage = damageWeightings[i]

        if highestDamage >= 3:
            if highestDamageSide == "LEFT":
                self.build_up_left(game_state)
                self.build_tunnel_right(game_state)

                self.deploy_attackers_left(game_state)
            elif highestDamageSide == "MIDDLE":
                self.build_up_middle(game_state)

                self.deploy_attackers_left(game_state)
            elif highestDamageSide == "RIGHT":
                self.build_up_right(game_state)
                self.build_tunnel_left(game_state)

                self.deploy_attackers_right(game_state)
        else:
            # ------------------BEGINNING OF GAME--------------------
            if game_state.turn_number == 0:
                self.build_that_wall(game_state)
                self.build_that_scratch_post(game_state)
            self.build_tunnel_right(game_state)
            self.build_up_left(game_state)
            # -------------------------------------------------------
            # -------------------DEPLOY ATTACKERS--------------------
            self.deploy_attackers_left(game_state)
            # -------------------------------------------------------

        # if game_state.get_resource(game_state.CORES) >= 10:
        #     self.build_that_front_wall(game_state)

        whatShouldBeOnTheBoard = self.removeDuplicates(whatShouldBeOnTheBoard).copy()
        destroyedFirewalls = self.find_destroyed_firewalls(whatShouldBeOnTheBoard,whatHasBeenBuilt)
        self.set_side_weighting(destroyedFirewalls)
        for key in whatHasBeenBuilt:
            for xy in whatHasBeenBuilt[key]:
                whatShouldBeOnTheBoard[key].append(xy)
        for key in whatHasBeenBuilt:
            whatHasBeenBuilt[key] = []

    def build_defences(self, game_state):
        global whatHasBeenBuilt

        firewall_locations = [[20,10],[13,10],[6,10]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

        firewall_locations = [[26,12], [24,10]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
                whatHasBeenBuilt["ENCRYPTORS"].append(location)


    def build_that_wall(self, game_state):
        global whatHasBeenBuilt
        filter_locations = []

        for i in range(5, 23):
            new_location = [i, 11]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)

    def build_that_front_wall(self, game_state):
        global whatHasBeenBuilt
        filter_locations = []

        for i in range(8, 20):
            new_location = [i, 10]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)

    def build_that_scratch_post(self, game_state):
        global whatHasBeenBuilt
        destructor_locations = [[0,13],[27,13],[7,10],[20,10],[1,13]]

        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

    def deploy_attackers_left(self, game_state):

        if (game_state.turn_number in range(1,2)):
            while game_state.get_resource(game_state.BITS) >= 1.0:
                game_state.attempt_spawn(PING, [4,9])
            else: return

        if (game_state.get_resource(game_state.BITS) < 12):
            return
        if (game_state.get_resource(game_state.BITS) <= 0):
            return

        while game_state.get_resource(game_state.BITS) >= 3.0:
            game_state.attempt_spawn(EMP, [4, 9])

        while game_state.get_resource(game_state.BITS) >= 1.0:
            game_state.attempt_spawn(SCRAMBLER, [5, 8])

    def deploy_attackers_right(self, game_state):

        if (game_state.turn_number in range(1,2)):
            while game_state.get_resource(game_state.BITS) >= 1.0:
                game_state.attempt_spawn(PING, [23,9])
            else: return

        if (game_state.get_resource(game_state.BITS) < 12):
            return
        if (game_state.get_resource(game_state.BITS) <= 0):
            return

        while game_state.get_resource(game_state.BITS) >= 3.0:
            game_state.attempt_spawn(EMP, [23, 9])

        while game_state.get_resource(game_state.BITS) >= 1.0:
            game_state.attempt_spawn(SCRAMBLER, [22, 8])

    def find_destroyed_firewalls(self, whatsShouldBeTheBoard, whatHasBeenBuilt):

        destroyedDefences = {"DESTRUCTOR": [],
                           "ENCRYPTORS": [],
                           "FILTERS": []
                           }

        for key in whatsShouldBeTheBoard:
            destroyedDefences[key] = [item for item in whatHasBeenBuilt[key] if item in whatsShouldBeTheBoard[key]]

        return destroyedDefences

    def set_side_weighting(self,destroyedDictionary):
        global damageWeightings

        for key in destroyedDictionary:
            for xy in destroyedDictionary[key]:
                if xy[0] in range(0,9): damageWeightings["LEFT"] += 1
                elif xy[0] in range(9,19): damageWeightings["MIDDLE"] += 1
                else: damageWeightings["RIGHT"] += 1
                
    def removeDuplicates(self,whatHasBeenBuilt):

        output = {"DESTRUCTOR": [],
                             "ENCRYPTORS": [],
                             "FILTERS": []
                             }

        for key in whatHasBeenBuilt:
            for xy in whatHasBeenBuilt[key]:
                if xy not in output[key]:
                    output[key].append(xy)
        return output

    def build_up_left(self, game_state):
        global whatHasBeenBuilt
        # -------------BUILD CORNER DESTRUCTORS----------------
        destructor_locations = [[0, 13], [1, 13]]
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)
        # -----------------------------------------------------
        #-------------BUILD SECOND WALL OF FILTERS--------------
        filter_locations = []
        for i in range(2, 8):
            new_location = [i, 12]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        # -----------------------------------------------------
        # -------------BUILD FRONT WALL OF FILTERS-------------
        filter_locations = []
        for i in range(1, 7):
            new_location = [i, 13]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        # -----------------------------------------------------
        #-------------BUILD BACK WALL OF FILTERS---------------
        filter_locations = []
        for i in range(2, 9):
            new_location = [i, 11]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        # -----------------------------------------------------

    def build_up_middle(self, game_state):
        global whatHasBeenBuilt

        self.build_that_front_wall(game_state)

        return

    def build_up_right(self, game_state):
        global whatHasBeenBuilt
        # -------------BUILD CORNER DESTRUCTORS----------------
        destructor_locations = [[26,13],[27,13]]
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)
        # -----------------------------------------------------
        #-------------BUILD SECOND WALL OF FILTERS--------------
        filter_locations = []
        for i in range(26, 20,-1):
            new_location = [i, 12]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        # -----------------------------------------------------
        # -------------BUILD FRONT WALL OF FILTERS-------------
        filter_locations = []
        for i in range(27, 21, -1):
            new_location = [i, 13]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        # -----------------------------------------------------
        # -------------BUILD BACK WALL OF FILTERS---------------
        filter_locations = []
        for i in range(25, 18,-1):
            new_location = [i, 11]
            filter_locations.append(new_location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)
        # -----------------------------------------------------

    def build_tunnel_right(self, game_state):
        global whatHasBeenBuilt
        clear_path = [[23,10],[23,11],[24,11],[24,12],[25,12],[25,13],[26,13]]
        game_state.attempt_remove(clear_path)

        destructor_locations = [[27,13],[24,13],[23,12],[25,11],[23,13]]
        filter_locations = [[22,11]]
        encyrptor_locations = [[26,12],[24,10]]

        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        for location in encyrptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
                whatHasBeenBuilt["ENCRYPTORS"].append(location)

    def build_tunnel_left(self, game_state):
        global whatHasBeenBuilt
        clear_path = [[3,11],[4,11],[3,12],[2,12],[1,13],[2,13],[4,10]]
        game_state.attempt_remove(clear_path)

        destructor_locations = [[0,13],[3,13],[4,12],[2,11],[4,13]]
        filter_locations = [[5,11]]
        encyrptor_locations = [[1, 12],[3,10]]

        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)
        for location in encyrptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
                whatHasBeenBuilt["ENCRYPTORS"].append(location)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
