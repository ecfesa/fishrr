import pygame
import sys
from fishing.example_scene import run_fishing_scene

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
font_path = "font/JetBrainsMono-Regular.ttf"
pygame.display.set_caption("Fishing Game")

# Load font
font = pygame.font.Font(font_path, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Run the fishing scene
caught_items = run_fishing_scene(screen, font_path)

