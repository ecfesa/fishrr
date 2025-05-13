import pygame
from typing import List, Dict, Callable
from constants import FONT, BLACK, WHITE

class Terminal:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(FONT, 16)
        self.input_text = ""
        self.output_lines: List[str] = []
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds
        self.background_color = BLACK  # Pode ser alterado pela ilha
        
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
        
        # Command history
        self.command_history = []
        self.history_index = -1
        
        # Command handling
        self.commands: Dict[str, Callable] = {
            "fish": self.cmd_fish,
            "man": self.cmd_man,
            "help": self.cmd_help
        }
    
    def cmd_fish(self) -> str:
        return "You grab your fishing rod and start looking for fish in the sea..."
        
    def cmd_man(self, *args) -> str:
        if not args:
            page_num = 1
        else:
            try:
                page_num = int(args[0])
            except (ValueError, IndexError):
                return "Usage: man <page_number>"
        
        from manual import Manual
        page = Manual.get_page(page_num)
        content = page["content"]
        hint = page["hint"]
        
        return f"{content}\n\nHint: {hint}"
    
    def cmd_help(self) -> str:
        return "\n".join([
            "Available commands:",
            "- fish: Start fishing",
            "- man <page>: Show manual page",
            "- help: Show this help message"
        ])
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Processa a entrada do usuário para o terminal"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Process command
                if self.input_text:
                    # Save to history
                    self.command_history.append(self.input_text)
                    self.history_index = -1
                    
                    # Display command in output
                    self.output_lines.append(f"> {self.input_text}")
                    
                    # Parse and execute command
                    command_parts = self.input_text.split()
                    command = command_parts[0].lower() if command_parts else ""
                    args = command_parts[1:] if len(command_parts) > 1 else []
                    
                    # Execute command if it exists
                    if command in self.commands:
                        result = self.commands[command](*args)
                        if result:
                            # Split result into lines and add to output
                            for line in result.split('\n'):
                                self.output_lines.append(line)
                    else:
                        self.output_lines.append(f"Command not found: {command}")
                    
                    # Clear input
                    self.input_text = ""
            
            elif event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.input_text = self.input_text[:-1]
            
            elif event.key == pygame.K_UP:
                # Navigate command history up
                if self.command_history:
                    if self.history_index < len(self.command_history) - 1:
                        self.history_index += 1
                        self.input_text = self.command_history[-(self.history_index + 1)]
            
            elif event.key == pygame.K_DOWN:
                # Navigate command history down
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_text = self.command_history[-(self.history_index + 1)]
                else:
                    self.history_index = -1
                    self.input_text = ""
            
            elif event.unicode and ord(event.unicode) >= 32 and ord(event.unicode) < 127:
                # Add character to input
                self.input_text += event.unicode
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o terminal na tela"""
        # Draw output area background
        pygame.draw.rect(screen, self.background_color, self.output_rect)
        
        # Draw input area background
        pygame.draw.rect(screen, BLACK, self.input_rect)
        
        # Draw separator line
        pygame.draw.line(
            screen,
            (128, 128, 128),  # Gray color
            (self.rect.x, self.input_rect.y),
            (self.rect.x + self.rect.width, self.input_rect.y),
            2
        )
        
        # Update cursor visibility based on timer
        self.cursor_timer += pygame.time.get_ticks() % 1000
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
        
        # Draw input text with cursor
        input_prompt = "> "
        input_surface = self.font.render(input_prompt + self.input_text, True, WHITE)
        screen.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # Draw cursor if visible
        if self.cursor_visible:
            cursor_x = self.input_rect.x + 5 + self.font.size(input_prompt + self.input_text)[0]
            pygame.draw.line(
                screen,
                WHITE,
                (cursor_x, self.input_rect.y + 5),
                (cursor_x, self.input_rect.y + self.input_height - 5),
                2
            )
        
        # Draw output lines (showing only the last n lines that fit in the output area)
        visible_lines = self.output_rect.height // 20  # Estimating ~20px per line
        start_line = max(0, len(self.output_lines) - visible_lines)
        
        for i, line in enumerate(self.output_lines[start_line:]):
            line_surface = self.font.render(line, True, WHITE)
            screen.blit(line_surface, (self.output_rect.x + 5, self.output_rect.y + 5 + i * 20))