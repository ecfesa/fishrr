import pygame
import pygame.gfxdraw
from typing import Dict, Set, Tuple, List
import math
import os

# Initialize pygame
pygame.init()

# Colors - Update to fishing theme
BACKGROUND_COLOR = (9, 42, 72)     # Deep sea blue (#092A48)
BORDER_COLOR = (103, 155, 178)     # Light blue (#679BAE) 
TITLE_COLOR = (230, 230, 235)      # Off-white (#E6E6EB)
TEXT_COLOR = (210, 226, 235)       # Light blue gray (#D2E2EB)
HIDDEN_COLOR = (30, 60, 90)        # Very dark blue, almost invisible
HIGHLIGHT_COLOR = (150, 185, 200)  # Highlighted command color
EXAMPLE_COLOR = (180, 200, 215)    # Example text color

# Window dimensions
WIDTH, HEIGHT = 480, 640
BORDER_RADIUS = 8
BORDER_WIDTH = 2
PADDING = 20

# Font setup
try:
    font_path = "font/JetBrainsMono-Regular.ttf"
    if os.path.exists(font_path):
        TITLE_FONT = pygame.font.Font(font_path, 24)
        BODY_FONT = pygame.font.Font(font_path, 18)
        EXAMPLE_FONT = pygame.font.Font(font_path, 16)
    else:
        # Final fallback to system fonts if custom font not available
        TITLE_FONT = pygame.font.SysFont("consolas", 24)
        BODY_FONT = pygame.font.SysFont("consolas", 18)
        EXAMPLE_FONT = pygame.font.SysFont("consolas", 16)
except:
    # Final fallback to system fonts if custom font not available
    TITLE_FONT = pygame.font.SysFont("consolas", 24)
    BODY_FONT = pygame.font.SysFont("consolas", 18)
    EXAMPLE_FONT = pygame.font.SysFont("consolas", 16)

def load_commands() -> Dict[str, Dict[str, str]]:
    """Load all commands, their descriptions, and examples."""
    commands = {
        "ls": {
            "desc": "list files/directories in cwd. Shows disk usage for each file",
            "example": "ls\nls -la\nls /home/user"
        },
        "pwd": {
            "desc": "prints current directory",
            "example": "pwd"
        },
        "tree": {
            "desc": "shows file tree. Supposed to show everything available",
            "example": "tree\ntree -L 2"
        },
        "cd": {
            "desc": "changes the current directory, supports passworded folders",
            "example": "cd /path/to/dir\ncd ..\ncd ~"
        },
        "cp": {
            "desc": "copies a file/directory. Has restrictions on what can be copied",
            "example": "cp file.txt destination/\ncp -r folder/ destination/"
        },
        "exit": {
            "desc": "closes the game",
            "example": "exit"
        },
        "cat": {
            "desc": "prints out a file. Shows the contents of things in the game",
            "example": "cat file.txt\ncat -n file.txt"
        },
        "help": {
            "desc": "displays a help prompt with simple useful commands",
            "example": "help\nhelp command"
        },
        "rm": {
            "desc": "deletes a file/directory ('drops' the file into the water)",
            "example": "rm file.txt\nrm -rf directory/"
        },
        "reboot": {
            "desc": "resets the game",
            "example": "reboot"
        },
        "clear": {
            "desc": "wipes the CLI text",
            "example": "clear"
        },
        "egg": {
            "desc": "...",
            "example": "???"
        },
        "ps": {
            "desc": "lists running processes",
            "example": "ps\nps aux"
        },
        "kill": {
            "desc": "kills a process",
            "example": "kill 1234\nkill -9 5678"
        },
        "df": {
            "desc": "shows current disk usage",
            "example": "df\ndf -h"
        },
        "fish lore": {
            "desc": "fish lore...",
            "example": "fish lore"
        }
    }
    return commands

def get_hidden_commands() -> Set[str]:
    """Return the set of hidden commands."""
    return {"tree", "cp", "reboot", "egg", "fish lore"}

def rounded_rect(surface, rect, color, radius=10, border_width=0):
    """Draw a rounded rectangle with a border."""
    x, y, width, height = rect
    
    # Draw the filled rounded rectangle
    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=radius)
    
    # Draw the border if specified
    if border_width > 0:
        pygame.draw.rect(surface, BORDER_COLOR, (x, y, width, height), 
                         width=border_width, border_radius=radius)

