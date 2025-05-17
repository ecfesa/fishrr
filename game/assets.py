import os
import pygame

if not pygame.font.get_init():
    pygame.font.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "logo.png"))
LOGO_TRANSPARENT_64PX = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "logo_transparent_64px.png"))

TERMINAL_FONT = pygame.font.Font(os.path.join(SCRIPT_DIR, "assets", "fonts", "JetBrainsMono-Regular.ttf"), 16)

KEYBOARD_SOUND = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "assets", "sounds", "keyboard.wav"))
KEYBOARD_SOUND.set_volume(1)
