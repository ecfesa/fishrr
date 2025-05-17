import pygame
import pygame.gfxdraw
from typing import Dict, Set, Tuple, List
import math
import os

# Initialize pygame
pygame.init()

# Colors - Update to fishing theme
BACKGROUND_COLOR = (0, 0, 0)         # Black
BORDER_COLOR = (0, 128, 0)       # Green
TITLE_COLOR = (0, 255, 0)        # Bright Green
TEXT_COLOR = (0, 200, 0)         # Medium Green
HIDDEN_COLOR = (0, 50, 0)          # Dark Green, almost invisible
HIGHLIGHT_COLOR = (0, 100, 0)    # Darker Green for highlight
EXAMPLE_COLOR = (0, 180, 0)      # Lighter Green for examples

# Window dimensions
WIDTH, HEIGHT = 480, 640
BORDER_RADIUS = 8
BORDER_WIDTH = 2
PADDING = 20

# Font setup
try:
    font_path = "font/JetBrainsMono-Regular.ttf"
    if os.path.exists(font_path):
        TITLE_FONT = pygame.font.Font(font_path, 30) # Increased title font size
        BODY_FONT = pygame.font.Font(font_path, 14)
        EXAMPLE_FONT = pygame.font.Font(font_path, 13)
    else:
        # Final fallback to system fonts if custom font not available
        TITLE_FONT = pygame.font.SysFont("consolas", 30) # Increased title font size
        BODY_FONT = pygame.font.SysFont("consolas", 14)
        EXAMPLE_FONT = pygame.font.SysFont("consolas", 13)