def blur_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: pygame.font.Font, color: Tuple[int, int, int]):
    """Render text with a heavy blur effect to make hidden commands completely unreadable."""
    # Create a random character string to replace hidden text
    import random
    chars = "█▓▒░▄▀■□▪▫●○◆◇★☆⬛⬜◼◻"
    random_text = ''.join(random.choice(chars) for _ in range(len(text)))
    
    # Apply heavy distortion
    text_surface = font.render(random_text, True, color)
    blur_surface = pygame.Surface((text_surface.get_width(), text_surface.get_height()), pygame.SRCALPHA)
    
    # Very low opacity
    text_surface.set_alpha(40)
    
    # Add noise and distortion
    for _ in range(5):
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        blur_surface.blit(text_surface, (offset_x, offset_y))
    
    # Blit the final blurred text to the main surface
    surface.blit(blur_surface, pos)

class CommandList:
    def __init__(self, discovered: Set[str]):
        self.commands = load_commands()
        self.hidden = get_hidden_commands()
        self.discovered = discovered
        self.expanded_command = None
        self.scroll_offset = 0
        self.max_visible_commands = 10
    
    def toggle_command(self, command: str):
        """Toggle expansion of a command."""
        if self.expanded_command == command:
            self.expanded_command = None
        else:
            self.expanded_command = command
    
    def scroll(self, amount: int):
        """Scroll the command list by the specified amount."""
        max_scroll = max(0, len(self.commands) - self.max_visible_commands)
        self.scroll_offset = max(0, min(self.scroll_offset + amount, max_scroll))
    
    def get_command_rect(self, index: int, y_pos: int) -> pygame.Rect:
        """Get the rectangle for a command at the specified index and y position."""
        return pygame.Rect(PADDING, y_pos, WIDTH - 2 * PADDING, BODY_FONT.get_height())
    
    def draw(self, surface: pygame.Surface) -> List[Tuple[pygame.Rect, str]]:
        """Draw the command list and return a list of (rect, command) pairs for clickable areas."""
        # Clear the surface
        surface.fill(BACKGROUND_COLOR)
        
        # Draw rounded rectangle border
        rounded_rect(
            surface, 
            (BORDER_WIDTH//2, BORDER_WIDTH//2, WIDTH-BORDER_WIDTH, HEIGHT-BORDER_WIDTH),
            BACKGROUND_COLOR,
            BORDER_RADIUS,
            BORDER_WIDTH
        )
        
        # Draw title
        title_text = TITLE_FONT.render("COMMAND LIST", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH//2, PADDING + title_text.get_height()//2))
        surface.blit(title_text, title_rect)
        
        # Draw horizontal line below title
        pygame.draw.line(
            surface, 
            BORDER_COLOR, 
            (PADDING, title_rect.bottom + PADDING//2),
            (WIDTH - PADDING, title_rect.bottom + PADDING//2),
            1
        )
        
        # Draw scroll buttons
        scroll_up = "▲"
        scroll_down = "▼"
        up_text = BODY_FONT.render(scroll_up, True, TEXT_COLOR)
        down_text = BODY_FONT.render(scroll_down, True, TEXT_COLOR)
        
        up_rect = up_text.get_rect(topright=(WIDTH - PADDING, title_rect.bottom + PADDING//2 + 5))
        down_rect = down_text.get_rect(bottomright=(WIDTH - PADDING, HEIGHT - PADDING))
        
        surface.blit(up_text, up_rect)
        surface.blit(down_text, down_rect)
        
        # Calculate available area
        header_bottom = title_rect.bottom + PADDING + 5
        
        # Draw commands
        y_pos = header_bottom + 10
        line_height = BODY_FONT.get_height() + 10
        
        clickable_areas = []
        
        # Get list of command keys and slice based on scroll position
        cmd_keys = list(self.commands.keys())
        visible_commands = cmd_keys[self.scroll_offset:self.scroll_offset + self.max_visible_commands]
        
        for i, cmd in enumerate(visible_commands):
            cmd_info = self.commands[cmd]
            
            # Check if command is discovered
            is_discovered = cmd in self.discovered
            is_hidden = cmd in self.hidden
            is_expanded = self.expanded_command == cmd
            
            # Create clickable area for this command
            cmd_rect = self.get_command_rect(i, y_pos)
            
            # Only make discovered or non-hidden commands clickable
            if is_discovered or not is_hidden:
                clickable_areas.append((cmd_rect, cmd))
                
                # Highlight the row if this command is expanded
                if is_expanded:
                    highlight_rect = pygame.Rect(PADDING + 5, y_pos - 5, 
                                               WIDTH - 2 * PADDING - 10, 
                                               BODY_FONT.get_height() + 5)
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect, border_radius=4)
                
                # Render normal text for discovered commands or non-hidden commands
                cmd_text = BODY_FONT.render(cmd, True, TEXT_COLOR)
                desc_text = BODY_FONT.render(cmd_info["desc"], True, TEXT_COLOR)
                
                # Draw command name
                surface.blit(cmd_text, (PADDING + 10, y_pos))
                
                # Calculate maximum width for description
                max_desc_width = WIDTH - 2 * PADDING - BODY_FONT.size(cmd)[0] - 30
                
                # Truncate description if necessary and not expanded
                desc_str = cmd_info["desc"]
                if not is_expanded:
                    # Estimate character width
                    avg_char_width = BODY_FONT.size("A")[0]
                    max_chars = max_desc_width // avg_char_width
                    
                    if len(desc_str) > max_chars:
                        desc_str = desc_str[:max_chars-3] + "..."
                
                # Draw description text
                desc_text = BODY_FONT.render(desc_str, True, TEXT_COLOR)
                surface.blit(desc_text, (PADDING + 150, y_pos))
                
                # Draw expansion indicator
                expand_indicator = "▼" if is_expanded else "▶"
                exp_text = BODY_FONT.render(expand_indicator, True, TEXT_COLOR)
                surface.blit(exp_text, (WIDTH - PADDING - 20, y_pos))
                
                # If expanded, show example(s)
                if is_expanded:
                    examples = cmd_info["example"].split("\n")
                    example_y = y_pos + line_height
                    
                    # Draw example box
                    example_height = len(examples) * EXAMPLE_FONT.get_height() + 20
                    example_rect = pygame.Rect(
                        PADDING + 20, 
                        example_y - 5, 
                        WIDTH - 2 * PADDING - 40, 
                        example_height
                    )
                    
                    # Draw semi-transparent background
                    s = pygame.Surface((example_rect.width, example_rect.height), pygame.SRCALPHA)
                    s.fill((30, 70, 100, 128))  # Semi-transparent blue
                    surface.blit(s, example_rect)
                    
                    # Draw border
                    pygame.draw.rect(surface, BORDER_COLOR, example_rect, width=1, border_radius=4)
                    
                    # Draw "Example:" text
                    ex_title = EXAMPLE_FONT.render("Example:", True, EXAMPLE_COLOR)
                    surface.blit(ex_title, (PADDING + 30, example_y + 5))
                    
                    # Draw each example line
                    for j, example in enumerate(examples):
                        ex_text = EXAMPLE_FONT.render(example, True, EXAMPLE_COLOR)
                        surface.blit(ex_text, (PADDING + 50, example_y + 5 + (j+1) * EXAMPLE_FONT.get_height()))
                    
                    # Increase y_pos to account for expanded section
                    y_pos += example_height
            else:
                # Render completely unreadable text for undiscovered hidden commands
                blur_text(surface, cmd, (PADDING + 10, y_pos), BODY_FONT, HIDDEN_COLOR)
                blur_text(surface, "??????????????????", (PADDING + 150, y_pos), BODY_FONT, HIDDEN_COLOR)
            
            y_pos += line_height
            
            # Draw horizontal line after each entry except the last one
            if i < len(visible_commands) - 1:
                pygame.draw.line(
                    surface, 
                    (BORDER_COLOR[0], BORDER_COLOR[1], BORDER_COLOR[2], 100),  # Semi-transparent
                    (PADDING, y_pos - 5),
                    (WIDTH - PADDING, y_pos - 5),
                    1
                )
        
        # Add scroll button areas to clickable areas
        clickable_areas.append((up_rect, "scroll_up"))
        clickable_areas.append((down_rect, "scroll_down"))
        
        return clickable_areas

def draw_manual(surface: pygame.Surface, discovered: Set[str]) -> List[Tuple[pygame.Rect, str]]:
    """Draw the manual with the expandable command list."""
    command_list = CommandList(discovered)
    return command_list.draw(surface)

def main():
    """Test function to display the manual."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Command Manual")
    
    # Set of discovered commands for testing
    discovered = {"ls", "pwd", "cd", "exit", "cat", "help", "rm", "clear", "ps", "kill", "df"}
    
    # Create command list
    command_list = CommandList(discovered)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    command_list.scroll(-1)
                elif event.key == pygame.K_DOWN:
                    command_list.scroll(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Get clickable areas
                    clickable_areas = command_list.draw(screen)
                    
                    # Check if click is on a command
                    for rect, cmd in clickable_areas:
                        if rect.collidepoint(event.pos):
                            if cmd == "scroll_up":
                                command_list.scroll(-1)
                            elif cmd == "scroll_down":
                                command_list.scroll(1)
                            else:
                                command_list.toggle_command(cmd)
        
        # Draw the manual
        command_list.draw(screen)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main() 