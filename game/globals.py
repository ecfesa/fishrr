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
GAME_STATE_HYDRA = "hydra" # New game state for Hydra
GAME_STATE = GAME_STATE_TERMINAL # Initial game state

# Manual View Instance
MANUAL_VIEW_INSTANCE = None

# Hydra Game Instance
HYDRA_GAME_INSTANCE = None # Placeholder for Hydra game instance

# Discovered Commands (placeholder - this should ideally be loaded/saved or part of game progression)
DISCOVERED_COMMANDS = {"ls", "pwd", "cd", "exit", "cat", "help", "clear", "man"} # Added "man" to discovered
