import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    pings_spawned = []
    deletedWalls = False

    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

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
        # This is a good place to do initial setup
        self.scored_on_locations = []


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
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """


    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)

        # Now build reactive defenses based on where the enemy scored
        # TODO: Implement
        # self.build_reactive_defense(game_state)

        # TODO: Fix stall
        # If not enough bits, scrambler stall
        if game_state.get_resource(game_state.BITS, player_index=0) < 12:
            # If the turn is less than 4, stall with Scramblers with 1 on each side
            self.stall_with_scramblers(game_state)
        else:
            # # Now let's analyze the enemy base to see where their defenses are concentrated.
            # # If they have many units in the front we can build a line for our EMPs to attack them at long range.
            # if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
            #     self.emp_line_strategy(game_state)
            # else:
            #     # They don't have many units in the front so lets figure out their least defended area and send Pings there.

            #     # Only spawn Ping's every other turn
            #     # Sending more at once is better since attacks can only hit a single ping at a time
            #     if game_state.turn_number % 2 == 1:
            #         # To simplify we will just check sending them from back left and right
            #         ping_spawn_location_options = [[13, 0], [14, 0]]
            #         best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
            #         game_state.attempt_spawn(PING, best_location, 1000)

            #     # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
            #     encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
            #     game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)
        # Else - Ping rush
            self.pingRush(game_state)

    def pingRush(self, game_state):
        mostDangerousSide = self.check_side_more_defences(game_state)
        if mostDangerousSide == "LEFT":
            # Attack the right side
            location = [5,8]
        else:
            # Attack the left side
            location = [22,8]
        while game_state.can_spawn(PING, location):
            game_state.attempt_spawn(PING, location)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """




        # Destructor spawn
        destructor_locations = [[11,7], [16, 7]]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)
        
        # Place filters to block the edges
        filter_locations = [[0, 13], [1,13], [2,13], [25,13], [26,13], [27,13], [3,12], [4,11], [24,12], [23,11]]  
        game_state.attempt_spawn(FILTER, filter_locations)

        if not self.deletedWalls:
            filter_locations_2 = [[22,10],[5,10], [6,9], [21,9], [20,8], [7,8], [8,7], [19,7]]
            game_state.attempt_spawn(FILTER, filter_locations_2)

        destructor_locations_2 = [[12,5], [15,5]]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations_2)

        destructor_locations_3 = [[10,7], [17,7], [12,6], [16,7], [15,6], [25,12], [2,12]]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations_3)

        filter_locations_4 = [[9,7], [18,7], [12,7], [15,7],[11,8], [16,8], [17,8], [10,8]]
        game_state.attempt_spawn(FILTER, filter_locations_4)

        destructor_locations_4 = [[11,6], [16,6], [12,5], [15,5], [4,10], [23,10]]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations_4)

        encryptor_locations = [[9,6], [10,6], [10,5], [17,6], [18,6], [17,5]]
        game_state.attempt_spawn(ENCRYPTOR,encryptor_locations)

        encryptor_locations_2 = [[11,5], [11,4], [12,4], [15,4], [16,4], [16,5], [12,2], [13,2], [14,2], [15,2], [11,11], [16,11]]
        game_state.attempt_spawn(ENCRYPTOR,encryptor_locations_2)

        # Filters for random turrets
        filter_locations_5 = [[11,12], [10,11], [12,11], [11,10], [16,12], [15,11], [17,11], [16,10]]
        game_state.attempt_spawn(FILTER, filter_locations_5)

    
        # Rebuild (Condition)
        # TODO: Write condition for rebuild
        if not self.deletedWalls and game_state.get_resource(game_state.CORES, player_index=0) >= 24:
            # TODO: Need to save boolean states in game_state
            self.rebuildWallsRight(game_state)
            self.rebuildWallsLeft(game_state)
            self.deletedWalls = True
        if self.deletedWalls and game_state.get_resource(game_state.CORES, player_index=0 >= 8):
            self.buildWallEncryptorRight(game_state)
            self.buildWallEncryptorLeft(game_state)

    def rebuildWallsRight(self, game_state):
        filter_deletes = [[19,7], [20,8], [21,9], [22,10]]
        filter_build = [[19,8], [20,9], [21,10], [22,11]]
        game_state.attempt_remove(filter_deletes)
        game_state.attempt_spawn(FILTER, filter_build)

    def rebuildWallsLeft(self, game_state):
        filter_deletes = [[8,7], [7,8], [6,9], [5,10]]
        filter_build = [[5,11], [6,10], [7,9], [8,8]]
        game_state.attempt_remove(filter_deletes)
        game_state.attempt_spawn(FILTER, filter_build)

    def buildWallEncryptorRight(self, game_state):
        encryptor_build = [[19,7], [20,8], [21,9], [22,10]]
        game_state.attempt_spawn(ENCRYPTOR, encryptor_build)

    def buildWallEncryptorLeft(self, game_state):
        encryptor_build = [[8,7], [7,8], [6,9], [5,10]]
        game_state.attempt_spawn(ENCRYPTOR, encryptor_build)

    def check_side_more_defences(self, game_state):
        total_defence_left = 0
        total_defence_right = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit:
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and unit.unit_type == DESTRUCTOR and location[1] > 13:
                        if location[0] < 14:
                            total_defence_left += 1
                        else:
                            total_defence_right += 1
        return "LEFT" if total_defence_left > total_defence_right else "RIGHT"

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        enemy_bits = game_state.get_resource(game_state.BITS, player_index=1)
        projected_enemy_bits = game_state.project_future_bits(player_index=1, current_bits = enemy_bits)

        gamelib.debug_write("Current enemy bits: {}".format(enemy_bits))
        gamelib.debug_write("Projected enemy bits: {}".format(projected_enemy_bits))

        if game_state.turn_number < 5:
            scrambler_locations = [[11,2]]
            game_state.attempt_spawn(SCRAMBLER, scrambler_locations)
        else:
            if projected_enemy_bits > 5:
                # Initial scramblers to prevent bum-rush
                scrambler_locations = [[11,2], [16,2]]
                if projected_enemy_bits > 5 and projected_enemy_bits < 8:
                    pass
                # 3 in total
                elif projected_enemy_bits > 7 and projected_enemy_bits < 11:
                    scrambler_locations.append([16,2])
                # 4 in total
                elif projected_enemy_bits > 10 and projected_enemy_bits < 13:
                    scrambler_locations.append([16,2])
                    scrambler_locations.append([11,12])
                else:
                # 5 in total
                    scrambler_locations.append([16, 2])
                    scrambler_locations.append([16, 2])
                    scrambler_locations.append([11,12])

                game_state.attempt_spawn(SCRAMBLER, scrambler_locations)
            else:
                pass

        # TODO: DO we need this?
        # # We can spawn moving units on our edges so a list of all our edge locations
        # friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # # Remove locations that are blocked by our own firewalls 
        # # since we can't deploy units there.
        # deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # # While we have remaining bits to spend lets send out scramblers randomly.
        # while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
        #     # Choose a random deploy location.
        #     deploy_index = random.randint(0, len(deploy_locations) - 1)
        #     deploy_location = deploy_locations[deploy_index]
            
        #     game_state.attempt_spawn(SCRAMBLER, deploy_location)
        #     """
        #     We don't have to remove the location since multiple information 
        #     units can occupy the same space.
        #     """
    def did_enemy_rush_with_pings_prev_turns(self):
        lenSpawned = len(self.pings_spawned)
        if lenSpawned > 1:
            return self.pings_spawned[len(self.pings_spawned)-1] > self.pings_spawned[len(self.pings_spawned) - 2]
        return False

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]


    # def countEnemyUnits(self, game_state, unit_type=None):
    #     total_units = 0
    #     for location in game_state.game_map:
    #         if location[1] > 13 and game_state.contains_stationary_unit(location):
    #             for unit in game-state.game_map[loica]


    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]

        # IF FIRST ANIMATION FRAME
        if state["turnInfo"][2] == 0:
            count_pings = len(state["p2Units"][3])
            self.pings_spawned.append(count_pings)

        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
