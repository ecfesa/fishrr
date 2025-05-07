import pygame
import sys
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TITLE = "Fishrr"
FPS = 60
FONT = 'font\JetBrainsMono-Regular.ttf'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

class Terminal:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(FONT, 16)
        self.input_text = ""
        self.output_lines: List[str] = []
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds
        
        # Input box properties
        self.input_height = 30
        self.input_rect = pygame.Rect(
            x,
            y + height - self.input_height,
            width,
            self.input_height
        )
        
        # Output area properties
        self.output_rect = pygame.Rect(
            x,
            y,
            width,
            height - self.input_height
        )
        
        # Command handling
        self.commands = {
            "fish": self.cmd_fish
        }
    
    def cmd_fish(self) -> str:
        return "You grab your fishing rod and start looking for fish in the sea..."
    
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.input_text.strip():
                command = self.input_text.strip().lower()
                if command in self.commands:
                    self.output_lines.append(f"> {self.input_text}")
                    self.output_lines.append(self.commands[command]())
                else:
                    self.output_lines.append(f"> {self.input_text}")
                    self.output_lines.append("Command not recognized.")
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if event.unicode.isprintable():
                    self.input_text += event.unicode

    def draw(self, screen: pygame.Surface) -> None:
        # Draw terminal background
        pygame.draw.rect(screen, BLACK, self.rect)
        
        # Draw output area with text
        pygame.draw.rect(screen, BLACK, self.output_rect)
        y_offset = self.output_rect.bottom - 30
        for line in reversed(self.output_lines[-100:]):  # Show last 100 lines
            text_surface = self.font.render(line, True, WHITE)
            screen.blit(text_surface, (self.output_rect.x + 10, y_offset))
            y_offset -= 30
        
        # Draw input area
        pygame.draw.rect(screen, DARK_GRAY, self.input_rect)
        
        # Draw input text with cursor
        input_surface = self.font.render(self.input_text, True, WHITE)
        screen.blit(input_surface, (self.input_rect.x + 10, self.input_rect.y + 5))
        
        # Draw blinking cursor
        if self.cursor_visible:
            cursor_x = self.input_rect.x + 10 + input_surface.get_width()
            pygame.draw.line(screen, WHITE,
                           (cursor_x, self.input_rect.y + 5),
                           (cursor_x, self.input_rect.y + 25))
        
        # Update cursor visibility
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_blink_speed // 16:  # Adjust for 60 FPS
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

class Sidebar:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(FONT, 16)
        self.title_font = pygame.font.Font(FONT, 24)
        self.commands = ["fish"]
    
    def draw(self, screen: pygame.Surface) -> None:
        # Draw sidebar background
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        
        # Draw title
        title_surface = self.title_font.render("Commands", True, WHITE)
        screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw commands list
        y_offset = self.rect.y + 50
        for cmd in self.commands:
            cmd_surface = self.font.render(cmd, True, WHITE)
            screen.blit(cmd_surface, (self.rect.x + 20, y_offset))
            y_offset += 30

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