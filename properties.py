"""contains the properties for the program, pretty self explanatory"""


class Properties:
    """stores all the properties, has no methods"""

    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.columns = self.window_width // 20
        self.rows = self.window_height // 20
        self.box_width = self.window_width // self.columns  # floor division
        self.box_height = self.window_height // self.rows
        self.bg_color = (138, 154, 91)
        self.box_color = (4, 57, 39)
        self.pathcolor = (12, 4, 4)
        self.visitedcolor = (255, 138, 138)
        self.queuedcolor = (255, 79, 88)
        self.wallcolor = (255, 255, 255)
