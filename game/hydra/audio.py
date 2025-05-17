import pygame
from game.assets import sounds # Import the sounds dictionary

# Initialize pygame mixer
pygame.mixer.init() # This might be redundant if assets.py already does it, but safe to keep.

# Dictionary to store loaded sounds - REMOVED as it's now in assets.py
# sounds = {}

# load_sounds() function - REMOVED as it's now in assets.py
# def load_sounds():
# ... (original load_sounds content removed)

def play_sound(sound_name, volume=None):
    """Play a sound by name with optional volume override"""
    # Make sure to add .wav extension if not already present and it's not a key in sounds
    if sound_name not in sounds:
        # This part of the logic might need adjustment if we strictly want to use preloaded sounds.
        # For now, it attempts to load a sound dynamically if not found in the preloaded dictionary.
        # Consider if dynamic loading from a fixed 'sounds/' path is desired or if all sounds must be preloaded.
        if not sound_name.endswith('.wav'):
            sound_name_with_ext = sound_name + '.wav'
        else:
            sound_name_with_ext = sound_name
        
        # Construct path relative to a potential 'sounds' directory or adjust as needed.
        # This path construction might be problematic if the script's CWD is not what's expected.
        # It's generally better to load all required sounds via assets.py.
        dynamic_sound_path = f"sounds/{sound_name_with_ext}" # This path is relative and might not work as expected.
                                                        # Consider using absolute paths or paths relative to a known root.
        try:
            # Create a temporary sound object
            print(f"Attempting to dynamically load sound: {dynamic_sound_path}") # Debug print
            sound = pygame.mixer.Sound(dynamic_sound_path)
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(0.15)  # Default volume for dynamically loaded sounds
            sound.play()
        except pygame.error as e:
            print(f"Warning: Sound file '{dynamic_sound_path}' not found or error loading: {e}")
        except Exception as e:
            print(f"Error playing dynamically loaded sound: {e}")
    else:
        # Use the preloaded sound from game.assets
        if volume is not None:
            # Store the original volume
            original_volume = sounds[sound_name].get_volume()
            # Set the new volume temporarily
            sounds[sound_name].set_volume(volume)
            # Play the sound
            sounds[sound_name].play()
            # Schedule a reset of the volume (in main loop) - This comment suggests a dependency on the main loop.
            # The return value is used to reset volume. Ensure the calling code handles this.
            return original_volume 
        else:
            # Play with current volume
            sounds[sound_name].play()
            return None 