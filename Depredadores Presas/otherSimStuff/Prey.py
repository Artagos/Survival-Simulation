import random
import os
import time
import heapq

# Define the environment (grid world)
GRID_SIZE = 27
FOOD_COUNT = 20
WATER_COUNT = 30

#for console printing
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'

SLEEP_AREA = (GRID_SIZE-1, GRID_SIZE-1)
PERCEPTION_RADIUS = 3  # The prey can only perceive a 3x3 area around itself

# Prey agent with reduced perception
class Prey:
    def __init__(self,name):
        # self.position = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        self.position =[11,0]
        self.hunger = 50  # Full hunger level
        self.thirst = 50  # Full thirst level
        self.energy = 50 
        self.name=name# Full energy level
        self.dead=False
        
        # Beliefs about food, water, and sleeping areas
        self.beliefs = {
            'food': [],
            'water': [],
        }
        
        # Desires: The agent desires to stay alive, requiring eating, drinking, and sleeping
        self.desires = {
            'eat': False,
            'drink': False,
            'sleep': False
        }
        self.visited = set()
        self.visited.add(tuple(self.position))

    def manhattan_distance(self,pos1, pos2):
        """ Calculate Manhattan distance between two points on a grid. """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def find_closest_resource(self, resource_list):
        """ Find the closest resource from the list of known resource positions. """
        if not resource_list:
            return None
        
        # Get the current position of the prey
        current_position = tuple(self.position)
        
        # Find the closest resource based on Manhattan distance
        closest_resource = min(resource_list, key=lambda r: self.manhattan_distance(current_position,r))
        
        return closest_resource
    def update_desires(self):
        """ Update desires based on the current state. """
        if self.hunger < 25:
            if not self.beliefs['food']:  # If no known food, desire to explore
                self.desires['explore'] = True
            else:
                self.desires['eat'] = True
                self.desires['explore'] = False
        else:
            self.desires['eat'] = False
        
        if self.thirst < 40:
            if not self.beliefs['water']:  # If no known water, desire to explore
                self.desires['explore'] = True
            else:
                self.desires['drink'] = True
                self.desires['explore'] = False
        else:
            self.desires['drink'] = False
            
        if self.energy < 50:
            self.desires['sleep'] = True
        else:
            self.desires['sleep'] = False
    
    def update_beliefs(self, environment):
        """ Update beliefs by perceiving only a small part of the environment around the prey. """
        x, y = self.position
        for i in range(max(0, x - PERCEPTION_RADIUS), min(GRID_SIZE, x + PERCEPTION_RADIUS + 1)):
            for j in range(max(0, y - PERCEPTION_RADIUS), min(GRID_SIZE, y + PERCEPTION_RADIUS + 1)):
                if environment[i][j] == 'F':  # Food location
                    if (i, j) not in self.beliefs['food']:
                        self.beliefs['food'].append((i, j))
                elif environment[i][j] == 'W':  # Water location
                    if (i, j) not in self.beliefs['water']:
                        self.beliefs['water'].append((i, j))

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

            # If we reached the goal, reconstruct the path
            if current == goal:
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
        print(f"No valid path found to {target}")
        return None

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

    def move(self, target, environment):
        """ Move the prey using A* search towards the target position. """
        path = self.a_star_search(target, environment)

        if path and len(path) > 1:
            # Move one step along the path
            next_step = path[1]
            if self.is_valid_position(next_step, environment):
                self.position = list(next_step)
                print(f"Moved to {next_step}")
            else:
                print(f"Cannot move to {next_step}, it is blocked.")
        else:
            print("No valid path found or already at target.")
        
    def is_valid_position(self, position, environment):
        """ Check if the position is valid (not water and not occupied by another prey). """
        x, y = position
        # Check if it's within bounds
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return False
        # Check if it's water
        if environment[x][y] == 'W':  # Assuming 'W' denotes water in the environment
            return False
        # Check if it's occupied by another prey
        if environment[x][y] == f"{YELLOW}P{RESET}":  # Assuming 'W' denotes water in the environment
                return False
        return True
        
    
    def explore(self,environment):
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Possible movements: up, down, left, right
        random.shuffle(moves)  # Shuffle moves to randomize exploration
        new_x=0;
        new_y=0;
        for move in moves:
            new_x = max(0, min(GRID_SIZE-1, self.position[0] + move[0]))
            new_y = max(0, min(GRID_SIZE-1, self.position[1] + move[1]))
            new_position = (new_x, new_y)
            
            # Move to this position if it hasn't been visited yet
            if (new_position not in self.visited and self.is_valid_position(new_position,environment)):
                self.position = [new_x, new_y]
                self.visited.add(new_position)  # Mark as visited
                return
        if(self.is_valid_position((new_x,new_y),environment)):
            self.position = [new_x, new_y]
            print("Can't move!! :(")   
        # If all neighboring locations have been visited, stay in place (or randomly backtrack)
        print("No new places to explore nearby, revisiting.")

    def one_step_away(self,pos1,pos2):
        if(abs(pos1[0]-pos2[0])<=1 and abs(pos1[1]-pos2[1])<=1 ):
            return True
        return False
    def act(self, environment):
        """ Perform actions based on desires. """
        if self.desires['eat'] and self.beliefs['food']:
            # Move towards food
            target = self.find_closest_resource(self.beliefs['food'])# Move towards the first known food source
            if self.one_step_away(tuple(self.position),target):
                print("Eating food at", target)
                environment[target[0]][target[1]] = ' '  # Remove the food from the environment
                self.hunger = 50  # Reset hunger level
                self.beliefs['food'].remove(target)
            else:# Remove from beliefs
                self.move(target,environment)
            # Eat if on the food

        elif self.desires['drink'] and self.beliefs['water']:
            # Move towards water
            target = self.find_closest_resource(self.beliefs['water'])  # Move towards the first known water source
            
            # Drink if on the water
            if self.one_step_away(tuple(self.position),target):
                print("Drinking water at", target)
                self.thirst = 50  # Reset thirst level
                self.beliefs['water'].remove(target)  # Remove from beliefs
            else:
                self.move(target,environment)
        
        elif self.desires.get('explore', False):
            print("Exploring...")
            self.explore(environment)

        elif self.desires['sleep']:
            # Move towards the sleeping area
            # target = self.beliefs['sleep_area']
            # self.move(target)
            # Sleep if at the sleeping area
                print("Sleeping at ", self.position)
                self.energy +=2  # Reset energy level
    def update_internal_state(self):
        """ Decrease hunger, thirst, and energy over time. """
        self.hunger -= 1
        self.thirst -= 1
        self.energy -= 1

