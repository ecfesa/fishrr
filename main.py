import pygame
import sys

from levels import level1
from levels import level2
from manager.gamemanager import GameManager
from manager import constantmanager
from components.game import Game

from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Initial Config

# Game Manager Config
screen = pygame.display.set_mode((constantmanager.WINDOW_WIDTH, constantmanager.WINDOW_HEIGHT))
pygame.display.set_caption(constantmanager.TITLE)
gamemanager = GameManager(screen)

level_classes = [level1.Level1, level2.Level2]
gamemanager.set_levels(level_classes)

if __name__ == "__main__":
    game = Game(gamemanager)
    game.run() 
