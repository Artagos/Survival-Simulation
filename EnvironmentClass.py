from RuleClass import Belief
class Environment:
    def __init__(self, grid_size, default_value=' '):
        """
        Initialize the environment with a 2D map (grid).
        :param grid_size: Tuple (width, height) of the grid.
        :param default_value: The default value for each cell in the grid (e.g., ' ' for empty space).
        """
        self.grid_size = grid_size
        self.map = [[default_value for _ in range(grid_size[1])] for _ in range(grid_size[0])]
        self.context:list[Belief]=[]

    def update_cell(self, x, y, value):
        """
        Update the value of a specific cell in the environment.
        :param x: The x-coordinate of the cell.
        :param y: The y-coordinate of the cell.
        :param value: The new value to place in the cell (e.g., 'W' for water, 'F' for food).
        """
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.map[x][y] = value
        else:
            print(f"Coordinates ({x}, {y}) are out of bounds!")

    def get_cell_value(self, x, y):
        """
        Get the value of a specific cell in the environment.
        :param x: The x-coordinate of the cell.
        :param y: The y-coordinate of the cell.
        :return: The value in the cell.
        """
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            return self.map[x][y]
        else:
            print(f"Coordinates ({x}, {y}) are out of bounds!")
            return None

    def display(self):
        """
        Display the current map of the environment.
        """
        for row in self.map:
            print('.'.join(row))
    def add_to_context(self,info:Belief):
        self.context.append(info)
# Example usage:

# # Create a 10x10 environment
# env = Environment((10, 10))

# # Update some cells with resources
# env.update_cell(2, 3, 'W')  # W for water
# env.update_cell(5, 6, 'F')  # F for food

# # Display the current state of the environment
# env.display()
