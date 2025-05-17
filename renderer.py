import pygame
import math
from constants import *
from utils import get_font, draw_terminal_style_corner, draw_glow_color

# Draw the bar based on its position with pulsing glow effect
def draw_bar(screen, bar_position, glow_value):
    # Calculate pulsing glow effect
    glow_intensity = 155 + int(100 * math.sin(glow_value))
    glow_color = (0, glow_intensity, 0)
    
    # Draw the bar on the inner square (changed from outer)
    bar_positions = [
        (SQUARE_POS[0], SQUARE_POS[1], SQUARE_SIZE, BAR_THICKNESS),  # Top
        (SQUARE_POS[0] + SQUARE_SIZE - BAR_THICKNESS, SQUARE_POS[1], BAR_THICKNESS, SQUARE_SIZE),  # Right
        (SQUARE_POS[0], SQUARE_POS[1] + SQUARE_SIZE - BAR_THICKNESS, SQUARE_SIZE, BAR_THICKNESS),  # Bottom
        (SQUARE_POS[0], SQUARE_POS[1], BAR_THICKNESS, SQUARE_SIZE)  # Left
    ]
    
    pygame.draw.rect(screen, glow_color, bar_positions[bar_position])

# Draw water ripples - terminal style
def draw_water(screen, ripples, water_offset):
    """Draw a simplified water background with moving patterns but no static circles"""
    # Draw outer square background with subtle grid pattern
    pygame.draw.rect(screen, BLACK, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], 
                                    OUTER_SQUARE_SIZE, OUTER_SQUARE_SIZE))
    
    # Draw subtle grid pattern in outer square (space between inner and outer)
    cell_size = 20
    for x in range(OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[0] + OUTER_SQUARE_SIZE, cell_size):
        for y in range(OUTER_SQUARE_POS[1], OUTER_SQUARE_POS[1] + OUTER_SQUARE_SIZE, cell_size):
            # Skip drawing if in the inner square
            if (x >= SQUARE_POS[0] and x < SQUARE_POS[0] + SQUARE_SIZE and
                y >= SQUARE_POS[1] and y < SQUARE_POS[1] + SQUARE_SIZE):
                continue
                
            # Draw a very subtle pattern in the outer area
            if int((x + y + water_offset * 3) % 4) == 0:
                pygame.draw.rect(screen, (0, 40, 0), (x + 8, y + 8, 2, 2), 0)
    
    # Draw inner water background
    pygame.draw.rect(screen, BLACK, (SQUARE_POS[0], SQUARE_POS[1], SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw ASCII-like grid pattern for water (reduced flickering)
    for x in range(SQUARE_POS[0], SQUARE_POS[0] + SQUARE_SIZE, cell_size):
        for y in range(SQUARE_POS[1], SQUARE_POS[1] + SQUARE_SIZE, cell_size):
            # Determine which character to draw based on position and time
            char_index = int((x + y + water_offset * 5) % 3)
            if char_index == 0:
                pygame.draw.line(screen, DARK_GREEN, (x, y), (x + cell_size, y + cell_size), 1)
            elif char_index == 1:
                pygame.draw.line(screen, DARK_GREEN, (x + cell_size, y), (x, y + cell_size), 1)
            elif char_index == 2:
                pygame.draw.rect(screen, DARK_GREEN, (x + 3, y + 3, 2, 2), 0)
    
    # No ripple effects (static circles) are drawn

# Draw wind gust feedback effects
def draw_gust_feedback(screen, wind_gusts, flash_timer):
    center_x, center_y = BOAT_CENTER
    
    for gust in wind_gusts:
        if not gust.active:  # Only process inactive (already handled) gusts
            if gust.collected:
                # Draw positive feedback (expanding green circle)
                radius = flash_timer * 3
                if radius < 40:
                    alpha = max(0, 255 - (radius * 6))
                    feedback_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(feedback_surf, (0, 255, 0, alpha), (radius, radius), radius, 2)
                    screen.blit(feedback_surf, (center_x - radius, center_y - radius))
            
            elif gust.blocked:
                # Draw neutral feedback (red X)
                size = min(30, flash_timer * 3)
                if size > 0:
                    thickness = max(1, 3 - (flash_timer // 10))
                    pygame.draw.line(screen, RED, 
                                    (center_x - size, center_y - size),
                                    (center_x + size, center_y + size), thickness)
                    pygame.draw.line(screen, RED, 
                                    (center_x + size, center_y - size),
                                    (center_x - size, center_y + size), thickness)
            
            elif gust.missed:
                # Draw negative feedback (yellow caution lines)
                size = min(20, flash_timer * 2)
                if size > 0:
                    thickness = max(1, 2 - (flash_timer // 10))
                    spacing = 7
                    
                    for i in range(-2, 3):
                        pygame.draw.line(screen, YELLOW, 
                                        (center_x + (i*spacing), center_y - size),
                                        (center_x + (i*spacing), center_y + size), thickness)

# Draw boat with image or fallback to drawn version
def draw_boat(screen, boat_offset):
    # Calculate boat bobbing effect
    bob_offset = math.sin(boat_offset) * 2
    boat_center = (BOAT_CENTER[0], BOAT_CENTER[1] + bob_offset)
    
    # Try to load and cache boat image
    if not hasattr(draw_boat, 'boat_img'):
        try:
            boat_img = pygame.image.load("sprites/boat.png").convert_alpha()
            # Scale image preserving aspect ratio
            original_width, original_height = boat_img.get_size()
            target_width = BOAT_SIZE + 10
            target_height = int((original_height * target_width) / original_width)
            draw_boat.boat_img = pygame.transform.scale(boat_img, (target_width, target_height))
        except Exception as e:
            print(f"Boat image error: {e}. Using drawn boat.")
            draw_boat.boat_img = None
    
    # Use image if available, otherwise draw the boat
    if hasattr(draw_boat, 'boat_img') and draw_boat.boat_img is not None:
        boat_width, boat_height = draw_boat.boat_img.get_size()
        boat_x = boat_center[0] - boat_width // 2
        boat_y = boat_center[1] - boat_height // 2
        screen.blit(draw_boat.boat_img, (boat_x, boat_y))
    else:
        # Draw a simple boat shape
        pygame.draw.lines(screen, GREEN, True, [
            (boat_center[0], boat_center[1] - BOAT_SIZE // 2),  # Top
            (boat_center[0] + BOAT_SIZE // 2, boat_center[1]),  # Right
            (boat_center[0], boat_center[1] + BOAT_SIZE // 2),  # Bottom
            (boat_center[0] - BOAT_SIZE // 2, boat_center[1])   # Left
        ], 2)
        
        # Draw mast and sail
        pygame.draw.line(screen, GREEN, 
                        (boat_center[0], boat_center[1]),
                        (boat_center[0], boat_center[1] - BOAT_SIZE // 1.5), 2)
        
        pygame.draw.lines(screen, GREEN, False, [
            (boat_center[0], boat_center[1] - BOAT_SIZE // 1.5),
            (boat_center[0] + BOAT_SIZE // 3, boat_center[1] - BOAT_SIZE // 3),
            (boat_center[0], boat_center[1] - BOAT_SIZE // 3)
        ], 1)

# Draw terminal-style border with corners
def draw_terminal_border(screen, boat_speed, boat_acceleration, glow_value):
    # Determine border color based on danger level
    danger_level = max(abs(boat_acceleration) / MAX_ACCELERATION, abs(boat_speed) / MAX_SPEED)
    
    if danger_level < 0.3:
        border_color = GREEN  # Safe
    elif danger_level < 0.6:
        border_color = YELLOW  # Warning
    else:
        # Pulsing red for high danger
        border_color = (255, 155 + 100 * math.sin(glow_value), 155 + 100 * math.sin(glow_value))
    
    # Draw the main border
    pygame.draw.rect(screen, border_color, 
                    (BORDER_MARGIN, BORDER_MARGIN, 
                     WIDTH - 2*BORDER_MARGIN, HEIGHT - 2*BORDER_MARGIN), 
                    BORDER_THICKNESS)
    
    # Draw corner characters
    corners = [
        (BORDER_MARGIN, BORDER_MARGIN, True, True),  # Top-left
        (WIDTH - BORDER_MARGIN, BORDER_MARGIN, True, False),  # Top-right
        (BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, True),  # Bottom-left
        (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, False)  # Bottom-right
    ]
    
    for x, y, is_top, is_left in corners:
        draw_terminal_style_corner(screen, border_color, x, y, CORNER_SIZE, is_top, is_left)
    
    # Draw title with difficulty indication
    font = get_font(16)
    
    if danger_level < 0.3:
        title_text = " TERMINAL BOAT NAVIGATION "
    elif danger_level < 0.6:
        title_text = " !!! WARNING: INCREASING TURBULENCE !!! "
    else:
        title_text = " !!! DANGER: EXTREME CONDITIONS !!! "
    
    # Draw text with background
    text_surf = font.render(title_text, True, border_color)
    text_width = text_surf.get_width()
    text_height = text_surf.get_height()
    
    # Position text at top center
    text_x = WIDTH // 2 - text_width // 2
    text_y = BORDER_MARGIN - text_height // 2
    
    # Draw background
    bg_margin = 5
    pygame.draw.rect(screen, BLACK, 
                    (text_x - bg_margin, 
                     text_y - bg_margin // 2, 
                     text_width + bg_margin * 2, 
                     text_height + bg_margin))
    
    # Draw text
    screen.blit(text_surf, (text_x, text_y))
    
    # Draw small version info in bottom right
    small_font = get_font(12)
    version_text = "v1.0"
    version_surf = small_font.render(version_text, True, DARK_GREEN)
    screen.blit(version_surf, (WIDTH - BORDER_MARGIN - version_surf.get_width() - 10, 
                             HEIGHT - BORDER_MARGIN - version_surf.get_height() - 5))
    
    # Draw square labels
    small_font = get_font(12)
    
    labels = [
        ("NAVIGATION ZONE", DARK_GREEN, 
         OUTER_SQUARE_POS[0] + OUTER_SQUARE_SIZE // 2, 
         OUTER_SQUARE_POS[1] - 2),
        
        ("CONTROL ZONE", GREEN, 
         SQUARE_POS[0] + SQUARE_SIZE // 2, 
         SQUARE_POS[1] - 2)
    ]
    
    for text, color, x, y in labels:
        label = small_font.render(text, True, color)
        screen.blit(label, (x - label.get_width() // 2, y - label.get_height()))

# Draw progress and speed meters
def draw_meters(screen, boat_speed, boat_acceleration, current_distance, glow_value):
    font = get_font(14)
    
    # Draw speed meter in top-left
    speed_meter_width = 100
    speed_meter_height = 20
    speed_meter_x = 20
    speed_meter_y = 40
    
    # Draw meter background
    pygame.draw.rect(screen, DARK_GRAY, 
                    (speed_meter_x, speed_meter_y, speed_meter_width, speed_meter_height))
    
    # Calculate speed meter fill
    center_x = speed_meter_x + speed_meter_width / 2
    if boat_speed >= 0:
        fill_width = int((boat_speed / MAX_SPEED) * (speed_meter_width / 2))
        fill_x = center_x
        fill_color = GREEN
    else:
        fill_width = int((boat_speed / MIN_SPEED) * (speed_meter_width / 2))
        fill_x = center_x - fill_width
        fill_color = RED
    
    if fill_width > 0:
        pygame.draw.rect(screen, fill_color, 
                        (fill_x, speed_meter_y, fill_width, speed_meter_height))
    
    # Draw center line and border
    pygame.draw.line(screen, WHITE, 
                    (center_x, speed_meter_y), 
                    (center_x, speed_meter_y + speed_meter_height), 1)
    
    pygame.draw.rect(screen, GREEN, 
                    (speed_meter_x, speed_meter_y, speed_meter_width, speed_meter_height), 1)
    
    # Draw speed and acceleration text
    texts = [
        (f"SPEED: {int(boat_speed)}", speed_meter_x, speed_meter_y - 20),
        (f"ACCEL: {boat_acceleration:.2f}", speed_meter_x, speed_meter_y + 25)
    ]
    
    for text, x, y in texts:
        screen.blit(font.render(text, True, GREEN), (x, y))
    
    # Draw vertical progress bar
    progress_width = 20
    progress_height = HEIGHT - 100
    progress_x = WIDTH - 40
    progress_y = 50
    
    # Draw meter background
    pygame.draw.rect(screen, DARK_GRAY, 
                    (progress_x, progress_y, progress_width, progress_height))
    
    # Calculate progress fill
    progress_percentage = min(1.0, current_distance / TOTAL_DISTANCE)
    fill_height = int(progress_percentage * progress_height)
    fill_y = progress_y + progress_height - fill_height
    
    # Determine progress color based on speed
    if boat_speed < 0:
        progress_color = RED  # Moving backward
    elif boat_speed < MAX_SPEED * 0.3:
        progress_color = GREEN  # Slow
    elif boat_speed < MAX_SPEED * 0.7:
        progress_color = YELLOW  # Medium
    else:
        # Fast - pulsing cyan
        pulse = int(155 + 100 * math.sin(glow_value))
        progress_color = (0, 255, pulse)
    
    # Draw progress fill
    if fill_height > 0:
        pygame.draw.rect(screen, progress_color, 
                        (progress_x, fill_y, progress_width, fill_height))
    
    # Draw distance markers
    for i in range(1, 10):
        tick_y = progress_y + i * (progress_height / 10)
        pygame.draw.line(screen, WHITE, 
                        (progress_x - 5, tick_y), 
                        (progress_x, tick_y), 1)
    
    # Draw border
    pygame.draw.rect(screen, GREEN, 
                    (progress_x, progress_y, progress_width, progress_height), 1)
    
    # Draw position arrow indicator
    arrow_size = 8
    arrow_x = progress_x - arrow_size - 2
    arrow_y = fill_y - arrow_size // 2
    
    # Keep arrow within bar bounds
    arrow_y = max(progress_y, min(progress_y + progress_height - arrow_size, arrow_y))
    
    # Arrow color and animation
    arrow_color = progress_color
    arrow_wobble = 0
    if abs(boat_speed) > MAX_SPEED * 0.5:
        arrow_wobble = int(math.sin(glow_value * 3) * 3)
    
    # Draw arrow pointing to progress bar
    pygame.draw.polygon(screen, arrow_color, [
        (arrow_x + arrow_wobble, arrow_y),
        (arrow_x + arrow_size + arrow_wobble, arrow_y + arrow_size // 2),
        (arrow_x + arrow_wobble, arrow_y + arrow_size)
    ])
    
    # Draw destination and distance labels
    labels = [
        ("DEST", progress_x - 5, progress_y - 20),
        (f"{int(TOTAL_DISTANCE - current_distance)}", progress_x - 5, progress_y + progress_height + 5)
    ]
    
    for text, x, y in labels:
        if text.isdigit() and int(text) <= 0:
            continue  # Skip showing distance if we've arrived
        screen.blit(font.render(text, True, GREEN), (x, y))
    
    # Return progress bar rect for hydra indicators
    return pygame.Rect(progress_x, progress_y, progress_width, progress_height)

def draw_status_line(screen, bar_position):
    # Bar position labels
    font = get_font(16)
    
    # Position names
    positions = ["FORWARD", "STARBOARD", "AFT", "PORT"]
    
    # Draw the current position
    status_text = f"BAR: {positions[bar_position]}"
    status_surf = font.render(status_text, True, GREEN)
    
    # Position centered at bottom
    screen.blit(status_surf, (WIDTH // 2 - status_surf.get_width() // 2, 
                            HEIGHT - BORDER_MARGIN - 20))