# Create the environment with random food and water locations
def create_environment():
    environment = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['W', 'W', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', 'F', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'W', 'W', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
]

    # environment = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # # Place food randomly
    # for _ in range(FOOD_COUNT):
    #     x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    #     environment[x][y] = 'F'  # Food
    
    # # Place water randomly
    # for _ in range(WATER_COUNT):
    #     x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    #     environment[x][y] = 'W'  # Water
    
    return environment
# Function to print the environment and the prey position
def print_environment(environment, prey_positions):
    # Clear the console (works on most terminals)
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen for Windows ('cls') or Unix ('clear')
    
    # Create a copy of the environment to add the prey
    temp_env = [row[:] for row in environment]
    
    for prey_position in prey_positions:
    # Mark the prey's position with 'P'
        x, y = prey_position
        temp_env[x][y] = f"{YELLOW}P{RESET}"
    
    # Print the grid
    for row in temp_env:
        print('.'.join(row))
    print()

    # Optionally, add a small delay to make the updates easier to see
      # Sleep for half a second before the next update

# Simulation loop
def simulation(steps):
    environment = create_environment()
    #prey = Prey()
    prey_list = [Prey("P"+str(i)) for i in range(1)]
    deadArray=[]
    for step in range(steps):
        print_environment(environment,[x.position for x in prey_list])
        for prey in prey_list:
            if(not prey.dead):
                prey.update_beliefs(environment)  # Sense environment
                prey.update_desires()  # Update desires based on hunger, thirst, and energy levels
                prey.act(environment)  # Act on desires
                prey.update_internal_state()  # Update internal state (hunger, thirst, energy)
                # Check if the prey dies from hunger, thirst, or exhaustion
                if prey.hunger <= 0 or prey.thirst <= 0 or prey.energy <= 0:
                    print(f"The prey {prey.name} has died.")
                    prey.dead=True
                    deadArray.append(prey)
            print(f"Position: {prey.position}, Hunger: {prey.hunger}, Thirst: {prey.thirst}, Energy: {prey.energy}")
            print(f"Desires: {prey.desires}")
            print(f"Believes: {prey.beliefs}")
            
        print(f"\n--- Step {step + 1} ---")
        
        time.sleep(1)
    print([x.name if x.dead==True else None for x in deadArray])
    
# Run the simulation for 50 steps
if __name__ == "__main__":
    simulation(100)
