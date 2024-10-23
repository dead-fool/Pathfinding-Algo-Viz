from queue import Queue
from queue import PriorityQueue
import math
import random
import sys

from tkinter import messagebox, Tk
import pygame
import pygame.font


from properties import Properties
from box import Box
from button import Button


class VisualizerApp:
    """the main class to perform all the tasks"""

    def __init__(self):

        self.properties = Properties()
        pygame.init()  # initializes pygame
        self.window = pygame.display.set_mode(
            (self.properties.window_width, self.properties.window_height))
        pygame.display.set_caption("VISUALIZER.ALGO")
        game_icon = pygame.image.load(
            'images/gameicon.jpg')  # icon on the window title
        pygame.display.set_icon(game_icon)
        self._init_images()  # Initializes all the images to be used at the start
        self._init_variables()
        self._create_grid()  # creates grid of boxes
        self.homescreen = True  # first land on home menu
        self.helpscreen = False  # displays help screen when true
        # initializes buttons for the homescreen
        self.start_custom = Button(self, 'start  custom')
        self.start_random = Button(self, 'start  random')
        self.help_button = Button(self, 'help')
        self.exit_button = Button(self, 'exit')

    def _init_variables(self):
        # initializes various variables
        self.grid = []  # array to store grid of boxes
        # to store startbox, initially no so garbage index -1, -1
        self.start_box = Box(self, -1, -1)
        self.target_box = Box(self, -1, -1)  # to store targetbox
        self.target_loc = []  # to store target box location
        self.start_loc = []  # to store start box location
        self.start_box_set = False  # true when start node is set
        self.target_box_set = False  # true when target node is set
        self.searching = False  # true when algorithm is running
        self.completed = False  # true when algorithm has just finished running
        # sets appropriate true when chosen
        self.begin_search = {'dijk': False, 'astar': False}
        self.queue = Queue()  # queue used in dijkstra's
        self.path = []  # path to store the shortest path through backtracking

    def _reset_algo_variables(self):
        # resets the algorithm variables
        self.queue = Queue()
        self.path = []
        # resets the grid, by resetting flags of each boxes through iteration
        for i in range(self.properties.columns):
            for j in range(self.properties.rows):
                self.grid[i][j].resetflags()
                self.grid[i][j].resetvalues()

    def _init_images(self):
        """initializes all the images needed"""

        self.start_icon = pygame.image.load('images/home.png')
        self.start_icon = pygame.transform.scale(
            self.start_icon, (self.properties.box_width, self.properties.box_height))
        self.target_icon = pygame.image.load('images/target.png')
        self.target_icon = pygame.transform.scale(
            self.target_icon, (self.properties.box_width, self.properties.box_height))
        self.homescreen_img = pygame.image.load('images/landing.png')
        self.helpscreen_img = pygame.image.load('images/help.png')

    def _create_grid(self):
        """creates a grid of boxes when the program starts"""
        for i in range(self.properties.columns):
            arr = []
            for j in range(self.properties.rows):
                arr.append(Box(self, i, j))
            self.grid.append(arr)

    def _set_neighbours(self):
        """calls set neighbours for every box in the grid"""
        for i in range(self.properties.columns):
            for j in range(self.properties.rows):
                self.grid[i][j].set_neighbours()

    def run_app(self):
        """main program loop"""
        while True:
            if self.homescreen:
                # checks hover buttons for homescreen
                self._check_hover()
            self._checkevents()
            if self.homescreen and not self.helpscreen:
                # calls appropriate actions if any buttons selected
                self._click_action()  # function only for home buttons click
            # changes here
            if self.begin_search:
                if self.begin_search['dijk']:
                    self._run_dijkstra()
                elif self.begin_search['astar']:
                    self._run_A_star()
            self._updatescreen()

    def _checkevents(self):
        for event in pygame.event.get():
            # quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # while algorithm is running dont take inputs
            if self.searching:
                continue

            # allows drag n draw to create walls
            elif event.type == pygame.MOUSEMOTION:
                mouse_x = pygame.mouse.get_pos()[0]
                mouse_y = pygame.mouse.get_pos()[1]

                if event.buttons[0]:
                    if not self.homescreen:
                        self._mouse_event_createwall(mouse_x, mouse_y)

            # checks all types of clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if we proceed to modify maze after an algorithm has run, it resets the visited queued visualization
                if self.completed:
                    self._reset_algo_variables()

                # when we click in homescreen, check if any buttons are clicked
                if self.homescreen:
                    self._buttoncheck()
                # gets mouse coordinates when clicked
                mouse_x = pygame.mouse.get_pos()[0]
                mouse_y = pygame.mouse.get_pos()[1]
                if not self.homescreen:
                    # while in grid
                    if pygame.mouse.get_pressed()[0]:
                        self._mouse_event_leftclick(mouse_x, mouse_y)
                    elif pygame.mouse.get_pressed()[2]:
                        self._mouse_event_rightclick(mouse_x, mouse_y)

            if event.type == pygame.KEYDOWN and not self.searching:
                if event.key == pygame.K_ESCAPE:  # back to homescreen from anywhere
                    self.homescreen = True
                    self.helpscreen = False

            if event.type == pygame.KEYDOWN and self.target_box_set and self.start_box_set and not self.searching and not self.homescreen:
                # user input to run the algorithms according to choice

                if event.key == pygame.K_1:
                    self.begin_search['dijk'] = True
                    self.completed = False
                    self._reset_algo_variables()
                    self._init_Dijkstra()
                elif event.key == pygame.K_2:
                    self.begin_search['astar'] = True
                    self.completed = False
                    self._reset_algo_variables()
                    self._init_A_star()

    def _click_action(self):
        """function to perform appropriate button click action"""
        if self.exit_button.selected:
            pygame.quit()
            sys.exit()

        elif self.help_button.selected:
            self.helpscreen = True
            # action is performed , so reset
            self.help_button.selected = False

        elif self.start_custom.selected:
            self.homescreen = False
            self._reset_algo_variables()
            for i in range(self.properties.columns):
                for j in range(self.properties.rows):
                    self.grid[i][j].resetwall()
            # action is performed so reset
            self.start_custom.selected = False

        elif self.start_random.selected:
            self.homescreen = False
            self._reset_algo_variables()
            self._resetgrid()
            self._init_randomgrid()
            # action is performed so reset
            self.start_random.selected = False

    def _check_hover(self):
        # resets every button hover property to false first
        self._hover_reset()

        # logic is , if mouse position overlaps button rectangle, then it is hovered over
        if self.start_random.rect.collidepoint(pygame.mouse.get_pos()) and not self.start_random.selected:
            self.start_random.hover = True

        elif self.start_custom.rect.collidepoint(pygame.mouse.get_pos()) and not self.start_custom.selected:
            self.start_custom.hover = True

        elif self.help_button.rect.collidepoint(pygame.mouse.get_pos()) and not self.help_button.selected:
            self.help_button.hover = True

        elif self.exit_button.rect.collidepoint(pygame.mouse.get_pos()) and not self.exit_button.selected:
            self.exit_button.hover = True

    def _buttoncheck(self):
        """when mouse is clicked in home screen, this checked if the position of click
        overlaps any of the button rectangle"""
        if self.start_random.rect.collidepoint(pygame.mouse.get_pos()):
            self.start_random.selected = True

        elif self.start_custom.rect.collidepoint(pygame.mouse.get_pos()):
            self.start_custom.selected = True

        elif self.help_button.rect.collidepoint(pygame.mouse.get_pos()):
            self.help_button.selected = True

        elif self.exit_button.rect.collidepoint(pygame.mouse.get_pos()):
            self.exit_button.selected = True

    def _hover_reset(self):
        """resets every button hover properties to false before checking hover in each loop"""

        self.start_random.hover = False
        self.start_custom.hover = False
        self.help_button.hover = False
        self.exit_button.hover = False

    def _init_A_star(self):
        """initializes all the variables required for running A start algorithm"""
        # this function is called when user presses key to run A star

        self.searching = True  # algorithm has started
        self._set_neighbours()  # sets neighbour for every boxes in grid
        self.count = 0
        self.priority_queue = PriorityQueue()
        self.priority_queue.put((0, self.count, self.start_box))
        self.prior = {}
        # g_score = total score ie f_score + h_score; minimum traversed first
        # initialzed to infinity for every box first
        self.g_score = {Box: math.inf for row in self.grid for Box in row}
        self.g_score[self.start_box] = 0

        # f_score is also initialized to infinity for every points first
        self.f_score = {Box: math.inf for row in self.grid for Box in row}

        # for start box f_score = h_score
        self.f_score[self.start_box] = self.start_box.heuristic_func(
            self.target_box)

        # add start box to open set
        self.open_set = {self.start_box}

    def _run_A_star(self):
        """A star implementation"""

        if not self.priority_queue.empty() and self.searching:
            current_box = self.priority_queue.get()[2]
            self.open_set.remove(current_box)
            if current_box == self.target_box:
                # path found
                self.searching = False
                self.completed = True
                self.begin_search['astar'] = False
                # generating path through backtracking
                while current_box in self.prior:
                    current_box = self.prior[current_box]
                    self.path.append(current_box)

            for neighbor in current_box.neighbours:
                # add neighbours of the current visited node to queue
                # calculate scores of neighbours
                temp_g_score = self.g_score[current_box] + 1
                if temp_g_score < self.g_score[neighbor]:
                    self.prior[neighbor] = current_box
                    self.g_score[neighbor] = temp_g_score
                    self.f_score[neighbor] = temp_g_score + \
                        neighbor.heuristic_func(self.target_box)
                    if neighbor not in self.open_set:
                        self.count += 1
                        self.priority_queue.put(
                            (self.f_score[neighbor], self.count, neighbor))
                        self.open_set.add(neighbor)
                        if neighbor != self.target_box:
                            neighbor.queued = True
            if current_box != self.start_box:
                current_box.visited = True

        else:
            if self.searching:
                # this means every node already visited, target not reached, algorithm running
                # in other words,no solution
                self.searching = False
                self.completed = True
                self.begin_search['astar'] = False
                self._no_solution_prompt()

    def _no_solution_prompt(self):
        """displays message box with no solution prompt"""

        self._reset_algo_variables()
        Tk().wm_withdraw()
        messagebox.showinfo("No Solution", "There is no solution!")

    def _init_Dijkstra(self):
        """initializes the variables needed for dijkstra's algorithm"""
        # called when user enters key to run dijkstra'self

        self.searching = True
        self.prior = {}  # set to store all the previous nodes for backtracking
        self._set_neighbours()
        self.queue.put(self.start_box)  # start box is added to queue first
        self.start_box.queued = True

    def _run_dijkstra(self):
        """algorithm implementation of dijkstra's"""

        if self.queue.qsize() > 0 and self.searching:
            current_box = self.queue.get_nowait()
            current_box.visited = True
            if current_box == self.target_box:
                # solution found
                self.searching = False
                self.completed = True
                self.begin_search['dijk'] = False
                # generate path through backtracking
                while current_box in self.prior:
                    current_box = self.prior[current_box]
                    self.path.append(current_box)

            else:
                for neighbour in current_box.neighbours:
                    # add neighbours of the current visited node to queue
                    if not neighbour.queued:
                        neighbour.queued = True
                        self.prior[neighbour] = current_box
                        self.queue.put_nowait(neighbour)
        else:
            if self.searching:
                # this means every node already visited, target not reached, algorithm running
                # in other words,no solution
                self.searching = False
                self.completed = True
                self.begin_search['dijk'] = False
                self._no_solution_prompt()

    def _resetgrid(self):
        """resets every wall set in the grid"""

        for i in range(self.properties.columns):
            for j in range(self.properties.rows):
                self.grid[i][j].resetwall

    def _init_randomgrid(self):
        """initializes random maze"""

        for i in range(self.properties.columns):
            for j in range(self.properties.rows):
                self.grid[i][j].wall == False  # first every box is not wall
                if self.grid[i][j].start == True:
                    continue  # start node shouldn't be overwritten by wall
                elif self.grid[i][j].target == True:
                    continue  # target node shouldn't be overwritten by wall
                else:
                    self.grid[i][j].wall = self._get_randomwall()
                    # if empty then get boolean value for wall through this function

    def _get_randomwall(self):
        """randomly decides whether wall should be set or not by returning true or false"""

        n = random.randint(1, 100)
        if n % 5 <= 2:
            n = random.randint(1, 2)
            if n == 1:
                return False
            if n == 2:
                return True
        else:
            return False

    def _mouse_event_createwall(self, x, y):
        """if mouse is left clicked and dragged after start node set"""

        index_i = x // self.properties.box_width
        index_j = y // self.properties.box_height
        if self.start_box_set:
            if not self.grid[index_i][index_j].target:  # to avoid overwriting
                if not self.grid[index_i][index_j].start:  # to avoid overwriting
                    if not self.grid[index_i][index_j].wall:  # to avoid overwriting
                        self.grid[index_i][index_j].wall = True

    def _mouse_event_leftclick(self, x, y):
        """to set start node or to make wall or clear wall without dragging"""

        index_i = x // self.properties.box_width
        index_j = y // self.properties.box_height
        if not self.start_box_set:
            # draw start , changes here
            if self.grid[index_i][index_j].wall == False and self.grid[index_i][index_j].target == False:
                self._select_start_box(index_i, index_j)

        elif self.grid[index_i][index_j].start:
            # to unselect start node
            self._unselect_start_box(index_i, index_j)

        else:
            # draw wall, toggles the state
            if not self.grid[index_i][index_j].target:
                if not self.grid[index_i][index_j].start:
                    self.grid[index_i][index_j].reset()

    def _select_start_box(self, i, j):
        """to set appropriate vales to necessary variables when start node is set"""

        self.start_box = self.grid[i][j]
        self.grid[i][j].start = True
        self.start_loc.append(i)
        self.start_loc.append(j)
        self.start_box.start = True
        self.start_box_set = True

    def _unselect_start_box(self, i, j):
        """to set appropriate vales to necessary variables when start node is reset"""

        self.start_box = None
        self.grid[i][j].reset()
        self.start_loc.pop()
        self.start_loc.pop()
        self.start_box_set = False

    def _mouse_event_rightclick(self, x, y):
        """function to select target node"""

        index_i = x // self.properties.box_width
        index_j = y // self.properties.box_height
        if not self.target_box_set:  # avoid overwriting
            # avoid overwriting
            if self.grid[index_i][index_j].wall == False and self.grid[index_i][index_j].start == False:
                self.target_box = self.grid[index_i][index_j]
                self.grid[index_i][index_j].target = True
                self.target_loc.append(index_i)
                self.target_loc.append(index_j)
                self.target_box.target = True
                self.target_box_set = True

        # reset target node when it is rightclicked and selected
        elif self.grid[index_i][index_j].target:
            self.target_box = None
            self.grid[index_i][index_j].reset()
            self.target_loc.pop()
            self.target_loc.pop()
            self.target_box_set = False

    def _updatescreen(self):
        """main display function to update screen in each main loop iteration"""

        if not self.homescreen:
            # when we enter grid
            self.window.fill(self.properties.bg_color)
            self._drawGrid()
            if self.start_box_set:
                self._draw_starticon()
            if self.target_box_set:
                self._draw_targeticon()
        else:
            # home screen
            self._displayhomescreen()
            if not self.helpscreen:
                self._displayhomebuttons()
            if self.helpscreen:
                # help screen
                self._displayhelpscreen()
        pygame.display.flip()  # update screen with new display(next frame)

    def _displayhelpscreen(self):
        """method to display the help screen"""

        helpscreenrect = self.helpscreen_img.get_rect()
        helpscreenrect.center = self.window.get_rect().center
        self.window.blit(self.helpscreen_img, helpscreenrect)

    def _displayhomescreen(self):
        """function to display the homescreen"""

        homescreenrect = self.homescreen_img.get_rect()
        homescreenrect.center = self.window.get_rect().center
        self.window.blit(self.homescreen_img, homescreenrect)

    def _displayhomebuttons(self):
        """functions to display the home buttons"""

        self.start_custom.draw_button()
        self.start_random.draw_button()
        self.help_button.draw_button()
        self.exit_button.draw_button()

    def _drawGrid(self):
        """function to draw grid by drawing each boxes in the grid"""

        for i in range(self.properties.columns):
            for j in range(self.properties.rows):
                box = self.grid[i][j]
                box.draw(self.properties.box_color)
                # to set different color for different types of boxes
                if box.wall:
                    box.draw(self.properties.wallcolor)

                if box.queued:
                    box.draw(self.properties.queuedcolor)

                if box.visited:
                    box.draw(self.properties.visitedcolor)

                if box in self.path:
                    box.draw(self.properties.pathcolor)

    def _draw_starticon(self):
        """to draw the home picture in the start node box"""

        if self.start_box_set:
            start_rect = self.start_icon.get_rect()  # create rectangle
            # align
            start_rect.left = self.window.get_rect(
            ).left + self.start_loc[0] * self.properties.box_width

            start_rect.top = self.window.get_rect(
            ).top + self.start_loc[1] * self.properties.box_height
            # paste to the screen
            self.window.blit(self.start_icon, start_rect)

    def _draw_targeticon(self):
        if self.target_box_set:
            target_rect = self.target_icon.get_rect()  # create rectangle
            # align
            target_rect.left = self.window.get_rect(
            ).left + self.target_loc[0] * self.properties.box_width
            target_rect.top = self.window.get_rect(
            ).top + self.target_loc[1] * self.properties.box_height
            # paste to the screen
            self.window.blit(self.target_icon, target_rect)
