import game.system as system
import pygame

SYSTEM = system.System(65, 25)
SYSTEM.shell.add_auto_text("# You can copy files from the root directory to the backpack.")

PADDING = 20

WIDTH, HEIGHT = 800, 600
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GREEN = (0, 255, 0)
