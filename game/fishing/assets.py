import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT # For potential scaling
import os
# Asset paths
# Construct path relative to this file (assets.py)
# Assumes images are in fishrr/game/assets/images/
_assets_py_dir = os.path.dirname(__file__)
ASSET_PATH = os.path.join(_assets_py_dir, "..", "assets", "images") 
# IMAGE_PATH = "./assets/images/" # Not used if all are in ./assets/
# SOUND_PATH = "./assets/sounds/" # For future use

# Function to load an image, optionally with scaling
def load_image(filename: str, scale: tuple[int, int] | None = None, use_alpha: bool = False):
    """Loads an image, converts it (with alpha for transparency), and optionally scales it."""
    try:
        # Ensure the full path to the image is used
        full_image_path = os.path.join(ASSET_PATH, filename)
        image = pygame.image.load(full_image_path)
    except pygame.error as message:
        print(f"Cannot load image from {full_image_path}: {message}")
        # Return a placeholder surface or raise error, depending on desired handling
        # For now, let's create a small red square as a fallback visual cue
        fallback_surface = pygame.Surface((30, 30) if not scale else scale)
        fallback_surface.fill((255,100,100)) # Bright red, noticeable
        pygame.draw.line(fallback_surface, (0,0,0), (0,0), fallback_surface.get_size(), 2)
        pygame.draw.line(fallback_surface, (0,0,0), (0,fallback_surface.get_height()), (fallback_surface.get_width(),0), 2)
        return fallback_surface # Return placeholder
        # raise SystemExit(message) # Alternatively, re-raise to halt if assets are critical

    if use_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if scale:
        image = pygame.transform.scale(image, scale)
    
    return image

CLOSE_BAIT_SPRITE = None
MID_BAIT_SPRITE = None
LONG_BAIT_SPRITE = None

CLOSE_CATCH_SPRITE = None
MID_CATCH_SPRITE = None
LONG_CATCH_SPRITE = None

CASTING_SPRITE = None

# Additional sprites that drawing.py expects (initialize as None)
PLAYER_IDLE_SPRITE = None
FISH_ICON_PLACEHOLDER = None
TRASH_ICON_PLACEHOLDER = None

def load_all_assets():
    global CLOSE_BAIT_SPRITE, MID_BAIT_SPRITE, LONG_BAIT_SPRITE
    global CLOSE_CATCH_SPRITE, MID_CATCH_SPRITE, LONG_CATCH_SPRITE
    global CASTING_SPRITE
    global PLAYER_IDLE_SPRITE, FISH_ICON_PLACEHOLDER, TRASH_ICON_PLACEHOLDER

    print("Loading assets...")
    try:
        # Example: PLAYER_IDLE_SPRITE = load_image("player_idle.png", scale=(100,150))
        # Example: FISH_ICON_PLACEHOLDER = load_image("fish_icon.png", scale=(30,30))
        # Example: TRASH_ICON_PLACEHOLDER = load_image("trash_icon.png", scale=(30,30))

        CLOSE_BAIT_SPRITE = load_image("close_bait_throw.png", scale=(100, 150))
        MID_BAIT_SPRITE = load_image("mid_bait_throw.png", scale=(100, 150))
        LONG_BAIT_SPRITE = load_image("long_bait_throw.png", scale=(100, 150))

        CLOSE_CATCH_SPRITE = load_image("battle_close.png", scale=(100, 150))
        MID_CATCH_SPRITE = load_image("battle_mid.png", scale=(100, 150))
        LONG_CATCH_SPRITE = load_image("battle_long.png", scale=(100, 150))

        CASTING_SPRITE = load_image("swing_bait.png", scale=(100, 150))
        
        print("Assets loaded successfully.")
    except Exception as e:
        print(f"Error during asset loading: {e}")
        # Game can still run with placeholder surfaces if load_image returns them

# Call load_all_assets() early in your game, e.g., in main.py after settings are imported.

# Placeholder for loaded assets (sprites, images, sounds)
# Example: PLAYER_SPRITE = load_image("player.png", (50, 70))
# FISH_ICONS = {
# "Sardine": load_image("sardine_icon.png", (30,30)),
# "Tuna": load_image("tuna_icon.png", (40,40)),
# }
# BACKGROUND_OCEAN = load_image("ocean_bg.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT), use_alpha=False)

# It's good practice to load all assets once at the start of the game 
# and store them in variables or dictionaries for easy access.

# Example of how you might initialize them in your main game setup:
# def load_all_assets():
# global PLAYER_SPRITE, FISH_ICONS, BACKGROUND_OCEAN
# PLAYER_SPRITE = load_image("player.png", (50, 70))
# FISH_ICONS = {
# "Sardine": load_image("sardine_icon.png", (30,30)),
# "Tuna": load_image("tuna_icon.png", (40,40)),
# }
# BACKGROUND_OCEAN = load_image("ocean_bg.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT), use_alpha=False)
# print("Assets loaded.")

# Call load_all_assets() once in your main.py after pygame.init() 