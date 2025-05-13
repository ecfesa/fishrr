import pygame
import sys
from components.sidebar import Sidebar
from components.terminal import Terminal
from manager import constantmanager
from manager.gamemanager import GameManager

class Game:
    def __init__(self, gamemanager):

        # Create gamemanager object
        self.gamemanager = gamemanager

        # Create sidebar (200px width)
        self.sidebar = Sidebar(0, 0, 200, gamemanager.screen.get_height())

        # Create terminal (remaining width)
        self.terminal = Terminal(
            200, 0,  # Position after sidebar
            gamemanager.screen.get_width() - 200,
            gamemanager.screen.get_height()# Remaining space
            , gamemanager
        )

    def run(self):
        self.gamemanager.running = True

        while self.gamemanager.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gamemanager.quit_game()
                self.terminal.handle_input(event)

            # Fill background
            self.gamemanager.screen.fill(constantmanager.BLACK)

            # Draw terminal and sidebar
            self.sidebar.draw(self.gamemanager.screen)
            self.terminal.draw(self.gamemanager.screen)

            # Update display
            pygame.display.flip()

            # Cap the frame rate
            self.gamemanager.clock.tick(constantmanager.FPS)

        pygame.quit()
        sys.exit()