except:
    # Final fallback to system fonts if custom font not available
    TITLE_FONT = pygame.font.SysFont("consolas", 30) # Increased title font size
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
        self.active_buttons_feedback = {} # For visual feedback on key press

        # Layout constants
        self.screen_margin = 20  # Increased outer margin
        self.title_extra_padding_top = 10
        self.content_padding = 15 # Padding between elements (title-line, line-buttons, etc.)
        
        self.scroll_button_width = 80 # Slightly wider scroll buttons
        self.scroll_button_height = 30
        self.line_height = BODY_FONT.get_height() + 10  # Height of one unexpanded command entry slot

        # Title positioning
        title_text_height = TITLE_FONT.get_height()
        self.title_rect_center_y = self.screen_margin + self.title_extra_padding_top + title_text_height // 2 + 5 # Adjusted for new font size
        title_bottom = self.title_rect_center_y + title_text_height // 2
        
        # Horizontal line below title
        self.title_line_y = title_bottom + self.content_padding + 5 # Adjusted for new font size

        # UP scroll button positioning
        up_button_top_y = self.title_line_y + self.content_padding
        self.up_button_rect = pygame.Rect(0, 0, self.scroll_button_width, self.scroll_button_height)
        self.up_button_rect.centerx = WIDTH // 2
        self.up_button_rect.top = up_button_top_y
        
        # Start Y for command list (top of command drawing area)
        self.commands_start_y = self.up_button_rect.bottom + self.content_padding

        # DOWN scroll button positioning
        self.down_button_rect = pygame.Rect(0, 0, self.scroll_button_width, self.scroll_button_height)
        self.down_button_rect.centerx = WIDTH // 2
        self.down_button_rect.bottom = HEIGHT - self.screen_margin - 10 # Added 10px bottom padding for the list area
        
        # Calculate command area height (space available for command entries)
        # This is the bottom limit for where command content can be drawn.
        self.command_area_bottom_limit = self.down_button_rect.top - self.content_padding
        self.command_area_height = self.command_area_bottom_limit - self.commands_start_y
        
        if self.command_area_height < self.line_height:
            self.max_visible_commands_unexpanded = 0 # How many non-expanded items fit
        else:
            self.max_visible_commands_unexpanded = self.command_area_height // self.line_height
    
    def set_button_feedback(self, button_key: str, active: bool):
        """Set feedback state for a button (e.g., scroll up/down)."""
        if active:
            self.active_buttons_feedback[button_key] = pygame.time.get_ticks() # Store time for animation
        elif button_key in self.active_buttons_feedback:
            del self.active_buttons_feedback[button_key]

    def toggle_command(self, command: str):
        """Toggle expansion of a command."""
        if self.expanded_command == command:
            self.expanded_command = None
        else:
            self.expanded_command = command
    
    def scroll(self, amount: int):
        """Scroll the command list by the specified amount."""
        num_commands = len(self.commands)
        if num_commands == 0:
            self.scroll_offset = 0
            return

        # Allow scrolling so that the last command can be at the top of the list.
        # The draw method handles clipping if content is too tall.
        new_offset = self.scroll_offset + amount
        self.scroll_offset = max(0, min(new_offset, num_commands - 1))
    
    def get_command_rect(self, index: int, y_pos: int) -> pygame.Rect:
        """Get the rectangle for a command at the specified index and y position."""
        return pygame.Rect(self.screen_margin, y_pos, WIDTH - 2 * self.screen_margin, BODY_FONT.get_height())
    
    def draw(self, surface: pygame.Surface, mouse_pos: Tuple[int, int] | None) -> List[Tuple[pygame.Rect, str]]:
        """Draw the command list and return a list of (rect, command) pairs for clickable areas."""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw title
        title_text = TITLE_FONT.render("COMMAND LIST", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, self.title_rect_center_y))
        surface.blit(title_text, title_rect)
        
        # Draw horizontal line below title
        pygame.draw.line(
            surface, BORDER_COLOR, 
            (self.screen_margin, self.title_line_y),
            (WIDTH - self.screen_margin, self.title_line_y), 1
        )
        
        # Draw Scroll Buttons
        up_text_render = BODY_FONT.render("▲", True, TEXT_COLOR)
        down_text_render = BODY_FONT.render("▼", True, TEXT_COLOR)
        
        up_button_bg_color = BORDER_COLOR
        if "scroll_up" in self.active_buttons_feedback and pygame.time.get_ticks() - self.active_buttons_feedback["scroll_up"] < 200: # 200ms feedback
            up_button_bg_color = HIGHLIGHT_COLOR
        elif mouse_pos and self.up_button_rect.collidepoint(mouse_pos):
            up_button_bg_color = HIGHLIGHT_COLOR
            
        down_button_bg_color = BORDER_COLOR
        if "scroll_down" in self.active_buttons_feedback and pygame.time.get_ticks() - self.active_buttons_feedback["scroll_down"] < 200: # 200ms feedback
            down_button_bg_color = HIGHLIGHT_COLOR
        elif mouse_pos and self.down_button_rect.collidepoint(mouse_pos):
            down_button_bg_color = HIGHLIGHT_COLOR

        pygame.draw.rect(surface, up_button_bg_color, self.up_button_rect, border_radius=4)
        pygame.draw.rect(surface, down_button_bg_color, self.down_button_rect, border_radius=4)
        up_text_rect = up_text_render.get_rect(center=self.up_button_rect.center)
        down_text_rect = down_text_render.get_rect(center=self.down_button_rect.center)
        surface.blit(up_text_render, up_text_rect)
        surface.blit(down_text_render, down_text_rect)

        # Add navigation hint text
        hint_font = pygame.font.Font(font_path, 14) if os.path.exists(font_path) else pygame.font.SysFont("consolas", 14)
        hint_text_surface = hint_font.render("Use UP/DOWN arrow keys to scroll", True, TEXT_COLOR)
        hint_text_rect = hint_text_surface.get_rect(centerx=WIDTH // 2, top=self.down_button_rect.bottom + 5)
        surface.blit(hint_text_surface, hint_text_rect)
        
        clickable_areas = [(self.up_button_rect, "scroll_up"), (self.down_button_rect, "scroll_down")]
        
        cmd_keys = list(self.commands.keys())

        # First Pass: Determine what fits and calculate their drawing properties
        visible_command_details = []
        current_y_cumulative = self.commands_start_y # Tracks the top Y for the *next* command to be placed

        for i in range(self.scroll_offset, len(cmd_keys)):
            cmd_key = cmd_keys[i]
            cmd_info_dict = self.commands[cmd_key]

            is_expanded_flag = (self.expanded_command == cmd_key) and \
                               (cmd_key in self.discovered or cmd_key not in self.hidden)

            # Height of the command's main line (name, desc, indicator) + its bottom padding
            main_line_total_height = self.line_height 
            
            # Calculate description height if expanded
            desc_render_details = {"is_present": False, "height": 0, "surfaces": []}
            if is_expanded_flag:
                desc_str = cmd_info_dict["desc"]
                max_desc_width_pixels = WIDTH - 2 * self.screen_margin - 20 - 25 # available width for desc, -20 for left padding
                
                words = desc_str.split(' ')
                lines = []
                current_line = ""
                for word in words:
                    if BODY_FONT.size(current_line + word)[0] <= max_desc_width_pixels:
                        current_line += word + " "
                    else:
                        lines.append(current_line.strip())
                        current_line = word + " "
                lines.append(current_line.strip())
                
                desc_surfaces = [BODY_FONT.render(line, True, TEXT_COLOR) for line in lines]
                desc_total_height = sum(s.get_height() for s in desc_surfaces)
                
                desc_render_details = {
                    "is_present": True, 
                    "height": desc_total_height, 
                    "surfaces": desc_surfaces
                }
                # Adjust main_line_total_height if description is now part of the "main" area when expanded
                # The original self.line_height was for a single line. Now we have potentially multi-line description.
                # We need to account for the name line + the multi-line description.
                # Let's assume the command name is one line.
                main_line_total_height = BODY_FONT.get_height() + 5 # Command name + some padding
                main_line_total_height += desc_total_height + 5 # Add height of wrapped description + padding
            
            current_item_total_draw_height = main_line_total_height
            
            example_render_details = {"is_present": False, "height": 0}

            if is_expanded_flag:
                examples_text_list = cmd_info_dict["example"].split("\\n")
                ex_title_h = EXAMPLE_FONT.get_height()
                ex_lines_h = len(examples_text_list) * EXAMPLE_FONT.get_height()
                
                # Padding for example box: 5px top/bottom inside box, 10px left/right inside.
                # Additional gap between main command line and example box.
                ex_box_vertical_padding_content = 10 # 5 top + 5 bottom for text within box lines
                ex_box_top_margin = 10 # Gap between command line/description and example box border
                                
                example_section_visual_height = ex_title_h + ex_lines_h + ex_box_vertical_padding_content
                
                # Total height added by the example section including its top margin
                total_example_section_added_height = example_section_visual_height + ex_box_top_margin
                current_item_total_draw_height += total_example_section_added_height
                
                # Add a small gap after the example section before the next command
                current_item_total_draw_height += 10 # Gap after example
                                
                example_render_details = {
                    "is_present": True, "height": example_section_visual_height, 
                    "top_margin": ex_box_top_margin,
                    "texts": examples_text_list, "title_h": ex_title_h, 
                    "box_padding_content": ex_box_vertical_padding_content,
                    "item_y_start_for_box": current_y_cumulative + main_line_total_height # Y where example box starts
                }
            
            # Stop adding if the very top of the non-expanded part of this command is already beyond the drawing area limit.
            # Allow the first item to be partially drawn even if it's very tall.
            if len(visible_command_details) > 0 and \
               current_y_cumulative + BODY_FONT.get_height() > self.command_area_bottom_limit:
                break
            
            # If cumulative Y has already gone way past the bottom (e.g. scrolled too far down for any content)
            if current_y_cumulative >= self.command_area_bottom_limit + self.line_height: # allow some overshoot for last item
                 if not (len(visible_command_details) == 0 and cmd_key == cmd_keys[self.scroll_offset]): # if it's the first desired item
                    break


            visible_command_details.append({
                "key": cmd_key, "info": cmd_info_dict,
                "y_start_coord": current_y_cumulative, 
                "main_line_h": main_line_total_height, 
                "desc_details": desc_render_details, # Store desc details
                "total_item_h": current_item_total_draw_height,
                "is_expanded": is_expanded_flag, 
                "example_details": example_render_details
            })
            
            current_y_cumulative += current_item_total_draw_height

        # Second Pass: Draw the determined visible commands
        for index, item_data in enumerate(visible_command_details):
            cmd = item_data["key"]
            cmd_info = item_data["info"]
            y_pos_item_start = item_data["y_start_coord"]
            is_expanded = item_data["is_expanded"]
            desc_details = item_data["desc_details"]
            
            # Clip drawing to the command area
            # Note: Pygame's blit and draw operations are clipped by surface boundaries,
            # but explicit clipping rect can be set on surface if needed for sub-areas.
            # For now, we rely on not starting to draw items that are fully below.

            # Draw separator line above this item (if not the first in the visible list)
            if index > 0:
                # line_height has 10px padding, use half for separator offset
                line_y = y_pos_item_start - (self.line_height - BODY_FONT.get_height()) // 2 
                if line_y > self.commands_start_y : # Don't draw above command area
                    pygame.draw.line(
                        surface, (BORDER_COLOR[0], BORDER_COLOR[1], BORDER_COLOR[2], 100),
                        (self.screen_margin, line_y),
                        (WIDTH - self.screen_margin, line_y), 1
                    )

            # --- Draw Command Main Line ---
            # Stop drawing this item if its starting Y is already beyond the command area bottom limit
            if y_pos_item_start >= self.command_area_bottom_limit + self.line_height: # Too far down
                continue

            is_discovered = cmd in self.discovered
            is_hidden = cmd in self.hidden

            # Clickable area for the main command line
            # Use BODY_FONT.get_height() for the clickable height of the primary line.
            cmd_click_rect_height = BODY_FONT.get_height()
            if is_expanded: # If expanded, the clickable area might span the command name and the description
                 cmd_click_rect_height = BODY_FONT.get_height() # Just the command name line is clickable to toggle
            
            cmd_click_rect = pygame.Rect(
                self.screen_margin, y_pos_item_start, 
                WIDTH - 2 * self.screen_margin, cmd_click_rect_height
            )

            if is_discovered or not is_hidden:
                if cmd_click_rect.bottom < self.command_area_bottom_limit + cmd_click_rect_height : # only add if visible
                    clickable_areas.append((cmd_click_rect, cmd))
                
                if is_expanded: # Highlight the main line of the expanded command
                    highlight_rect = pygame.Rect(
                        self.screen_margin + 5, y_pos_item_start - 2, # Small offset for visual
                        WIDTH - 2 * self.screen_margin - 10, cmd_click_rect_height + 4
                    )
                    if highlight_rect.bottom < self.command_area_bottom_limit + cmd_click_rect_height:
                         pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect, border_radius=4)
                
                # Command Name
                cmd_text_surface = BODY_FONT.render(cmd, True, TEXT_COLOR)
                surface.blit(cmd_text_surface, (self.screen_margin + 10, y_pos_item_start))

                # Command Description
                desc_x_start = self.screen_margin + 150 
                desc_y_start = y_pos_item_start
                
                if is_expanded and desc_details["is_present"]:
                    current_desc_y = y_pos_item_start + BODY_FONT.get_height() + 5 # Start below command name
                    desc_left_padding = 20 # Added padding for expanded description
                    for line_surface in desc_details["surfaces"]:
                        if current_desc_y + line_surface.get_height() <= self.command_area_bottom_limit + self.line_height :
                             surface.blit(line_surface, (self.screen_margin + 10 + desc_left_padding, current_desc_y)) # Indent expanded desc
                        current_desc_y += line_surface.get_height()
                elif not is_expanded:
                    max_desc_width_pixels = (WIDTH - self.screen_margin - 20 - desc_x_start)
                    desc_str = cmd_info["desc"]
                    avg_char_width = BODY_FONT.size("A")[0]
                    if avg_char_width > 0:
                        max_chars = max_desc_width_pixels // avg_char_width
                        if len(desc_str) > max_chars:
                            desc_str = desc_str[:max_chars-3] + "..."
                    else: 
                        desc_str = desc_str[:15] + "..." if len(desc_str) > 18 else desc_str
                    desc_text_surface = BODY_FONT.render(desc_str, True, TEXT_COLOR)
                    surface.blit(desc_text_surface, (desc_x_start, desc_y_start))

                # Expansion Indicator
                expand_indicator_char = "▼" if is_expanded else "▶"
                exp_ind_surface = BODY_FONT.render(expand_indicator_char, True, TEXT_COLOR)
                surface.blit(exp_ind_surface, (WIDTH - self.screen_margin - 25, y_pos_item_start)) # Adjusted for slightly more padding

                # --- Draw Expanded Example Section (if applicable) ---
                if is_expanded:
                    ex_details = item_data["example_details"]
                    # Y where the example box border starts
                    # This now needs to be relative to the bottom of the (potentially multi-line) description
                    desc_total_height = desc_details["height"] if desc_details["is_present"] else 0
                    example_box_start_y = y_pos_item_start + BODY_FONT.get_height() + 5 + desc_total_height + 5 # Name + padding + Description + padding
                    
                    # Check if example box itself is visible before drawing
                    if example_box_start_y < self.command_area_bottom_limit:
                        example_rect_visual = pygame.Rect(
                            self.screen_margin + 20, 
                            example_box_start_y,
                            WIDTH - 2 * self.screen_margin - 40, 
                            ex_details["height"] # This is the height of the content *inside* the box + its internal padding
                        )
                        
                        # Semi-transparent background for example box
                        s = pygame.Surface((example_rect_visual.width, example_rect_visual.height), pygame.SRCALPHA)
                        s.fill((30, 70, 100, 128)) 
                        surface.blit(s, example_rect_visual.topleft)
                        pygame.draw.rect(surface, BORDER_COLOR, example_rect_visual, width=1, border_radius=4)

                        # "Example:" title text
                        ex_title_draw_y = example_rect_visual.top + (ex_details["box_padding_content"] // 2) - (EXAMPLE_FONT.get_height()//2) + (ex_details["title_h"]//2)

                        surface.blit(
                            EXAMPLE_FONT.render("Example:", True, EXAMPLE_COLOR),
                            (example_rect_visual.left + 10, ex_title_draw_y)
                        )

                        # Example lines
                        current_example_line_draw_y = ex_title_draw_y + ex_details["title_h"]
                        for ex_line_str in ex_details["texts"]:
                            if current_example_line_draw_y + EXAMPLE_FONT.get_height() <= self.command_area_bottom_limit + EXAMPLE_FONT.get_height() : # also check this for clipping
                                surface.blit(
                                    EXAMPLE_FONT.render(ex_line_str, True, EXAMPLE_COLOR),
                                    (example_rect_visual.left + 10 + 20, current_example_line_draw_y) # Indent examples
                                )
                            current_example_line_draw_y += EXAMPLE_FONT.get_height()
            
            else: # Undiscovered hidden command
                # Ensure blurred text also respects command_area_bottom_limit
                if y_pos_item_start < self.command_area_bottom_limit:
                    blur_text(surface, cmd, (self.screen_margin + 10, y_pos_item_start), BODY_FONT, HIDDEN_COLOR)
                    blur_text(surface, "??????????????????", (self.screen_margin + 150, y_pos_item_start), BODY_FONT, HIDDEN_COLOR)
        
        return clickable_areas

def draw_manual(surface: pygame.Surface, discovered: Set[str], mouse_pos: Tuple[int, int] | None, command_list_ref: CommandList) -> List[Tuple[pygame.Rect, str]]:
    """Draw the manual with the expandable command list."""
    # command_list = CommandList(discovered) # Instance is now managed in main loop
    return command_list_ref.draw(surface, mouse_pos)

def main():
    """Test function to display the manual."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Command Manual")
    clock = pygame.time.Clock()

    # Example: Discovered commands (replace with actual game logic)
    discovered_commands = {"ls", "pwd", "cd", "exit", "cat", "help", "clear", "ps"} 
    
    command_list = CommandList(discovered_commands) # Create instance here

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    clickable_areas_drawn = command_list.draw(screen, mouse_pos) # Get current clickable areas
                    for rect, action in clickable_areas_drawn:
                        if rect.collidepoint(event.pos):
                            if action == "scroll_up":
                                command_list.scroll(-1)
                                command_list.set_button_feedback("scroll_up", True)
                            elif action == "scroll_down":
                                command_list.scroll(1)
                                command_list.set_button_feedback("scroll_down", True)
                            else: # It's a command
                                command_list.toggle_command(action)
                            break 
                elif event.button == 4:  # Scroll wheel up
                    command_list.scroll(-1)
                    command_list.set_button_feedback("scroll_up", True)
                elif event.button == 5:  # Scroll wheel down
                    command_list.scroll(1)
                    command_list.set_button_feedback("scroll_down", True)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    command_list.scroll(-1)
                    command_list.set_button_feedback("scroll_up", True)
                elif event.key == pygame.K_DOWN:
                    command_list.scroll(1)
                    command_list.set_button_feedback("scroll_down", True)
                elif event.key == pygame.K_ESCAPE:
                    running = False # Allow exiting with ESC
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    command_list.set_button_feedback("scroll_up", False)
                elif event.key == pygame.K_DOWN:
                    command_list.set_button_feedback("scroll_down", False)


        screen.fill(BACKGROUND_COLOR)
        clickable_areas = draw_manual(screen, discovered_commands, mouse_pos, command_list)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main() 