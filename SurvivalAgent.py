import heapq
import time
import os
from RuleClass import Belief,Rule,eliminate_belief,introduce_belief,get_highest_ranked_desire,match_goal_arrived,rules_set,desire_action
from EnvironmentClass import Environment

environment_stuff_types={
    'W':'water',
    'F':'food',
    'Z':'danger',
    'A':'ally'
}
class SurvivalAgent:
    def __init__(self, name, position, grid_size):
        # Basic attributes
        self.name = name                # Name or ID of the agent
        self.position = position        # (x, y) coordinates in the environment
        self.grid_size = grid_size      # Size of the environment (grid)

        # Survival stats
        self.health = 100               # Health points (0-100)
        self.hunger = 80               # Hunger level (0-100, where 0 = starving)
        self.thirst = 80               # Thirst level (0-100, where 0 = dehydrated)             # Energy level (0-100, where 0 = exhausted)         
        
        # Environmental Awareness
        self.memory = [['?' for _ in range(grid_size)] for _ in range(grid_size)]  # Map memory
        
        # Perception
        self.perception_radius = 2      # Default perception radius
        self.perceived_area = []        # Stores perceived environment area
        self.beliefs:list[Belief] =[]
        self.desires:list[Belief]=[]
        self.rules:list[Rule]=rules_set
        
        # Behavior/decision-making
        self.goal = None                # Current goal (e.g., find food, find shelter)
        self.status = "idle"            # Status (e.g., idle, exploring, moving to resource)
        self.inventory = []             # Items the agent carries (e.g., food, water)
    def update_stats(self):  
              
        if self.hunger!=0:self.hunger -= 1;  
        else: self.health-=20            
        if self.thirst!=0:self.thirst -= 1
        else: self.health-=30
    def perceive(self, environment:Environment, radius=None):
        """ Perceive surroundings based on a perception radius. """
        if radius is None:
            radius = self.perception_radius
        for comunication in environment.context:
            if(comunication.extraInf!=self.name):
                introduce_belief(comunication)
        self.perceived_area = self.get_perceived_area(environment.map, radius)
    def execute_rules(self):
        matched=True
        while matched:
            matched=False
            for rule in self.rules:
                if(not rule.done):
                    if rule.match(self): rule.do(self); rule.done=True;matched=True
        #limpiando reseteando las reglas para el proximo chequeo
        for rule in self.rules:
            rule.done=False
        
    
    def get_perceived_area(self, environment, radius):
        """
        Perceive an area around the agent with a given radius and update the agent's memory.
        :param environment: The grid representing the environment.
        :param radius: The radius of perception around the agent.
        :return: The perceived area within the given radius.
        """
        def get_beliefs_by_position(target_position):
            """
            Filters and returns a list of objects whose 'position' attribute matches the given tuple.
            :param objects: List of objects that have a 'position' attribute.
            :param target_position: Tuple (x, y) representing the target position.
            :return: List of objects whose 'position' matches the target_position.
            """
            return [obj for obj in self.beliefs if obj.position[0] == target_position[0] and obj.position[1] == target_position[1]]
        
        def update_belief_set(cell_value,pos):
            actual_position_beliefs=get_beliefs_by_position(pos) #*Deberia ser uno solo
            if len(actual_position_beliefs)==0 and cell_value!=' ':
                introduce_belief(self,Belief(cell_value,environment_stuff_types[cell_value],pos))
            for belief in actual_position_beliefs:
                if(cell_value==' '):
                    eliminate_belief(self,belief)
                else:
                    eliminate_belief(self,belief)
                    introduce_belief(self,Belief(cell_value,environment_stuff_types[cell_value],pos))

        x, y = self.position
        perceived = []

        # Calculate the boundaries of the perception area based on the radius
        for i in range(max(0, x - radius), min(self.grid_size, x + radius + 1)):
            row = []
            for j in range(max(0, y - radius), min(self.grid_size, y + radius + 1)):
                row.append(environment[i][j])
                self.memory[i][j] = environment[i][j]  # Update memory with perceived cells
                update_belief_set(environment[i][j],(i,j))
            perceived.append(row)

        return perceived
    
    
    def explore_unknown_area(agent):
        """ Moves the agent to the nearest unexplored area using a heuristic search. """
        unexplored = []
        for x in range(agent.grid_size):
            for y in range(agent.grid_size):
                if agent.memory[x][y] == '?':
                    unexplored.append((x, y))

        if unexplored:
            nearest_unexplored = min(unexplored, key=lambda u: agent.heuristic(u))
            return agent.move(nearest_unexplored,agent.memory)

        print("No unexplored areas left to explore!")
        return agent.position  # If no unexplored areas, stay in place
    
    def heuristic(self, pos):
        # Manhattan distance heuristic to the goal
        return abs(pos[0] - self.position[0]) + abs(pos[1] - self.position[1])
    
    
    def move(self, target,memory):
        """ Move the prey using A* search towards the target position. """
        path = self.a_star_search(target, memory)
        print("path found: ",path)
        if path and len(path) > 1:
            # Move one step along the path
            next_step = path[1]
            if self.is_valid_position(next_step, memory):
                self.position = list(next_step)
                print(f"Moved to {next_step}")
            else:
                print(f"Cannot move to {next_step}, it is blocked.")
        else:
            print("No valid path found")
    
    def is_valid_position(self, position, environment):
        """ Check if the position is valid (not water and not occupied by another prey). """
        x, y = position
        # Check if it's within bounds
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
        # Check if it's water
        if environment[x][y] == 'W':  # Assuming 'W' denotes water in the environment
            return False
        # Check if it's occupied by another prey
        # if environment[x][y] == f"{YELLOW}P{RESET}":  # Assuming 'W' denotes water in the environment
        #         return False
        return True
    def get_neighbors(self, position, environment):
        """ Get valid neighboring positions (up, down, left, right) that the prey can move to. """
        x, y = position
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]  # Adjacent cells

        # Filter out invalid positions (e.g., blocked cells or out of bounds)
        valid_neighbors = [n for n in neighbors if self.is_valid_position(n, environment)]
        return valid_neighbors
    
    def reconstruct_path(self, came_from, current):
        """ Reconstruct the path from the start to the current position. """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()  # Path was reconstructed backwards
        return total_path
    
    
    def a_star_search(self, target, environment):
        """ Use A* algorithm to find the shortest path to the target, avoiding blocked cells. """
        def heuristic(a, b):
            """ Heuristic function to estimate the distance between current node and target. """
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

        start = tuple(self.position)  # Starting position of the prey
        goal = tuple(target)  # Target position

        # Priority queue for the open set (nodes to be evaluated)
        open_set = []
        heapq.heappush(open_set, (0, start))

        # Dictionaries to store the best path and cost
        came_from = {}
        g_score = {start: 0}
        
        # Store the positions that have already been evaluated
        closed_set = set()

        while open_set:
            # Get the node with the lowest f-score (priority)
            current_f_score, current = heapq.heappop(open_set)

            x1, y1 = goal
            x2, y2 = current
            manhattan_distance = abs(x1 - x2) + abs(y1 - y2)
            # If we reached the goal, reconstruct the path
            if manhattan_distance==1:
                return self.reconstruct_path(came_from, current)

            closed_set.add(current)

            # Explore neighbors
            for neighbor in self.get_neighbors(current, environment):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + 1  # Assuming cost between adjacent nodes is 1

                # If the neighbor hasn't been evaluated or we found a better path
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

        # If no path is found
        #print(f"No valid path found to {target}")
        return None
    def pick(self,position,environment):
        x, y = position
        item=self.memory[x][y]
        self.inventory.append(item)
        environment[x][y]=' '
    def pick_water(self,position):
        self.thirst=100;
    def eat(self):
        index = next((i for i, element in enumerate(self.inventory) if element == 'F'), None)

        if index is not None:
            self.inventory.pop(index)  # Remove the element at the found index
        self.hunger=100
        
    
