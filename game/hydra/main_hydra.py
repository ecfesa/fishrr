import pygame
import sys
from game.hydra.constants import *
from game.hydra.game_state import GameState as HydraGameState # Renamed to avoid conflict
import game.globals as g # Import main game globals

class HydraGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.is_running = True # Flag to control the game loop from outside if needed
        self.game_over = False # Flag to indicate if the hydra game is over

        # Initialize pygame specific to Hydra if not already globally managed
        # For now, assume pygame.init() and mixer.init() are done globally or can be called safely
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Create Hydra's game state manager
        # Pass the main game's screen and clock
        self.hydra_game_state = HydraGameState(self.screen, self.clock, self) 

    def handle_events(self, events):
        # Pass pygame events to Hydra's game state
        # The Hydra game's handle_events might need adjustment
        # if it directly calls pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
                self.game_over = True # Or handle quit differently
                # Potentially switch back to terminal or main menu
                # For now, just mark as game over
        self.hydra_game_state.handle_events(events) # Pass all events

    def update(self):
        if not self.game_over:
            self.hydra_game_state.update()
            # Check if Hydra game state indicates game over
            if hasattr(self.hydra_game_state, 'current_state') and \
               hasattr(self.hydra_game_state.current_state, 'game_over_flag') and \
               self.hydra_game_state.current_state.game_over_flag:
                self.game_over = True

    def draw(self):
        if not self.game_over:
            self.hydra_game_state.draw()
        # else:
            # Optionally draw a game over screen for Hydra or let main game handle it

    def run(self, events): # Combined event handling, update, and draw for one frame
        if not self.is_running:
            return False # Indicate game should stop

        self.handle_events(events)
        self.update()
        self.draw()
        
        return not self.game_over # Return True if still running, False if game over


# This part is for standalone execution, not needed when integrated
# def main_standalone():
#     pygame.init()
#     pygame.mixer.init()
#     screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Using Hydra's constants
#     pygame.display.set_caption("Hydra Game Standalone")
#     clock = pygame.time.Clock()
    
#     game = HydraGame(screen, clock)
    
#     while game.is_running:
#         events = pygame.event.get()
#         if not game.run(events): # run returns False when game_over or quit
#             break
#         pygame.display.flip() # Ensure display is updated
#         clock.tick(FPS) # Using Hydra's constants

#     pygame.quit()
#     sys.exit()

# If __name__ == "__main__":
#     main_standalone()

# To be called from the main game loop:
def initialize_hydra_game(screen, clock):
    """Initializes and returns an instance of the Hydra game."""
    return HydraGame(screen, clock)