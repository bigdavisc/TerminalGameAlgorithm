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

        highestDamage = 0
        highestDamageSide = ""
        for i in damageWeightings:
            if damageWeightings[i] > highestDamage:
                highestDamageSide = i
                highestDamage = damageWeightings[i]

        if highestDamage >= 3:
            if highestDamageSide == "LEFT":
                # build left
            elif highestDamageSide == "MIDDLE":
                # build middle
            elif highestDamageSide == "RIGHT":
                #build right
        else:
            # ------------------BEGINNING OF GAME--------------------
            if game_state.turn_number == 0:
                self.build_that_scratch_post(game_state)
            self.build_that_wall(game_state)
            self.build_defences(game_state)
            # -------------------------------------------------------


        whatShouldBeOnTheBoard = self.removeDuplicates(whatShouldBeOnTheBoard).copy()
        destroyedFirewalls = self.find_destroyed_firewalls(whatShouldBeOnTheBoard,whatHasBeenBuilt)
        self.set_side_weighting(destroyedFirewalls)
        for key in whatHasBeenBuilt:
            for xy in whatHasBeenBuilt[key]:
                whatShouldBeOnTheBoard[key].append(xy)
        for key in whatHasBeenBuilt:
            whatHasBeenBuilt[key] = []

        # -----------DEPLOY ATTACKERS EVERY ROUND------------
        self.deploy_attackers(game_state)
        # ---------------------------------------------------

    def build_defences(self, game_state):
        global whatHasBeenBuilt

        firewall_locations = [[0,13],[1,12],[27,13],[23,12],[24,13],[20,10],[2,11],[25,11],[13,10],[6,10]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

        firewall_locations = [[26,12], [24,10]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
                whatHasBeenBuilt["ENCRYPTORS"].append(location)

        destructor_wall = []
        for i in range(3,21):
            new_location = [i, 10]
            destructor_wall.append(new_location)
        for location in destructor_wall:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

        firewall_locations = [[23,9]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

        encryptor_wall = []
        for i in range(20, 6, -3):
            new_location = [i, 9]
            encryptor_wall.append(new_location)
        for location in encryptor_wall:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)
                whatHasBeenBuilt["ENCRYPTORS"].append(location)

    def build_that_wall(self, game_state):
        global whatHasBeenBuilt
        filter_locations = []

        for i in range(2, 23):
            new_location = [i, 11]
            filter_locations.append(new_location)

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)

    def build_that_scratch_post(self, game_state):
        global whatHasBeenBuilt
        filter_locations = [[6,11],[7,11],[8,11],[19,11],[20,11],[21,11],[11,11],[12,11],[13,11],[14,11],[15,11],[16,11]]
        destructor_locations = [[7,10], [20,10],[0,13],[1,13],[27,13]]

        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                whatHasBeenBuilt["FILTERS"].append(location)

        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                whatHasBeenBuilt["DESTRUCTOR"].append(location)

    def deploy_attackers(self, game_state):

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

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
