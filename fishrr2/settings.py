import pygame
from enum import Enum

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fishrr")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (15, 25, 60)  # Darkened for battle background
DARK_BLUE = (10, 20, 50) # Further darkened 
GRAY = (200, 200, 200)
# LIGHT_BLUE = (173, 216, 230) # No longer primary background

# Casting Meter Colors & Zones
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

CAST_PERFECTION_ZONES = [
    {"min": 95, "max": 100, "label": "Perfect!", "color": GOLD, "line_color": BLACK},
    {"min": 85, "max": 94, "label": "Great!", "color": SILVER, "line_color": BLACK},
    {"min": 70, "max": 84, "label": "Good", "color": BRONZE, "line_color": BLACK}
    # Other areas will be the default green bar
]

# Game States
class GameState(Enum):
    IDLE = 0
    TUTORIAL = 1
    CASTING = 2
    WAITING = 3
    QTE = 4 # Quick Time Event
    BATTLE = 5
    RESULT = 6

# Fonts
try:
    font = pygame.font.Font("./JetBrainsMono-Regular.ttf", 36)
    small_font = pygame.font.Font("./JetBrainsMono-Regular.ttf", 18)
    tutorial_font = pygame.font.Font("./JetBrainsMono-Regular.ttf", 14)
except pygame.error as e:
    print(f"Font file not found or error loading font: {e}. Using default font.")
    font = pygame.font.Font(None, 74) # Fallback
    small_font = pygame.font.Font(None, 36) # Fallback
    tutorial_font = pygame.font.Font(None, 28) # Fallback 