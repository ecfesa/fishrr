import pygame
import math
from constants import *
from utils import get_font, draw_terminal_style_corner

def draw_menu(screen):
    """Draw the main menu screen with game title and options"""
    screen.fill(BLACK)
    
    # Draw terminal-style border
    pygame.draw.rect(screen, GREEN, (BORDER_MARGIN, BORDER_MARGIN, 
                                    WIDTH - 2*BORDER_MARGIN, 
                                    HEIGHT - 2*BORDER_MARGIN), BORDER_THICKNESS)
    
    # Draw corner characters with helper function
    corners = [
        (BORDER_MARGIN, BORDER_MARGIN, True, True),  # Top-left
        (WIDTH - BORDER_MARGIN, BORDER_MARGIN, True, False),  # Top-right
        (BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, True),  # Bottom-left
        (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, False)  # Bottom-right
    ]
    
    for x, y, is_top, is_left in corners:
        draw_terminal_style_corner(screen, GREEN, x, y, CORNER_SIZE, is_top, is_left)
    
    # Create common font objects to reuse with custom font
    title_font = get_font(38)
    secondary_font = get_font(18)
    danger_font = get_font(20)
    prompt_font = get_font(16)
    controls_font = get_font(14)
    options_font = get_font(20)
    mission_font = get_font(14)
    
    # Draw titles
    title_y = HEIGHT // 6 - 10
    
    title_elements = [
        (title_font, "HYDRA PROTOCOL", GREEN, title_y),
        (secondary_font, "MARITIME NAVIGATION SYSTEM", DARK_GREEN, title_y + 50)
    ]
    
    for font, text, color, y_pos in title_elements:
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y_pos))
    
    # Draw danger warning with flashing effect
    flash_color = RED if pygame.time.get_ticks() % 1000 < 500 else (180, 0, 0)
    danger_title = danger_font.render("!!! DANGER: HYDRAS DETECTED !!!", True, flash_color)
    screen.blit(danger_title, (WIDTH // 2 - danger_title.get_width() // 2, title_y + 85))
    
    # Load and draw hydra warning image
    if not hasattr(draw_menu, 'hydra_warning_img'):
        try:
            # Load and scale image
            hydra_warning_img = pygame.image.load("sprites/hydra_warning.png").convert_alpha()
            original_width, original_height = hydra_warning_img.get_size()
            target_width = 80
            target_height = int((original_height * target_width) / original_width)
            draw_menu.hydra_warning_img = pygame.transform.scale(hydra_warning_img, (target_width, target_height))
        except Exception as e:
            # Create fallback shape if image not found
            print(f"Hydra warning image error: {e}. Creating placeholder.")
            temp_surface = pygame.Surface((80, 60), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, RED, [(40, 0), (80, 60), (0, 60)])
            pygame.draw.polygon(temp_surface, (180, 0, 0), [(40, 10), (70, 55), (10, 55)], 3)
            draw_menu.hydra_warning_img = temp_surface
    
    # Position the hydra image
    hydra_x = WIDTH // 2 - draw_menu.hydra_warning_img.get_width() // 2
    hydra_y = title_y + 120
    
    # Add subtle pulsing effect to hydra image
    pulse_scale = 1.0 + 0.02 * math.sin(pygame.time.get_ticks() * 0.005)
    pulse_width = int(draw_menu.hydra_warning_img.get_width() * pulse_scale)
    pulse_height = int(draw_menu.hydra_warning_img.get_height() * pulse_scale)
    
    # Scale and center the image with pulse effect
    pulsed_hydra = pygame.transform.scale(draw_menu.hydra_warning_img, (pulse_width, pulse_height))
    pulse_x = WIDTH // 2 - pulse_width // 2
    pulse_y = hydra_y - (pulse_height - draw_menu.hydra_warning_img.get_height()) // 2
    
    screen.blit(pulsed_hydra, (pulse_x, pulse_y))
    
    # Draw mission info box
    hydra_bottom = pulse_y + pulsed_hydra.get_height()
    mission_box_width = 500
    mission_box_height = 80
    mission_box = pygame.Surface((mission_box_width, mission_box_height), pygame.SRCALPHA)
    mission_box.fill((0, 0, 0, 180))
    mission_y = hydra_bottom + 10
    
    screen.blit(mission_box, (WIDTH // 2 - mission_box_width // 2, mission_y - 10))
    
    # Draw mission text lines
    mission_lines = [
        "MISSION: Navigate to destination while outrunning hydra pursuers",
        "DANGER: Hydras will chase from behind - don't let them catch you!",
        "WARNING: Multiple hydras may spawn as you progress!"
    ]
    
    for line in mission_lines:
        mission_text = mission_font.render(line, True, YELLOW)
        screen.blit(mission_text, (WIDTH // 2 - mission_text.get_width() // 2, mission_y))
        mission_y += 25
    
    # Draw options with glow effect
    options_start_y = mission_y + 15
    
    glow_intensity = 155 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
    glow_color = (0, glow_intensity, 0)
    
    # Draw options box
    options_box_width = 300
    options_box_height = 70
    options_box = pygame.Surface((options_box_width, options_box_height), pygame.SRCALPHA)
    options_box.fill((0, 0, 0, 100))
    
    screen.blit(options_box, (WIDTH // 2 - options_box_width // 2, options_start_y - 5))
    
    # Draw menu options
    options = [
        ("[ENTER] START VOYAGE", glow_color, options_start_y),
        ("[ESC] ABANDON SHIP", GREEN, options_start_y + 35)
    ]
    
    for text, color, y_pos in options:
        option_text = options_font.render(text, True, color)
        screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, y_pos))
    
    # Show flashing prompt
    prompt_y = options[1][2] + 40  # Position after last option
    
    # Draw controls info
    controls_box_height = 75
    controls_y = HEIGHT - BORDER_MARGIN - 45 - controls_box_height
    
    # Ensure minimum spacing between prompt and controls
    if controls_y - prompt_y < 30:
        controls_y = prompt_y + 35
    
    # Draw controls box
    controls_box_width = 520
    controls_box = pygame.Surface((controls_box_width, controls_box_height), pygame.SRCALPHA)
    controls_box.fill((0, 30, 0, 200))
    
    screen.blit(controls_box, (WIDTH // 2 - controls_box_width // 2, controls_y - 5))
    
    # Draw controls title
    controls_title = get_font(16).render("CONTROLS:", True, GREEN)
    screen.blit(controls_title, (WIDTH // 2 - controls_box_width // 2 + 10, controls_y))
    
    # Draw control instructions
    control_instructions = [
        "• Use ARROW KEYS to position the bar",
        "• Collect wind by positioning bar on opposite side"
    ]
    
    for i, instruction in enumerate(control_instructions):
        control_text = controls_font.render(instruction, True, GREEN)
        screen.blit(control_text, (WIDTH // 2 - controls_box_width // 2 + 20, controls_y + 20 + i * 18))
    
    # Draw flashing "Press ENTER" prompt
    if pygame.time.get_ticks() % 1000 < 500:
        prompt = prompt_font.render("Press ENTER to begin", True, GREEN)
        prompt_width = prompt.get_width()
        prompt_height = prompt.get_height()
        
        # Draw box behind text
        prompt_box = pygame.Surface((prompt_width + 10, prompt_height + 6), pygame.SRCALPHA)
        prompt_box.fill((0, 0, 0, 100))
        screen.blit(prompt_box, (WIDTH // 2 - (prompt_width + 10) // 2, prompt_y - 3))
        
        # Draw prompt text
        screen.blit(prompt, (WIDTH // 2 - prompt_width // 2, prompt_y))

def draw_victory_screen(screen):
    """Draw a victory screen with animation"""
    screen.fill(BLACK)
    
    # Draw terminal-style border with green glow
    glow_value = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2  # 0 to 1 pulsing value
    border_color = (0, 200 + int(55 * glow_value), 0)  # Pulsing green
    
    pygame.draw.rect(screen, border_color, (BORDER_MARGIN, BORDER_MARGIN, 
                                          WIDTH - 2*BORDER_MARGIN, 
                                          HEIGHT - 2*BORDER_MARGIN), BORDER_THICKNESS)
    
    # Draw corner characters
    corners = [
        (BORDER_MARGIN, BORDER_MARGIN, True, True),  # Top-left
        (WIDTH - BORDER_MARGIN, BORDER_MARGIN, True, False),  # Top-right
        (BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, True),  # Bottom-left
        (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN, False, False)  # Bottom-right
    ]
    
    for x, y, is_top, is_left in corners:
        draw_terminal_style_corner(screen, border_color, x, y, CORNER_SIZE, is_top, is_left)
    
    # Draw victory text with animation
    title_font = get_font(40)
    subtitle_font = get_font(24)
    info_font = get_font(18)
    
    # Animated text color
    text_color = (0, 200 + int(55 * glow_value), 0)
    
    # Main title with shadow effect
    title_text = "MISSION ACCOMPLISHED"
    title_surf = title_font.render(title_text, True, text_color)
    shadow_surf = title_font.render(title_text, True, (0, 50, 0))
    
    title_y = HEIGHT // 3
    screen.blit(shadow_surf, (WIDTH // 2 - title_surf.get_width() // 2 + 3, title_y + 3))
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, title_y))
    
    # Subtitle
    subtitle = subtitle_font.render("DESTINATION REACHED SUCCESSFULLY", True, DARK_GREEN)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, title_y + 60))
    
    # Draw animated celebration particles (enhanced)
    current_time = pygame.time.get_ticks()
    for i in range(60):  # Increased from 40 to 60 particles for more celebration effect
        # Create a unique position for each particle based on time and index
        x = WIDTH // 2 + int(math.sin(current_time * 0.001 + i * 0.5) * WIDTH // 3)
        y = HEIGHT // 2 + int(math.cos(current_time * 0.001 + i * 0.5) * HEIGHT // 4)
        
        # Add more variety to movement patterns
        if i % 5 == 0:  # Every fifth particle follows a different pattern
            x = WIDTH // 3 + int(math.cos(current_time * 0.002 + i * 0.3) * WIDTH // 2.5)
            y = HEIGHT // 3 + int(math.sin(current_time * 0.0015 + i * 0.4) * HEIGHT // 3)
        elif i % 5 == 1:  # Another pattern
            x = WIDTH * 2 // 3 + int(math.sin(current_time * 0.0012 + i * 0.6) * WIDTH // 4)
            y = HEIGHT * 2 // 3 + int(math.cos(current_time * 0.0018 + i * 0.7) * HEIGHT // 3.5)
        elif i % 5 == 2:  # Spiral pattern
            angle = current_time * 0.001 + i * 0.2
            radius = 50 + int(math.sin(current_time * 0.0005 + i * 0.1) * 30)
            x = WIDTH // 2 + int(math.cos(angle) * radius)
            y = HEIGHT // 2 + int(math.sin(angle) * radius)
        elif i % 5 == 3:  # Zigzag pattern
            x = WIDTH // 2 + int(math.sin(current_time * 0.002 + i * 0.4) * WIDTH // 4)
            y = HEIGHT // 2 + int(math.sin(current_time * 0.004 + i * 0.3) * HEIGHT // 5)
        
        # More color variety
        if i % 6 == 0:
            particle_color = GREEN
        elif i % 6 == 1:
            particle_color = YELLOW
        elif i % 6 == 2:
            particle_color = (0, 180, 180)  # Teal
        elif i % 6 == 3:
            particle_color = (180, 180, 0)  # Gold
        elif i % 6 == 4:
            particle_color = (0, 255, 100)  # Lime
        else:
            particle_color = (100, 255, 100)  # Light green
        
        # More size variety
        particle_size = 2 + int(math.sin(current_time * 0.002 + i) * 3)
        
        # Draw the particle
        pygame.draw.circle(screen, particle_color, (x, y), particle_size)
        
        # Add trail effect for some particles
        if i % 4 == 0:
            trail_x = x - int(math.sin(current_time * 0.001 + i * 0.5) * 5)
            trail_y = y - int(math.cos(current_time * 0.001 + i * 0.5) * 5)
            pygame.draw.circle(screen, (particle_color[0]//2, particle_color[1]//2, particle_color[2]//2), 
                              (trail_x, trail_y), particle_size//2)
    
    # Instructions
    time_based_visibility = pygame.time.get_ticks() % 1000 < 500  # Flash every half second
    if time_based_visibility:
        info_text = info_font.render("Press any key to return to menu", True, GREEN)
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT - 100))

def draw_pause_menu(screen):
    """Draw the pause menu screen"""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Draw a terminal-style border for the pause menu
    menu_width, menu_height = 400, 250
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2
    
    # Draw menu background and border
    pygame.draw.rect(overlay, BLACK, (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(overlay, GREEN, (menu_x, menu_y, menu_width, menu_height), BORDER_THICKNESS)
    
    # Draw corner characters
    corners = [
        (menu_x, menu_y, True, True),  # Top-left
        (menu_x + menu_width, menu_y, True, False),  # Top-right
        (menu_x, menu_y + menu_height, False, True),  # Bottom-left
        (menu_x + menu_width, menu_y + menu_height, False, False)  # Bottom-right
    ]
    
    for x, y, is_top, is_left in corners:
        draw_terminal_style_corner(overlay, GREEN, x, y, CORNER_SIZE, is_top, is_left)
    
    # Draw title
    title_font = get_font(30)
    title_text = "SYSTEM PAUSED"
    title_surf = title_font.render(title_text, True, GREEN)
    overlay.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, menu_y + 30))
    
    # Draw options
    options_font = get_font(20)
    options = [
        ("[SPACE] RESUME NAVIGATION", GREEN),
        ("[ESC] RETURN TO MAIN MENU", DARK_GREEN)
    ]
    
    for i, (text, color) in enumerate(options):
        option_text = options_font.render(text, True, color)
        overlay.blit(option_text, 
                   (WIDTH // 2 - option_text.get_width() // 2, 
                    menu_y + 100 + i * 40))
    
    screen.blit(overlay, (0, 0))

def draw_game_over(screen, message):
    """Draw game over screen with the provided message"""
    screen.fill(BLACK)
    font = get_font(30)
    text = font.render(message, True, GREEN)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    
    # Draw return to menu message
    small_font = get_font(16)
    return_text = small_font.render("Returning to menu...", True, DARK_GREEN)
    screen.blit(return_text, (WIDTH // 2 - return_text.get_width() // 2, HEIGHT // 2 + 50)) 