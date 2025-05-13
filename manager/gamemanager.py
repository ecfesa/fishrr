import pygame

class GameManager:

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_level_index = 0
        self.levels = []
        self.current_level = None
        self.running = False

    # Level Initializer
    def set_levels(self, level_classes):
        self.levels = level_classes
        self.load_level(self.current_level_index)

    # Level Loader
    def load_level(self, index):

        print("loading level: ", index+1)

        if index < len(self.levels):
            self.current_level = self.levels[index]
        else:
            self.running = False

    # Next Level Loader
    def next_level(self):
        self.current_level_index += 1
        self.load_level(self.current_level_index)

    # Quit Game
    def quit_game(self):
        self.running = False
