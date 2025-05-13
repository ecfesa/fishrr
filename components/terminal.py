import pygame
from manager import constantmanager
from manager.gamemanager import GameManager

class Terminal:
    def __init__(self, x: int, y: int, width: int, height: int, gamemanager: GameManager):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(constantmanager.FONT, 16)
        self.input_text = ""
        self.output_lines: List[str] = []
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds

        # Game manager object
        self.gamemanager = gamemanager

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
            "fish": self.cmd_fish,
            "change" : self.cmd_change_level,
            "exit" : self.cmd_exit
        }

    def cmd_fish(self) -> str:
        return "You grab your fishing rod and start looking for fish in the sea..."

    def cmd_change_level(self) -> str:
        self.gamemanager.next_level()
        return "Your level has changed!!!"

    def cmd_exit(self) -> str:
        self.gamemanager.quit_game()
        return "Bye!!!"

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
        pygame.draw.rect(screen, constantmanager.BLACK, self.rect)

        # Draw output area with text
        pygame.draw.rect(screen, constantmanager.BLACK, self.output_rect)
        y_offset = self.output_rect.bottom - 30
        for line in reversed(self.output_lines[-100:]):  # Show last 100 lines
            text_surface = self.font.render(line, True, constantmanager.WHITE)
            screen.blit(text_surface, (self.output_rect.x + 10, y_offset))
            y_offset -= 30

        # Draw input area
        pygame.draw.rect(screen, constantmanager.DARK_GRAY, self.input_rect)

        # Draw input text with cursor
        input_surface = self.font.render(self.input_text, True, constantmanager.WHITE)
        screen.blit(input_surface, (self.input_rect.x + 10, self.input_rect.y + 5))

        # Draw blinking cursor
        if self.cursor_visible:
            cursor_x = self.input_rect.x + 10 + input_surface.get_width()
            pygame.draw.line(screen, constantmanager.WHITE,
                           (cursor_x, self.input_rect.y + 5),
                           (cursor_x, self.input_rect.y + 25))

        # Update cursor visibility
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_blink_speed // 16:  # Adjust for 60 FPS
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
