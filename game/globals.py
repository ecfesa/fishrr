import game.system as system
import pygame
from game.state import GameState

SYSTEM = system.System(75, 25)
PADDING = 20

WIDTH, HEIGHT = 800, 600
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GREEN = (0, 255, 0)

# Game States
GAME_STATE_TERMINAL = "terminal"
GAME_STATE_MANUAL = "manual"
GAME_STATE = GAME_STATE_TERMINAL # Initial game state

# Manual View Instance
MANUAL_VIEW_INSTANCE = None

# Discovered Commands (placeholder - this should ideally be loaded/saved or part of game progression)
DISCOVERED_COMMANDS = {"ls", "pwd", "cd", "exit", "cat", "help", "clear", "man"} # Added "man" to discovered
