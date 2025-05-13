import pygame
import sys
from terminal import Terminal
from sidebar import Sidebar
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, FPS, BLACK

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Create sidebar (200px width)
        self.sidebar = Sidebar(0, 0, 200, WINDOW_HEIGHT)
        
        # Create terminal (remaining width)
        self.terminal = Terminal(
            200, 0,  # Position after sidebar
            WINDOW_WIDTH - 200, WINDOW_HEIGHT  # Remaining space
        )

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.terminal.handle_input(event)

            # Fill background
            self.screen.fill(BLACK)
            
            # Draw terminal and sidebar
            self.sidebar.draw(self.screen)
            self.terminal.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
