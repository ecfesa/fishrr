import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Dictionary to store loaded sounds
sounds = {}

def load_sounds():
    """Load all game sound effects and store them in the sounds dictionary"""
    sound_files = {
        'gameOver': "sounds/gameOver.wav",
        'warning_storm': "sounds/warning_storm_waters.wav",
        'warning_turbulence': "sounds/warning_turbulence.wav",
        'startGame': "sounds/startGame.wav",
        'hydra': "sounds/hydra.wav",
        'missWind': "sounds/missWind.wav",
        'halfWind': "sounds/halfWind.wav",
        'fullWind': "sounds/fullWind.wav",
        'victory': "sounds/startGame.wav"  # Reuse startGame sound for victory
    }
    
    # Load each sound into the dictionary
    for name, path in sound_files.items():
        try:
            sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
    
    # Set volume levels
    for sound in sounds.values():
        sound.set_volume(0.15)  # Set default volume to 15%
    
    # Set specific volumes for certain sounds
    if 'gameOver' in sounds:
        sounds['gameOver'].set_volume(0.2)  # Game over is slightly louder
    if 'startGame' in sounds:
        sounds['startGame'].set_volume(0.2)  # Start game is slightly louder

def play_sound(sound_name, volume=None):
    """Play a sound by name with optional volume override"""
    # Make sure to add .wav extension if not already present and it's not a key in sounds
    if sound_name not in sounds:
        if not sound_name.endswith('.wav'):
            sound_name += '.wav'
        try:
            # Create a temporary sound object
            sound = pygame.mixer.Sound(f"sounds/{sound_name}")
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(0.15)  # Default volume
            sound.play()
        except FileNotFoundError:
            print(f"Warning: Sound file 'sounds/{sound_name}' not found")
        except Exception as e:
            print(f"Error playing sound: {e}")
    else:
        # Use the preloaded sound
        if volume is not None:
            # Store the original volume
            original_volume = sounds[sound_name].get_volume()
            # Set the new volume temporarily
            sounds[sound_name].set_volume(volume)
            # Play the sound
            sounds[sound_name].play()
            # Schedule a reset of the volume (in main loop)
            return original_volume
        else:
            # Play with current volume
            sounds[sound_name].play()
            return None 