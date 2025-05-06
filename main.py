import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TITLE = "Fishrr"
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)  # Default font, size 74
        self.button_font = pygame.font.Font(None, 36)
        
        # Button properties
        self.button_width = 200
        self.button_height = 50
        self.button_x = WINDOW_WIDTH // 2 - self.button_width // 2
        self.button_y = WINDOW_HEIGHT // 2 + 50
        self.button_rect = pygame.Rect(
            self.button_x,
            self.button_y,
            self.button_width,
            self.button_height
        )

    def draw_title_screen(self):
        # Fill background
        self.screen.fill(BLACK)
        
        # Draw title
        title_surface = self.font.render(TITLE, True, WHITE)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)
        
        # Draw button
        pygame.draw.rect(self.screen, GRAY, self.button_rect)
        button_text = self.button_font.render("Start Game", True, WHITE)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, button_text_rect)

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        print("Start game button clicked!")
                        # TODO: Implement game start logic

            # Draw everything
            self.draw_title_screen()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 