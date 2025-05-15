import pygame
import pygame.gfxdraw
from typing import Dict, Set, Tuple
import math

# Initialize pygame
pygame.init()

# Colors - Update to fishing theme
BACKGROUND_COLOR = (9, 42, 72)     # Deep sea blue (#092A48)
BORDER_COLOR = (103, 155, 178)     # Light blue (#679BAE) 
TITLE_COLOR = (230, 230, 235)      # Off-white (#E6E6EB)
TEXT_COLOR = (210, 226, 235)       # Light blue gray (#D2E2EB)
HIDDEN_COLOR = (30, 60, 90)        # Very dark blue, almost invisible

# Window dimensions
WIDTH, HEIGHT = 480, 640
BORDER_RADIUS = 8
BORDER_WIDTH = 2
PADDING = 20

# Font setup
try:
    # Try to use a more fishing-themed font first
    font_options = [
        "Castellar",       # Looks like an old maritime map font
        "Blackadder ITC",  # Has a wavy, water-like appearance
        "Papyrus",         # Looks like weathered parchment
        "Comic Sans MS",   # Friendly, casual font as fallback
    ]
    
    found_font = False
    for font_name in font_options:
        try:
            TITLE_FONT = pygame.font.SysFont(font_name, 24)
            BODY_FONT = pygame.font.SysFont(font_name, 18)
            found_font = True
            break
        except:
            continue
            
    if not found_font:
        # Original fallback
        TITLE_FONT = pygame.font.Font("font/JetBrainsMono-Regular.ttf", 24)
        BODY_FONT = pygame.font.Font("font/JetBrainsMono-Regular.ttf", 18)
except:
    # Final fallback to system fonts if custom font not available
    TITLE_FONT = pygame.font.SysFont("consolas", 24)
    BODY_FONT = pygame.font.SysFont("consolas", 18)

def load_commands() -> Dict[str, str]:
    """Load all commands and their descriptions."""
    commands = {
        "ls":        "list files/directories in cwd. Shows disk usage for each file",
        "pwd":       "prints current directory",
        "tree":      "shows file tree. Supposed to show everything available",
        "cd":        "changes the current directory, supports passworded folders",
        "cp":        "copies a file/directory. Has restrictions on what can be copied",
        "exit":      "closes the game",
        "cat":       "prints out a file. Shows the contents of things in the game",
        "help":      "displays a help prompt with simple useful commands",
        "rm":        "deletes a file/directory ('drops' the file into the water)",
        "reboot":    "resets the game",
        "clear":     "wipes the CLI text",
        "egg":       "...",
        "ps":        "lists running processes",
        "kill":      "kills a process",
        "df":        "shows current disk usage",
        "fish lore": "fish lore..."
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
    # Create a blurred effect by rendering multiple semi-transparent copies
    alpha = 60  # Lower alpha for hidden commands (more transparent)
    blur_radius = 3  # Increase blur radius to make text less readable
    
    # Base rendered text
    text_surface = font.render(text, True, color)
    
    # Create a surface with alpha channel for the blur effect
    blur_surface = pygame.Surface((text_surface.get_width() + blur_radius*2, 
                                  text_surface.get_height() + blur_radius*2), pygame.SRCALPHA)
    
    # Render multiple copies with slight offsets for blur
    for dx in range(-blur_radius, blur_radius+1):
        for dy in range(-blur_radius, blur_radius+1):
            # Skip center to avoid double rendering
            if dx == 0 and dy == 0:
                continue
                
            # Calculate fade based on distance from center
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > blur_radius:
                continue
                
            # Fade alpha based on distance
            current_alpha = int(alpha * (1 - distance/blur_radius))
            
            # Create a copy with the current alpha
            temp_surface = text_surface.copy()
            temp_surface.set_alpha(current_alpha)
            
            # Blit at offset position
            blur_surface.blit(temp_surface, (blur_radius + dx, blur_radius + dy))
    
    # Add the main text on top
    text_surface.set_alpha(alpha)  # Make the main text less visible
    blur_surface.blit(text_surface, (blur_radius, blur_radius))
    
    # Blit the final blurred text to the main surface
    surface.blit(blur_surface, (pos[0] - blur_radius, pos[1] - blur_radius))

def draw_manual(surface: pygame.Surface, discovered: Set[str]) -> None:
    """Draw the manual with the command list."""
    commands = load_commands()
    hidden = get_hidden_commands()
    
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
    
    # Remove the column headers
    header_bottom = title_rect.bottom + PADDING + 5
    
    # Draw commands
    y_pos = header_bottom + 10
    line_height = BODY_FONT.get_height() + 10
    
    # Calculate available width for command and description
    available_width = WIDTH - (2 * PADDING + 20)
    cmd_width = int(available_width * 0.3)  # 30% for command
    desc_width = int(available_width * 0.7)  # 70% for description
    
    col1_x = PADDING + 10
    col2_x = col1_x + cmd_width + 10
    
    for i, (cmd, desc) in enumerate(commands.items()):
        # Truncate description if too long to avoid going off screen
        max_desc_chars = int(desc_width / (BODY_FONT.size("A")[0]))
        if len(desc) > max_desc_chars:
            desc = desc[:max_desc_chars-3] + "..."
            
        # Check if command is discovered
        is_discovered = cmd in discovered
        is_hidden = cmd in hidden
        
        if is_discovered or not is_hidden:
            # Render normal text for discovered commands or non-hidden commands
            cmd_text = BODY_FONT.render(cmd, True, TEXT_COLOR)
            desc_text = BODY_FONT.render(desc, True, TEXT_COLOR)
            
            surface.blit(cmd_text, (col1_x, y_pos))
            surface.blit(desc_text, (col2_x, y_pos))
        else:
            # Render blurred text for undiscovered hidden commands
            blur_text(surface, cmd, (col1_x, y_pos), BODY_FONT, HIDDEN_COLOR)
            blur_text(surface, "???", (col2_x, y_pos), BODY_FONT, HIDDEN_COLOR)
        
        y_pos += line_height
        
        # Draw horizontal line after each entry except the last one
        if i < len(commands) - 1:
            pygame.draw.line(
                surface, 
                (BORDER_COLOR[0], BORDER_COLOR[1], BORDER_COLOR[2], 100),  # Semi-transparent
                (PADDING, y_pos - 5),
                (WIDTH - PADDING, y_pos - 5),
                1
            )

def main():
    """Test function to display the manual."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Command Manual")
    
    # Set of discovered commands for testing
    discovered = {"ls", "pwd", "cd", "exit", "cat", "help", "rm", "clear", "ps", "kill", "df"}
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw the manual
        draw_manual(screen, discovered)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main() 