import heapq
import time
import os

class Agent:
    def __init__(self, start, goal, grid_size):
        self.position = start
        self.goal = goal
        self.grid_size = grid_size
        self.memory = [['?' for _ in range(grid_size)] for _ in range(grid_size)]  # '?' means unexplored
        self.memory[start[0]][start[1]] = 'S'  # Starting position
    
    def heuristic(self, pos):
        # Manhattan distance heuristic to the goal
        return abs(pos[0] - self.goal[0]) + abs(pos[1] - self.goal[1])
    
    def get_perceived_area(self, environment, radius):
        """
        Perceive an area around the agent with a given radius and update the agent's memory.
        :param environment: The grid representing the environment.
        :param radius: The radius of perception around the agent.
        :return: The perceived area within the given radius.
        """
        x, y = self.position
        perceived = []

        # Calculate the boundaries of the perception area based on the radius
        for i in range(max(0, x - radius), min(self.grid_size, x + radius + 1)):
            row = []
            for j in range(max(0, y - radius), min(self.grid_size, y + radius + 1)):
                row.append(environment[i][j])
                self.memory[i][j] = environment[i][j]  # Update memory with perceived cells
            perceived.append(row)

        return perceived

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

    def explore_and_move(agent, target, environment):
        """ Move the agent towards the target or explore if path is blocked/unexplored. """
        
        def heuristic(a, b):
            """ Manhattan distance heuristic. """
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos):
            """ Get neighboring positions (up, down, left, right) within bounds. """
            x, y = pos
            neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            return [(nx, ny) for nx, ny in neighbors if 0 <= nx < 10 and 0 <= ny < 10]

        # Step 1: Update knowledge map with 3x3 perception
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                px, py = agent.position[0] + dx, agent.position[1] + dy
                if 0 <= px < 10 and 0 <= py < 10:
                    agent.memory[px][py] = environment[px][py]

        # Step 2: A* search on the known part of the map
        start = tuple(agent.position)
        goal = tuple(target)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        closed_set = set()

        while open_set:
            current_f, current = heapq.heappop(open_set)
            if current == goal:
                return agent.reconstruct_path(came_from, current)

            closed_set.add(current)

            for neighbor in get_neighbors(current):
                if neighbor in closed_set or agent.memory[neighbor[0]][neighbor[1]] == 'X':
                    continue  # Skip if already evaluated or blocked

                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

        # Step 3: If no path to the goal, switch to exploration
        return agent.explore_unknown_area(agent)

    def explore_unknown_area(agent):
        """ Moves the agent to the nearest unexplored area using a heuristic search. """
        unexplored = []
        for x in range(10):
            for y in range(10):
                if agent.memory[x][y] == '?':
                    unexplored.append((x, y))

        if unexplored:
            nearest_unexplored = min(unexplored, key=lambda u: agent.heuristic(agent.position, u))
            return agent.a_star_search(agent.position, nearest_unexplored, agent.memory)

        print("No unexplored areas left to explore!")
        return agent.position  # If no unexplored areas, stay in place
    def is_valid_position(self, position, environment):
        """ Check if the position is valid (not water and not occupied by another prey). """
        x, y = position
        # Check if it's within bounds
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
        # Check if it's water
        if environment[x][y] == 'X':  # Assuming 'W' denotes water in the environment
            return False

        return True

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

    def move(self, target,memory):
        """ Move the prey using A* search towards the target position. """
        path = self.a_star_search(target, memory)

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
        

# Example usage
grid_size = 10
environment = [
    [' ', ' ', ' ', 'X', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'X', ' ', 'X', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'X', ' ', 'X', ' ', ' ', ' ', 'X', 'X', ' '],
    [' ', 'X', ' ', 'X', ' ', ' ', ' ', ' ', 'X', ' '],
    [' ', ' ', ' ', 'X', 'X', ' ', ' ', ' ', 'X', ' '],
    [' ', ' ', ' ', 'X', ' ', ' ', ' ', ' ', 'X', ' '],
    ['X', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', 'X', 'X', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', 'X', ' ', ' ', 'X', 'X'],
    [' ', ' ', ' ', ' ', ' ', 'X', ' ', ' ', ' ', 'G']
]
def print_environment(environment, prey_positions):
    # Clear the console (works on most terminals)
      # Clear screen for Windows ('cls') or Unix ('clear')
    
    # Create a copy of the environment to add the prey
    temp_env = [row[:] for row in environment]
    
    for prey_position in prey_positions:
    # Mark the prey's position with 'P'
        x, y = prey_position
        temp_env[x][y] = f"A"
    
    # Print the grid
    for row in temp_env:
        print('.'.join(row))
    print()
agent = Agent(start=(0, 0), goal=(9, 9), grid_size=grid_size)

for _ in range(50):  # Simulate 50 steps
    os.system('cls' if os.name == 'nt' else 'clear')
    agent.get_perceived_area(environment,3)
    print_environment(environment,[agent.position])
    print_environment(agent.memory,[agent.position])
    if(agent.position[0]==agent.goal[0] and agent.position[1]==agent.goal[1]):
        print("Sellego")
        break
    agent.move(agent.goal,environment,agent.memory)
    time.sleep(2)
