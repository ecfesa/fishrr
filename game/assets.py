import os
import pygame

if not pygame.font.get_init():
    pygame.font.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "logo.png"))
LOGO_TRANSPARENT_64PX = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "logo_transparent_64px.png"))


KEYBOARD_SOUND = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "assets", "sounds", "keyboard.wav"))
KEYBOARD_SOUND.set_volume(1)

# Font setup
try:
    font_path = os.path.join(SCRIPT_DIR, "assets", "fonts", "JetBrainsMono-Regular.ttf")
    if os.path.exists(font_path):
        TERMINAL_FONT = pygame.font.Font(font_path, 16)
        TITLE_FONT = pygame.font.Font(font_path, 30) # Increased title font size
        BODY_FONT = pygame.font.Font(font_path, 14)
        EXAMPLE_FONT = pygame.font.Font(font_path, 13)
        HINT_FONT = pygame.font.Font(font_path, 14)
    else:
        # Final fallback to system fonts if custom font not available
        TERMINAL_FONT = pygame.font.SysFont("consolas", 16)
        TITLE_FONT = pygame.font.SysFont("consolas", 30) # Increased title font size
        BODY_FONT = pygame.font.SysFont("consolas", 14)
        EXAMPLE_FONT = pygame.font.SysFont("consolas", 13)
        HINT_FONT = pygame.font.SysFont("consolas", 14)
except:
    # Final fallback to system fonts if custom font not available
    TERMINAL_FONT = pygame.font.SysFont("consolas", 16)
    TITLE_FONT = pygame.font.SysFont("consolas", 30) # Increased title font size
    BODY_FONT = pygame.font.SysFont("consolas", 18)
    EXAMPLE_FONT = pygame.font.SysFont("consolas", 16)
    HINT_FONT = pygame.font.SysFont("consolas", 14)