#******TESTING SECTION*****#    
# def print_environment(environment, prey_positions):
#     # Clear the console (works on most terminals)
#       # Clear screen for Windows ('cls') or Unix ('clear')
    
#     # Create a copy of the environment to add the prey
#     temp_env = [row[:] for row in environment]
    
#     for prey_position in prey_positions:
#     # Mark the prey's position with 'P'
#         x, y = prey_position
#         temp_env[x][y] = f"A"
    
#     # Print the grid
#     for row in temp_env:
#         print('.'.join(row))
#     print()

# environment = [
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     ['W', 'W', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', 'W', 'F', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', 'W', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     ['F', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
# ]
# testAgent=SurvivalAgent("Jhon",(11,0),27)

# introduce_belief(testAgent,Belief('fruta','food',(11,3)))
# while True:
#     os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen for Windows ('cls') or Unix ('clear')
#     testAgent.perceive(environment,testAgent.perception_radius)
#     #print_environment(environment,[testAgent.position])
#     print_environment(testAgent.memory,[testAgent.position])
#     for rule in testAgent.rules:
#         if rule.match(testAgent): rule.do(testAgent)
#     print('Inventario: ', testAgent.inventory)
#     print("Beliefs: ", [x.name for x in testAgent.beliefs])
#     print('Desires: ', [x.name for x in testAgent.desires])
#     desire_implying_intention=get_highest_ranked_desire(testAgent)
    
#     #!Convertir deseo en accion
    
#     if desire_implying_intention!=None: desire_action[desire_implying_intention.name](testAgent,desire_implying_intention.position,environment)
    
#     # if(testAgent.position[0]==11 and testAgent.position[1]==3):
#     #     testAgent.eat('apple')
#     #     print('Inventario: ', testAgent.inventory)
#     #     print("Sellego")
#     #     break
#     testAgent.desires.clear()
#     time.sleep(7)
#     #testAgent.move((11,3),testAgent.memory)
    
    