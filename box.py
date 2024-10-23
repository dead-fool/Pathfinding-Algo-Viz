"""Contains the Class Box which represents the state of each cell in the grid"""

import pygame
# pygame is imported to use pygame.draw function


class Box:
    """Box class to model each cell in the grid"""

    def __init__(self, visualizer, i, j):
        self.x = i  # x index
        self.y = j  # y index
        self.grid = visualizer.grid  # create local variable from global
        self.properties = visualizer.properties  # create local variable from global
        self.width = self.properties.box_width  # width of each cell
        self.height = self.properties.box_height  # height of each cell
        self.color = self.properties.box_color  # default colour of blocks, dark green
        self.window = visualizer.window  # create local variable from global
        self._init_flags()
        self.neighbours = []  # array to store every neighbouring box that arent walls
        # to track where this box is accessed from, used for backtracking to find path
        self.prior = None

    def _init_flags(self):
        """initializes the state flags of the box"""
        self.start = False  # set if the box is start node
        self.wall = False  # set if the box is wall node
        self.target = False  # set if the box is target node
        # algorithm flags
        self.queued = False  # the box which is currently in the queue
        self.visited = False  # previously queued and moved on box

    def set_neighbours(self):
        """sets every neighbouring boxes which aren't walls and within the boundary"""

        # if box isn't in left boundary, set left
        if self.x > 0:
            if not self.grid[self.x - 1][self.y].wall:
                self.neighbours.append(self.grid[self.x - 1][self.y])

        # if box isn't in right boundary, set right
        if self.x < self.properties.columns - 1:
            if not self.grid[self.x + 1][self.y].wall:
                self.neighbours.append(self.grid[self.x + 1][self.y])

        # if box isn't in top boundary, set up
        if self.y > 0:
            if not self.grid[self.x][self.y - 1].wall:
                self.neighbours.append(self.grid[self.x][self.y - 1])

        # if box isn't in bottom boundary, set down
        if self.y < self.properties.rows - 1:
            if not self.grid[self.x][self.y + 1].wall:
                self.neighbours.append(self.grid[self.x][self.y + 1])

    def heuristic_func(self, target):
        """heuristic function used in Astar that returns the L distance from box to target node"""
        xdist = abs(target.x - self.x)
        ydist = abs(target.y - self.y)
        return xdist + ydist

    def draw(self, color):
        """function to draw box to the screen, called externally from visualizerapp"""
        if self.x >= 0 and self.y >= 0:
            pygame.draw.rect(self.window, color, (self.x * self.width,
                                                  self.y * self.height, self.width - 1, self.height - 1))

    def reset(self):
        """resets box type flags"""
        self.start = False
        self.wall = False
        self.target = False

    def resetwall(self):
        """resets wall"""
        self.wall = False

    def resetflags(self):
        """resets algorithm states of box"""
        self.queued = False
        self.visited = False

    def resetvalues(self):
        """resets algorithm properties of box"""
        self.neighbours = []
        self.prior = None

    def resetsrcdest(self):
        """resets start, wall, target"""
        self.start = False
        self.wall = False
        self.target = False
