import pygame
import math
from constants import *

# Draw the bar based on its position with pulsing glow effect
def draw_bar(screen, bar_position, glow_value):
    # Calculate pulsing glow value
    glow_intensity = 155 + int(100 * math.sin(glow_value))
    glow_color = (0, glow_intensity, 0)  # Terminal green glow
    
    # Draw the bar on the outer square now
    if bar_position == 0:  # Top
        pygame.draw.rect(screen, glow_color, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], OUTER_SQUARE_SIZE, BAR_THICKNESS))
    elif bar_position == 1:  # Right
        pygame.draw.rect(screen, glow_color, (OUTER_SQUARE_POS[0] + OUTER_SQUARE_SIZE - BAR_THICKNESS, OUTER_SQUARE_POS[1], BAR_THICKNESS, OUTER_SQUARE_SIZE))
    elif bar_position == 2:  # Bottom
        pygame.draw.rect(screen, glow_color, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1] + OUTER_SQUARE_SIZE - BAR_THICKNESS, OUTER_SQUARE_SIZE, BAR_THICKNESS))
    elif bar_position == 3:  # Left
        pygame.draw.rect(screen, glow_color, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], BAR_THICKNESS, OUTER_SQUARE_SIZE))

# Draw water ripples - terminal style (SIMPLIFIED)
def draw_water(screen, ripples, water_offset):
    # Draw outer square background with subtle grid pattern
    pygame.draw.rect(screen, BLACK, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], OUTER_SQUARE_SIZE, OUTER_SQUARE_SIZE))
    
    # Draw subtle grid pattern in outer square (space between inner and outer)
    cell_size = 20
    for x in range(OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[0] + OUTER_SQUARE_SIZE, cell_size):
        for y in range(OUTER_SQUARE_POS[1], OUTER_SQUARE_POS[1] + OUTER_SQUARE_SIZE, cell_size):
            # Only draw if in the outer square but not in the inner square
            in_inner_square = (
                x >= SQUARE_POS[0] and 
                x < SQUARE_POS[0] + SQUARE_SIZE and
                y >= SQUARE_POS[1] and 
                y < SQUARE_POS[1] + SQUARE_SIZE
            )
            
            if not in_inner_square:
                # Draw a very subtle pattern in the outer area
                char_index = int((x + y + water_offset * 3) % 4)
                if char_index == 0:
                    pygame.draw.rect(screen, (0, 40, 0), (x + 8, y + 8, 2, 2), 0)
    
    # Draw inner water background (dark area)
    pygame.draw.rect(screen, BLACK, (SQUARE_POS[0], SQUARE_POS[1], SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw ASCII-like grid pattern for water (REDUCED FLICKERING)
    cell_size = 20  # Increased from 10 to 20
    for x in range(SQUARE_POS[0], SQUARE_POS[0] + SQUARE_SIZE, cell_size):
        for y in range(SQUARE_POS[1], SQUARE_POS[1] + SQUARE_SIZE, cell_size):
            # Determine which character to draw based on position and time
            char_index = int((x + y + water_offset * 5) % 3)  # Reduced mod from 4 to 3, slowed animation
            if char_index == 0:
                pygame.draw.line(screen, DARK_GREEN, (x, y), (x + cell_size, y + cell_size), 1)
            elif char_index == 1:
                pygame.draw.line(screen, DARK_GREEN, (x + cell_size, y), (x, y + cell_size), 1)
            elif char_index == 2:
                pygame.draw.rect(screen, DARK_GREEN, (x + 3, y + 3, 2, 2), 0)
    
    # Draw simplified ripple effects
    for ripple in ripples:
        pygame.draw.circle(screen, GREEN, (int(ripple['x']), int(ripple['y'])), int(ripple['radius']), 1)

# Draw wind gust feedback effects (new function)
def draw_gust_feedback(screen, wind_gusts, flash_timer):
    # Draw feedback for collected and blocked gusts
    for gust in wind_gusts:
        if not gust.active:  # Only process inactive (already handled) gusts
            center_x, center_y = BOAT_CENTER
            
            if gust.collected:
                # Draw a positive feedback effect (expanding green circle)
                radius = flash_timer * 3
                if radius < 40:  # Only draw if still visible
                    alpha = max(0, 255 - (radius * 6))  # Fade out with size
                    color = (0, 255, 0, alpha)
                    
                    # Create a temporary surface with alpha
                    feedback_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(feedback_surf, color, (radius, radius), radius, 2)
                    screen.blit(feedback_surf, (center_x - radius, center_y - radius))
            
            elif gust.blocked:
                # Draw a neutral feedback effect (red X)
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
                # Draw a negative feedback effect (yellow caution lines)
                size = min(20, flash_timer * 2)
                if size > 0:
                    thickness = max(1, 2 - (flash_timer // 10))
                    spacing = 7
                    
                    # Draw caution stripes
                    for i in range(-2, 3):
                        pygame.draw.line(screen, YELLOW, 
                                       (center_x + (i*spacing), center_y - size),
                                       (center_x + (i*spacing), center_y + size), thickness)

# Simplified terminal-style boat
def draw_boat(screen, boat_offset):
    # Calculate boat bobbing effect
    bob_offset = math.sin(boat_offset) * 2
    
    # Boat center point with bobbing (visual effect only)
    boat_center = (BOAT_CENTER[0], BOAT_CENTER[1] + bob_offset)
    
    # Use the boat sprite image
    if not hasattr(draw_boat, 'boat_img'):
        try:
            # Load the image first time
            boat_img = pygame.image.load("sprites/boat.png").convert_alpha()
            # Scale it to appropriate size but preserve aspect ratio
            original_width, original_height = boat_img.get_size()
            target_width = BOAT_SIZE + 10  # Slightly larger than the original drawn boat
            # Calculate height to maintain aspect ratio
            target_height = int((original_height * target_width) / original_width)
            draw_boat.boat_img = pygame.transform.scale(boat_img, (target_width, target_height))
        except Exception as e:
            print(f"Boat image error: {e}. Falling back to drawn boat.")
            # If there's an error, we'll continue with drawn boat
            draw_boat.boat_img = None
    
    # If we successfully loaded the image, use it
    if hasattr(draw_boat, 'boat_img') and draw_boat.boat_img is not None:
        # Calculate position to center the boat sprite
        boat_width, boat_height = draw_boat.boat_img.get_size()
        boat_x = boat_center[0] - boat_width // 2
        boat_y = boat_center[1] - boat_height // 2
        
        # Blit the boat image at the calculated position
        screen.blit(draw_boat.boat_img, (boat_x, boat_y))
    else:
        # Fallback to drawing boat if image couldn't be loaded
        # Draw boat - ASCII-like representation
        # Boat outline
        pygame.draw.lines(screen, GREEN, True, [
            (boat_center[0], boat_center[1] - BOAT_SIZE // 2),  # Top
            (boat_center[0] + BOAT_SIZE // 2, boat_center[1]),  # Right
            (boat_center[0], boat_center[1] + BOAT_SIZE // 2),  # Bottom
            (boat_center[0] - BOAT_SIZE // 2, boat_center[1])   # Left
        ], 2)
        
        # Draw a mast as a simple line
        pygame.draw.line(screen, GREEN, 
                        (boat_center[0], boat_center[1]),
                        (boat_center[0], boat_center[1] - BOAT_SIZE // 1.5), 2)
        
        # Draw a simple sail as a triangle
        pygame.draw.lines(screen, GREEN, False, [
            (boat_center[0], boat_center[1] - BOAT_SIZE // 1.5),
            (boat_center[0] + BOAT_SIZE // 3, boat_center[1] - BOAT_SIZE // 3),
            (boat_center[0], boat_center[1] - BOAT_SIZE // 3)
        ], 1)

# Draw terminal-style border
def draw_terminal_border(screen, boat_speed, boat_acceleration, glow_value):
    # Border color changes with acceleration/speed to indicate danger level
    danger_level = max(abs(boat_acceleration) / MAX_ACCELERATION, abs(boat_speed) / MAX_SPEED)
    if danger_level < 0.3:
        border_color = GREEN  # Safe
    elif danger_level < 0.6:
        border_color = YELLOW  # Warning
    else:
        # Pulsing red for high danger
        pulse = int(155 + 100 * math.sin(glow_value))
        border_color = (255, pulse, pulse)  # Danger
    
    pygame.draw.rect(screen, border_color, (BORDER_MARGIN, BORDER_MARGIN, WIDTH - 2*BORDER_MARGIN, HEIGHT - 2*BORDER_MARGIN), BORDER_THICKNESS)
    
    # Draw corner characters
    # Top-left corner
    pygame.draw.line(screen, border_color, (BORDER_MARGIN, BORDER_MARGIN), (BORDER_MARGIN + CORNER_SIZE, BORDER_MARGIN), 2)
    pygame.draw.line(screen, border_color, (BORDER_MARGIN, BORDER_MARGIN), (BORDER_MARGIN, BORDER_MARGIN + CORNER_SIZE), 2)
    # Top-right corner
    pygame.draw.line(screen, border_color, (WIDTH - BORDER_MARGIN, BORDER_MARGIN), (WIDTH - BORDER_MARGIN - CORNER_SIZE, BORDER_MARGIN), 2)
    pygame.draw.line(screen, border_color, (WIDTH - BORDER_MARGIN, BORDER_MARGIN), (WIDTH - BORDER_MARGIN, BORDER_MARGIN + CORNER_SIZE), 2)
    # Bottom-left corner
    pygame.draw.line(screen, border_color, (BORDER_MARGIN, HEIGHT - BORDER_MARGIN), (BORDER_MARGIN + CORNER_SIZE, HEIGHT - BORDER_MARGIN), 2)
    pygame.draw.line(screen, border_color, (BORDER_MARGIN, HEIGHT - BORDER_MARGIN), (BORDER_MARGIN, HEIGHT - BORDER_MARGIN - CORNER_SIZE), 2)
    # Bottom-right corner
    pygame.draw.line(screen, border_color, (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN), (WIDTH - BORDER_MARGIN - CORNER_SIZE, HEIGHT - BORDER_MARGIN), 2)
    pygame.draw.line(screen, border_color, (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN), (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN - CORNER_SIZE), 2)
    
    # Draw title with difficulty indication in the top border
    font = pygame.font.SysFont("Courier New", 16)
    
    # Title changes based on current difficulty level
    if danger_level < 0.3:
        title_text = " TERMINAL BOAT NAVIGATION "
    elif danger_level < 0.6:
        title_text = " !!! WARNING: INCREASING TURBULENCE !!! "
    else:
        title_text = " !!! DANGER: EXTREME CONDITIONS !!! "
        
    title = font.render(title_text, True, border_color, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, BORDER_MARGIN - title.get_height() // 2))
    
    # Draw labels for the squares
    small_font = pygame.font.SysFont("Courier New", 12)
    
    # Label for outer square (controls)
    control_label = small_font.render("CONTROL ZONE", True, DARK_GREEN)
    screen.blit(control_label, (
        OUTER_SQUARE_POS[0] + OUTER_SQUARE_SIZE // 2 - control_label.get_width() // 2,
        OUTER_SQUARE_POS[1] - control_label.get_height() - 2
    ))
    
    # Label for inner square (navigation)
    nav_label = small_font.render("NAVIGATION ZONE", True, GREEN)
    screen.blit(nav_label, (
        SQUARE_POS[0] + SQUARE_SIZE // 2 - nav_label.get_width() // 2,
        SQUARE_POS[1] - nav_label.get_height() - 2
    ))

# Draw progress and speed meters
def draw_meters(screen, boat_speed, boat_acceleration, current_distance, glow_value):
    font = pygame.font.SysFont("Courier New", 14)
    
    # Draw speed meter in top-left corner
    speed_meter_width = 100
    speed_meter_height = 20
    speed_meter_x = 20
    speed_meter_y = 40
    
    # Draw meter background
    pygame.draw.rect(screen, DARK_GRAY, (speed_meter_x, speed_meter_y, speed_meter_width, speed_meter_height))
    
    # Calculate fill based on speed (centered at zero, expands left for negative, right for positive)
    if boat_speed >= 0:
        fill_width = int((boat_speed / MAX_SPEED) * (speed_meter_width / 2))
        fill_x = speed_meter_width / 2 + speed_meter_x
        pygame.draw.rect(screen, GREEN, (fill_x, speed_meter_y, fill_width, speed_meter_height))
    else:
        fill_width = int((boat_speed / MIN_SPEED) * (speed_meter_width / 2))
        fill_x = speed_meter_width / 2 + speed_meter_x - fill_width
        pygame.draw.rect(screen, RED, (fill_x, speed_meter_y, fill_width, speed_meter_height))
    
    # Draw center line
    center_x = speed_meter_x + speed_meter_width / 2
    pygame.draw.line(screen, WHITE, (center_x, speed_meter_y), (center_x, speed_meter_y + speed_meter_height), 1)
    
    # Draw border
    pygame.draw.rect(screen, GREEN, (speed_meter_x, speed_meter_y, speed_meter_width, speed_meter_height), 1)
    
    # Draw speed text
    speed_text = font.render(f"SPEED: {int(boat_speed)}", True, GREEN)
    screen.blit(speed_text, (speed_meter_x, speed_meter_y - 20))
    
    # Draw acceleration text
    accel_text = font.render(f"ACCEL: {boat_acceleration:.2f}", True, GREEN)
    screen.blit(accel_text, (speed_meter_x, speed_meter_y + 25))
    
    # Draw vertical progress bar on the right side of the screen
    progress_width = 20
    progress_height = HEIGHT - 100
    progress_x = WIDTH - 40
    progress_y = 50
    
    # Draw meter background
    pygame.draw.rect(screen, DARK_GRAY, (progress_x, progress_y, progress_width, progress_height))
    
    # Calculate fill based on progress (fills from bottom to top)
    progress_percentage = min(1.0, current_distance / TOTAL_DISTANCE)
    fill_height = int(progress_percentage * progress_height)
    fill_y = progress_y + progress_height - fill_height  # Start from bottom
    
    # Progress bar color changes with speed
    if boat_speed < 0:
        # Moving backward - red
        progress_color = RED
    elif boat_speed < MAX_SPEED * 0.3:
        # Slow - green
        progress_color = GREEN
    elif boat_speed < MAX_SPEED * 0.7:
        # Medium - yellow
        progress_color = YELLOW
    else:
        # Fast - pulsing cyan
        pulse = int(155 + 100 * math.sin(glow_value))
        progress_color = (0, 255, pulse)  # Cyan pulse
    
    pygame.draw.rect(screen, progress_color, (progress_x, fill_y, progress_width, fill_height))
    
    # Add distance markers (ticks) along the progress bar
    for i in range(1, 10):
        tick_y = progress_y + i * (progress_height / 10)
        tick_length = 5
        pygame.draw.line(screen, WHITE, 
                        (progress_x - tick_length, tick_y), 
                        (progress_x, tick_y), 1)
    
    # Draw border
    pygame.draw.rect(screen, GREEN, (progress_x, progress_y, progress_width, progress_height), 1)
    
    # Draw position arrow indicator
    arrow_size = 8
    arrow_x = progress_x - arrow_size - 2  # Position left of the progress bar
    arrow_y = fill_y - arrow_size // 2  # Center on current progress
    
    # Keep arrow within bar bounds
    arrow_y = max(progress_y, min(progress_y + progress_height - arrow_size, arrow_y))
    
    # Arrow color and animation based on speed
    arrow_color = progress_color
    arrow_wobble = 0
    if abs(boat_speed) > MAX_SPEED * 0.5:
        # Add wobble to arrow at high speeds
        arrow_wobble = int(math.sin(glow_value * 3) * 3)
    
    # Draw arrow pointing right (towards progress bar)
    pygame.draw.polygon(screen, arrow_color, [
        (arrow_x + arrow_wobble, arrow_y),  # Left point
        (arrow_x + arrow_size + arrow_wobble, arrow_y + arrow_size // 2),  # Right point (tip)
        (arrow_x + arrow_wobble, arrow_y + arrow_size)  # Bottom point
    ])
    
    # Draw destination label at top
    dest_text = font.render("DEST", True, GREEN)
    screen.blit(dest_text, (progress_x - 5, progress_y - 20))
    
    # Draw distance remaining at bottom
    remaining = int(TOTAL_DISTANCE - current_distance)
    if remaining > 0:
        dist_text = font.render(f"{remaining}", True, GREEN)
        screen.blit(dist_text, (progress_x - 5, progress_y + progress_height + 5))
    
    # Create a rectangle object for the progress bar (used for drawing hydra indicators)
    progress_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
    
    return progress_rect

def draw_status_line(screen, bar_position):
    font = pygame.font.SysFont("Courier New", 16)
    status_line = f"BAR: {'TOP' if bar_position == 0 else 'RIGHT' if bar_position == 1 else 'BOTTOM' if bar_position == 2 else 'LEFT'}"
    status_text = font.render(status_line, True, GREEN)
    screen.blit(status_text, (20, HEIGHT - 40)) 