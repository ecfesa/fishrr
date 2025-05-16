import pygame
import sys
from constants import *
from game_state import GameState
from audio import load_sounds

def main():
    """Main function to run the game"""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()  # Initialize the sound mixer
    
    # Load sound effects
    load_sounds()
    
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Terminal Boat Navigation")
    clock = pygame.time.Clock()
    
    # Create game state manager
    game_state = GameState(screen, clock)
    
    # Main game loop
    while True:
        # Handle events
        game_state.handle_events()
        
        # Update game state
        game_state.update()
        
        # Draw the current state
        game_state.draw()

if __name__ == "__main__":
    main()
