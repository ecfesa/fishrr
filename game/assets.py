import os
import pygame

if not pygame.font.get_init():
    pygame.font.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "logo.png"))
LOGO_TRANSPARENT_64PX = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "logo_transparent_64px.png"))
BULB_IMAGE = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "bulb.png"))

# Load the hydra warning image
HYDRA_WARNING_IMAGE = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "hydra_warning.png"))
# Load the hydra image
HYDRA_IMAGE = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "hydra.png"))
# Load the boat image
BOAT_IMAGE = pygame.image.load(os.path.join(SCRIPT_DIR, "assets", "images", "boat.png"))

KEYBOARD_SOUND = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "assets", "sounds", "keyboard.wav"))
KEYBOARD_SOUND.set_volume(1)

NEW_TIP_SOUND = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "assets", "sounds", "new_tip.wav"))
NEW_TIP_SOUND.set_volume(1)

# Dictionary to store loaded sounds
sounds = {}

def load_sounds():
    """Load all game sound effects and store them in the sounds dictionary"""
    sound_files = {
        'gameOver': os.path.join(SCRIPT_DIR, "assets", "sounds", "gameOver.wav"),
        'warning_storm': os.path.join(SCRIPT_DIR, "assets", "sounds", "warning_storm_waters.wav"),
        'warning_turbulence': os.path.join(SCRIPT_DIR, "assets", "sounds", "warning_turbulence.wav"),
        'startGame': os.path.join(SCRIPT_DIR, "assets", "sounds", "startGame.wav"),
        'hydra': os.path.join(SCRIPT_DIR, "assets", "sounds", "hydra.wav"),
        'missWind': os.path.join(SCRIPT_DIR, "assets", "sounds", "missWind.wav"),
        'halfWind': os.path.join(SCRIPT_DIR, "assets", "sounds", "halfWind.wav"),
        'fullWind': os.path.join(SCRIPT_DIR, "assets", "sounds", "fullWind.wav"),
        'victory': os.path.join(SCRIPT_DIR, "assets", "sounds", "startGame.wav")  # Reuse startGame sound for victory
    }
    
    # Load each sound into the dictionary
    for name, path in sound_files.items():
        try:
            sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
    
    # Set volume levels
    for sound_name, sound_obj in sounds.items(): # Iterate over items to use sound_name for specific volumes
        sound_obj.set_volume(0.15)  # Set default volume to 15%
    
    # Set specific volumes for certain sounds
    if 'gameOver' in sounds:
        sounds['gameOver'].set_volume(0.2)  # Game over is slightly louder
    if 'startGame' in sounds:
        sounds['startGame'].set_volume(0.2)  # Start game is slightly louder

# Call load_sounds to populate the dictionary when assets are loaded
load_sounds()

# Font constants for get_font and specific fonts
CUSTOM_FONT_FILENAME = "JetBrainsMono-Regular.ttf"
CUSTOM_FONT_PATH = os.path.join(SCRIPT_DIR, "assets", "fonts", CUSTOM_FONT_FILENAME)
FALLBACK_SYSTEM_FONT_NAME = "consolas"  # Consistent fallback from original assets.py

def get_font(size):
    """Load the custom font with the specified size.
    Falls back to a system font if the custom font fails to load."""
    try:
        # Pygame's font.Font will handle if path is incorrect or not a font file.
        return pygame.font.Font(CUSTOM_FONT_PATH, size)
    except pygame.error as e:
        print(f"Warning: Could not load custom font '{CUSTOM_FONT_PATH}' for size {size}. Error: {e}. "
              f"Using system font '{FALLBACK_SYSTEM_FONT_NAME}' instead.")
        try:
            return pygame.font.SysFont(FALLBACK_SYSTEM_FONT_NAME, size)
        except pygame.error as e_sys:
            print(f"Warning: Could not load system font '{FALLBACK_SYSTEM_FONT_NAME}' for size {size}. Error: {e_sys}. "
                  f"Using Pygame default font.")
            return pygame.font.Font(None, size) # None for Pygame's default font

# Font setup using the new get_font function
TERMINAL_FONT = get_font(16)
TITLE_FONT = get_font(30)
BODY_FONT = get_font(14)
EXAMPLE_FONT = get_font(13)
HINT_FONT = get_font(14)
