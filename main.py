import pygame
import sys
import math
import random
from constants import *
from entities import WindGust, MovingObject, Hydra
from renderer import (
    draw_bar, draw_water, draw_boat, draw_terminal_border,
    draw_meters, draw_status_line, draw_gust_feedback
)

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Terminal Boat Navigation")
clock = pygame.time.Clock()

def draw_menu():
    """Draw the main menu screen with game title and options"""
    screen.fill(BLACK)
    
    # Draw terminal-style border
    pygame.draw.rect(screen, GREEN, (BORDER_MARGIN, BORDER_MARGIN, 
                                    WIDTH - 2*BORDER_MARGIN, 
                                    HEIGHT - 2*BORDER_MARGIN), BORDER_THICKNESS)
    
    # Draw corner characters (terminal style)
    # Top-left corner
    pygame.draw.line(screen, GREEN, (BORDER_MARGIN, BORDER_MARGIN), 
                    (BORDER_MARGIN + CORNER_SIZE, BORDER_MARGIN), 2)
    pygame.draw.line(screen, GREEN, (BORDER_MARGIN, BORDER_MARGIN), 
                    (BORDER_MARGIN, BORDER_MARGIN + CORNER_SIZE), 2)
    # Top-right corner
    pygame.draw.line(screen, GREEN, (WIDTH - BORDER_MARGIN, BORDER_MARGIN), 
                    (WIDTH - BORDER_MARGIN - CORNER_SIZE, BORDER_MARGIN), 2)
    pygame.draw.line(screen, GREEN, (WIDTH - BORDER_MARGIN, BORDER_MARGIN), 
                    (WIDTH - BORDER_MARGIN, BORDER_MARGIN + CORNER_SIZE), 2)
    # Bottom-left corner
    pygame.draw.line(screen, GREEN, (BORDER_MARGIN, HEIGHT - BORDER_MARGIN), 
                    (BORDER_MARGIN + CORNER_SIZE, HEIGHT - BORDER_MARGIN), 2)
    pygame.draw.line(screen, GREEN, (BORDER_MARGIN, HEIGHT - BORDER_MARGIN), 
                    (BORDER_MARGIN, HEIGHT - BORDER_MARGIN - CORNER_SIZE), 2)
    # Bottom-right corner
    pygame.draw.line(screen, GREEN, (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN), 
                    (WIDTH - BORDER_MARGIN - CORNER_SIZE, HEIGHT - BORDER_MARGIN), 2)
    pygame.draw.line(screen, GREEN, (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN), 
                    (WIDTH - BORDER_MARGIN, HEIGHT - BORDER_MARGIN - CORNER_SIZE), 2)
    
    # Draw title - new title as requested
    title_font = pygame.font.SysFont("Courier New", 38)
    title = title_font.render("HYDRA PROTOCOL", True, GREEN)
    title_y = HEIGHT // 6 - 10  # Move title up slightly for better spacing
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))
    
    # Secondary title instead of subtitle
    secondary_title_font = pygame.font.SysFont("Courier New", 18)
    secondary_title = secondary_title_font.render("MARITIME NAVIGATION SYSTEM", True, DARK_GREEN)
    screen.blit(secondary_title, (WIDTH // 2 - secondary_title.get_width() // 2, title_y + 50))
    
    # Draw danger warning about hydras - optimized size
    danger_font = pygame.font.SysFont("Courier New", 20)  # Reduced from 24
    # Add flashing effect - alternate between bright red and darker red
    flash_color = RED if pygame.time.get_ticks() % 1000 < 500 else (180, 0, 0)
    danger_title = danger_font.render("!!! DANGER: HYDRAS DETECTED !!!", True, flash_color)
    screen.blit(danger_title, (WIDTH // 2 - danger_title.get_width() // 2, title_y + 85))
    
    # Load and draw hydra warning image
    if not hasattr(draw_menu, 'hydra_warning_img'):
        try:
            # Load the image first time
            hydra_warning_img = pygame.image.load("sprites/hydra_warning.png").convert_alpha()
            # Scale it to appropriate size but preserve aspect ratio - REDUCED SIZE
            original_width, original_height = hydra_warning_img.get_size()
            target_width = 80  # Reduced from 120 to 80
            # Calculate height to maintain aspect ratio
            target_height = int((original_height * target_width) / original_width)
            draw_menu.hydra_warning_img = pygame.transform.scale(hydra_warning_img, (target_width, target_height))
        except Exception as e:
            # Create a simple shape if image not found
            print(f"Hydra warning image error: {e}. Creating placeholder.")
            temp_surface = pygame.Surface((80, 60), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, RED, [(40, 0), (80, 60), (0, 60)])
            pygame.draw.polygon(temp_surface, (180, 0, 0), [(40, 10), (70, 55), (10, 55)], 3)
            draw_menu.hydra_warning_img = temp_surface
    
    # Position the hydra image to match the new title position
    hydra_x = WIDTH // 2 - draw_menu.hydra_warning_img.get_width() // 2
    hydra_y = title_y + 120  # Position relative to title
    
    # Draw the hydra with a very subtle pulsing effect
    pulse_scale = 1.0 + 0.02 * math.sin(pygame.time.get_ticks() * 0.005)  # Further reduced pulse
    pulse_width = int(draw_menu.hydra_warning_img.get_width() * pulse_scale)
    pulse_height = int(draw_menu.hydra_warning_img.get_height() * pulse_scale)
    pulsed_hydra = pygame.transform.scale(draw_menu.hydra_warning_img, (pulse_width, pulse_height))
    
    # Recenter after pulse scaling
    pulse_x = WIDTH // 2 - pulse_width // 2
    pulse_y = hydra_y - (pulse_height - draw_menu.hydra_warning_img.get_height()) // 2
    
    # Draw the hydra
    screen.blit(pulsed_hydra, (pulse_x, pulse_y))
    
    # Draw mission info - improved spacing and readability
    mission_font = pygame.font.SysFont("Courier New", 14)  # Reduced font size for better fit
    
    # Calculate the position of the mission box to be higher
    hydra_bottom = pulse_y + pulsed_hydra.get_height()
    
    # Draw a semi-transparent background for better text readability
    mission_box_width = 500  # Kept same width
    mission_box_height = 80  # Kept same height
    mission_box = pygame.Surface((mission_box_width, mission_box_height), pygame.SRCALPHA)
    mission_box.fill((0, 0, 0, 180))  # Semi-transparent black
    
    # Position mission box with proper spacing after hydra image
    mission_y = hydra_bottom + 10
    
    screen.blit(mission_box, (WIDTH // 2 - mission_box_width // 2, mission_y - 10))
    
    mission_lines = [
        "MISSION: Navigate to destination while outrunning hydra pursuers",
        "DANGER: Hydras will chase from behind - don't let them catch you!",
        "WARNING: Multiple hydras may spawn as you progress!"
    ]
    
    for line in mission_lines:
        mission_text = mission_font.render(line, True, YELLOW)
        screen.blit(mission_text, (WIDTH // 2 - mission_text.get_width() // 2, mission_y))
        mission_y += 25  # Increased line spacing
    
    # Draw options - position relative to mission box
    options_font = pygame.font.SysFont("Courier New", 20)  # Smaller font size
    
    # Calculate position relative to the end of the mission box
    options_start_y = mission_y + 15  # Reduced gap after mission info
    
    # Create glow effect for options
    glow_intensity = 155 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
    glow_color = (0, glow_intensity, 0)  # Terminal green glow
    
    # Draw background box for options
    options_box_width = 300
    options_box_height = 70
    options_box = pygame.Surface((options_box_width, options_box_height), pygame.SRCALPHA)
    options_box.fill((0, 0, 0, 100))  # Very subtle background
    
    screen.blit(options_box, (WIDTH // 2 - options_box_width // 2, options_start_y - 5))
    
    # Start Game option (highlighted)
    start_text = options_font.render("[ENTER] START VOYAGE", True, glow_color)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, options_start_y))
    
    # Exit Game option
    exit_text = options_font.render("[ESC] ABANDON SHIP", True, GREEN)
    exit_y = options_start_y + 35  # Reduced spacing
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, exit_y))
    
    # Show flashing prompt - position to not overlap with other elements
    prompt_font = pygame.font.SysFont("Courier New", 16)  # Smaller font
    
    # Calculate position to be safely between options and controls
    prompt_y = exit_y + 40  # Adequate spacing after options
    
    # Draw controls info with improved visibility and compact design
    controls_font = pygame.font.SysFont("Courier New", 14)  # Smaller font
    
    # Calculate position to ensure it fits at the bottom without overlapping with prompt
    controls_box_height = 75  # Even shorter box (reduced from 80)
    
    # Move controls box up higher to prevent clipping with Windows 125% scaling
    controls_y = HEIGHT - BORDER_MARGIN - 45 - controls_box_height  # Much more space from bottom
    
    # Ensure minimum spacing between prompt and controls
    if controls_y - prompt_y < 30:
        controls_y = prompt_y + 35
    
    # Draw a semi-transparent background for the controls
    controls_box_width = 520  # Narrower box
    controls_box = pygame.Surface((controls_box_width, controls_box_height), pygame.SRCALPHA)
    controls_box.fill((0, 30, 0, 200))  # Dark green semi-transparent
    
    screen.blit(controls_box, (WIDTH // 2 - controls_box_width // 2, controls_y - 5))
    
    # Control title with emphasis
    controls_title = pygame.font.SysFont("Courier New", 16).render("CONTROLS:", True, GREEN)
    screen.blit(controls_title, (WIDTH // 2 - controls_box_width // 2 + 10, controls_y))
    
    # Control instructions - shortened text slightly
    controls1 = controls_font.render("• Use ARROW KEYS to position the bar", True, GREEN)
    controls2 = controls_font.render("• Collect wind by positioning bar on opposite side", True, GREEN)
    controls3 = controls_font.render("• Block harmful wind by positioning bar on same side", True, GREEN)
    
    # Position the control text with tighter spacing
    screen.blit(controls1, (WIDTH // 2 - controls_box_width // 2 + 20, controls_y + 20))
    screen.blit(controls2, (WIDTH // 2 - controls_box_width // 2 + 20, controls_y + 38))
    screen.blit(controls3, (WIDTH // 2 - controls_box_width // 2 + 20, controls_y + 56))
    
    # Draw subtle background for visibility
    time_based_visibility = pygame.time.get_ticks() % 1000 < 500  # Flash every half second
    if time_based_visibility:
        prompt = prompt_font.render("Press ENTER to begin", True, GREEN)
        prompt_width = prompt.get_width()
        prompt_height = prompt.get_height()
        
        # Draw subtle box behind text
        prompt_box = pygame.Surface((prompt_width + 10, prompt_height + 6), pygame.SRCALPHA)
        prompt_box.fill((0, 0, 0, 100))
        screen.blit(prompt_box, (WIDTH // 2 - (prompt_width + 10) // 2, prompt_y - 3))
        
        # Draw prompt text
        screen.blit(prompt, (WIDTH // 2 - prompt_width // 2, prompt_y))

def run_game():
    """Run the main game loop"""
    # Bar position: 0 = top, 1 = right, 2 = bottom, 3 = left
    bar_position = 0

    # Animation variables
    glow_value = 0
    glow_direction = 1
    water_offset = 0
    boat_offset = 0

    # Physics variables 
    boat_acceleration = 0  # Current acceleration
    boat_speed = 0  # Current speed
    current_distance = 0  # Distance traveled so far

    # Difficulty stage thresholds - adjusted to be slightly easier
    EASY_THRESHOLD = TOTAL_DISTANCE / 3  # First third is easy
    MEDIUM_THRESHOLD = TOTAL_DISTANCE * 2 / 3  # Second third is medium
    # Last third is hard

    # Current difficulty stage
    current_stage = "EASY"
    
    # Difficulty parameters based on stage - reduced for balance with hydras
    difficulty_factor = 0.8  # Base value, will be adjusted by stage (reduced from 1.0)
    gust_frequency_modifier = 0.8  # How frequently gusts appear
    gust_pattern_predictability = 0.9  # How predictable are gust patterns (0-1)
    warning_time_modifier = 1.6  # Modifier for warning time (increased from 1.2)
    wobble_intensity = 0.4  # How much gusts wobble (0-1) (reduced from 0.5)

    # Hydras chasing the boat
    hydras = []
    
    # Hydra spawn parameters
    initial_hydra_spawn_distance = 15000  # Delay first hydra until player reaches this distance
    next_hydra_spawn = initial_hydra_spawn_distance  # Distance at which first hydra will spawn
    hydra_spawn_distance_range = (2000, 4000)  # Range for random spawn distance behind boat
    max_active_hydras = 3  # Maximum number of hydras active at once
    
    # Debugging flag - only output to console, not screen
    debug_mode = False
    debug_frame_counter = 0

    # Water ripples
    ripples = []
    for _ in range(5):
        ripples.append({
            'x': random.randint(SQUARE_POS[0], SQUARE_POS[0] + SQUARE_SIZE),
            'y': random.randint(SQUARE_POS[1], SQUARE_POS[1] + SQUARE_SIZE),
            'radius': random.randint(5, 15),
            'speed': random.uniform(0.1, 0.2)
        })

    # Create wind gusts
    wind_gusts = []
    inactive_gusts = []  # Store recently handled gusts for visual feedback
    flash_timer = 0  # Timer for visual feedback effects
    gust_timer = 0
    next_gust_direction = None  # For alternating directions
    
    # Minimum time between gusts (to prevent multiple gusts at once)
    min_gust_spacing = 30  # Minimum frames between gusts
    time_since_last_gust = min_gust_spacing  # Initialize as ready

    # Create moving objects
    moving_objects = []
    for i in range(8):
        moving_objects.append(MovingObject())

    # Result message
    result_message = None
    result_timer = 0
    
    # Stage transition announcement
    stage_announcement = None
    stage_announcement_timer = 0
    
    # Hydra warning system
    hydra_warning_active = False
    hydra_warning_timer = 0
    hydra_warning_text = "!!! HYDRA APPROACHING !!!"
        
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"  # Signal to quit the whole application
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    bar_position = 0  # Top
                elif event.key == pygame.K_RIGHT:
                    bar_position = 1  # Right
                elif event.key == pygame.K_DOWN:
                    bar_position = 2  # Bottom
                elif event.key == pygame.K_LEFT:
                    bar_position = 3  # Left
                elif event.key == pygame.K_ESCAPE:
                    return "menu"  # Return to menu
        
        # If we have a result message, display it and count down
        if result_message:
            result_timer -= 1
            if result_timer <= 0:
                return "menu"  # Return to menu after showing result
                
            # Draw the result message
            screen.fill(BLACK)
            font = pygame.font.SysFont("Courier New", 30)
            text = font.render(result_message, True, GREEN)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            
            # Draw return to menu message
            small_font = pygame.font.SysFont("Courier New", 16)
            return_text = small_font.render("Returning to menu...", True, DARK_GREEN)
            screen.blit(return_text, (WIDTH // 2 - return_text.get_width() // 2, HEIGHT // 2 + 50))
            
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # Update animation values
        glow_value += 0.1 * glow_direction
        if glow_value >= 3.14 or glow_value <= 0:
            glow_direction *= -1
        
        water_offset += 0.02
        boat_offset += 0.08
        
        # Physics update with challenging dynamics
        # Apply drag to acceleration (varies based on current speed)
        speed_factor = 1.0 + (abs(boat_speed) / MAX_SPEED) * 0.5
        boat_acceleration *= (1 - ACCELERATION_DECAY * speed_factor)
        
        # Random acceleration jitter at high speeds (reduced in easier stages)
        if abs(boat_speed) > MAX_SPEED * 0.7:
            jitter_base = (abs(boat_speed) - MAX_SPEED * 0.7) / (MAX_SPEED * 0.3) * 0.1
            # Scale jitter based on difficulty
            jitter_amount = jitter_base * difficulty_factor
            boat_acceleration += random.uniform(-jitter_amount, jitter_amount)
        
        # Apply acceleration to speed with exponential effect at high values
        accel_effect = boat_acceleration
        if abs(boat_acceleration) > 1.0:
            # Exponential effect for high acceleration (harder to control)
            # Scale based on difficulty
            exponent = 1.0 + (difficulty_factor - 1.0) * 0.2  # Ranges from 1.0 to 1.2
            accel_sign = 1 if boat_acceleration > 0 else -1
            accel_effect = accel_sign * (1.0 + (abs(boat_acceleration) - 1.0) ** exponent)
        
        boat_speed += accel_effect
        
        # Apply variable drag to speed based on current speed and difficulty
        drag_effect = DRAG * (1.0 + (abs(boat_speed) / MAX_SPEED)) * difficulty_factor
        if boat_speed > 0:
            boat_speed -= drag_effect
        elif boat_speed < 0:
            boat_speed += drag_effect
            
        # Clamp speed to limits
        boat_speed = max(MIN_SPEED, min(MAX_SPEED, boat_speed))
        
        # Update distance based on speed
        current_distance += boat_speed / 10
        
        # Cap distance at 0 (can't go backwards from start)
        current_distance = max(0, current_distance)
        
        # Check for stage transitions and update difficulty parameters
        # Easy stage (first third)
        if current_distance < EASY_THRESHOLD:
            if current_stage != "EASY":
                current_stage = "EASY"
                stage_announcement = "NAVIGATION: CALM WATERS"
                stage_announcement_timer = 120  # 2 seconds at 60fps
                
            difficulty_factor = 0.8  # Reduced from 1.0
            gust_frequency_modifier = 0.7  # Less frequent gusts (reduced from 0.8)
            gust_pattern_predictability = 0.95  # Very predictable pattern (increased from 0.9)
            warning_time_modifier = 1.8  # 80% longer warning time (increased from 1.5)
            wobble_intensity = 0.2  # Minimal wobble (reduced from 0.3)
            min_gust_spacing = 50  # More spacing between gusts in easy mode (increased from 45)
            
        # Medium stage (second third)
        elif current_distance < MEDIUM_THRESHOLD:
            if current_stage != "MEDIUM":
                current_stage = "MEDIUM"
                stage_announcement = "WARNING: INCREASING TURBULENCE"
                stage_announcement_timer = 120
                
            difficulty_factor = 1.1  # Reduced from 1.3
            gust_frequency_modifier = 0.9  # Normal gust frequency (reduced from 1.0)
            gust_pattern_predictability = 0.7  # Medium predictability (increased from 0.6)
            warning_time_modifier = 1.2  # Longer warning time (increased from 1.0)
            wobble_intensity = 0.5  # Medium wobble (reduced from 0.6)
            min_gust_spacing = 40  # Medium spacing between gusts (increased from 35)
            
        # Hard stage (final third)
        else:
            if current_stage != "HARD":
                current_stage = "HARD"
                stage_announcement = "DANGER: NAVIGATING STORM WATERS"
                stage_announcement_timer = 120
                
            difficulty_factor = 1.4  # Reduced from 1.6
            gust_frequency_modifier = 1.1  # More frequent gusts (reduced from 1.2)
            gust_pattern_predictability = 0.5  # Less predictable (increased from 0.4)
            warning_time_modifier = 0.9  # 10% shorter warning time (increased from 0.8)
            wobble_intensity = 0.8  # High wobble (reduced from 1.0)
            min_gust_spacing = 35  # Reduced but still manageable (increased from 30)
        
        # Update stage announcement timer
        if stage_announcement_timer > 0:
            stage_announcement_timer -= 1
        
        # Check if destination reached
        if current_distance >= TOTAL_DISTANCE:
            result_message = "DESTINATION REACHED!"
            result_timer = 180  # Show for 3 seconds (60 fps)
            continue
            
        # Update hydras and check for collisions
        closest_hydra_distance = float('inf')
        for hydra in hydras[:]:
            # Update the hydra, passing the debug flag
            defeated = hydra.update(boat_speed, difficulty_factor, debug_mode)
            
            # Print debug info every 60 frames (about once per second)
            if debug_mode and debug_frame_counter % 60 == 0:
                print(f"Hydra: pos={hydra.distance:.1f}, boat={current_distance:.1f}, diff={current_distance-hydra.distance:.1f}, speed={hydra.speed:.1f}")
            
            # Remove defeated hydras
            if defeated:
                if debug_mode:
                    print(f"Hydra defeated and removed!")
                hydras.remove(hydra)
                continue
                
            # Calculate distance between boat and hydra
            distance_to_boat = current_distance - hydra.distance
            
            # Keep track of closest hydra
            if distance_to_boat < closest_hydra_distance:
                closest_hydra_distance = distance_to_boat
                
            # Check for collision (hydra caught up with the boat)
            if distance_to_boat < 100:  # Arbitrary small distance for collision
                if debug_mode:
                    print(f"GAME OVER: Hydra caught the boat! Distance: {distance_to_boat:.1f}")
                result_message = "DEVOURED BY HYDRA!"
                result_timer = 180  # Show for 3 seconds (60 fps)
                break
        
        # Update debug counter
        debug_frame_counter = (debug_frame_counter + 1) % 60
        
        # Spawn new hydras at certain intervals if we don't have too many
        if len(hydras) < max_active_hydras and current_distance > next_hydra_spawn:
            spawn_distance = current_distance - random.randint(hydra_spawn_distance_range[0], hydra_spawn_distance_range[1])
            new_hydra = Hydra(spawn_distance)
            hydras.append(new_hydra)
            if debug_mode:
                print(f"New hydra spawned at distance {new_hydra.distance}, boat at {current_distance}, difference: {current_distance - new_hydra.distance}")
            next_hydra_spawn = current_distance + random.randint(10000, 20000)  # Next spawn point
        
        # Show warning if hydras get close
        if closest_hydra_distance < 1000 and not hydra_warning_active:
            hydra_warning_active = True
            hydra_warning_timer = 120  # 2 seconds
        
        # Update hydra warning timer
        if hydra_warning_timer > 0:
            hydra_warning_timer -= 1
            
        # Deactivate warning when timer expires
        if hydra_warning_timer <= 0 and hydra_warning_active:
            hydra_warning_active = False
        
        # Increment time since last gust
        time_since_last_gust += 1
        
        # Generate new wind gusts with increasing randomness based on acceleration
        gust_timer += 1
        
        # More gusts at higher speeds/accelerations, adjusted by stage difficulty
        effective_interval = max(
            GUST_MIN_INTERVAL,
            GUST_INTERVAL_BASE / gust_frequency_modifier - (abs(boat_speed) / 2) - (abs(boat_acceleration) * 20 * difficulty_factor)
        )
        
        # Only generate a new gust if:
        # 1. Enough time has passed since interval
        # 2. Minimum spacing between gusts is respected
        # 3. No gusts are currently in warning phase (to prevent overlapping warnings)
        if gust_timer >= effective_interval and time_since_last_gust >= min_gust_spacing:
            # Check if any existing gusts are in warning phase
            any_warnings_active = any(gust.warning for gust in wind_gusts)
            
            if not any_warnings_active:
                # Determine gust pattern based on acceleration and difficulty
                accel_threshold = MAX_ACCELERATION * 0.6 * gust_pattern_predictability
                
                if abs(boat_acceleration) < accel_threshold:
                    # More predictable pattern at lower acceleration
                    if next_gust_direction is None:
                        next_gust_direction = random.randint(0, 3)
                    else:
                        # Follow pattern with chance of deviation based on difficulty
                        if random.random() < (1 - gust_pattern_predictability):
                            # Random direction when unpredictable
                            next_gust_direction = random.randint(0, 3)
                        else:
                            # Otherwise follow pattern with occasional skips
                            if random.random() < 0.2:  # 20% chance to skip
                                next_gust_direction = (next_gust_direction + 2) % 4
                            else:
                                next_gust_direction = (next_gust_direction + 1) % 4
                else:
                    # Completely random at high acceleration
                    randomness_factor = min(1.0, (abs(boat_acceleration) - accel_threshold) / (MAX_ACCELERATION - accel_threshold))
                    randomness_factor *= (2 - gust_pattern_predictability)  # Scale by difficulty
                    
                    if random.random() < randomness_factor:
                        # Pure random direction
                        next_gust_direction = random.randint(0, 3)
                    else:
                        # Continue pattern but with more chaos
                        next_gust_direction = (next_gust_direction + random.choice([1, 2, 3])) % 4
                        
                # Create wind gust with parameters adjusted by current stage
                new_gust = WindGust(next_gust_direction, boat_acceleration * wobble_intensity, difficulty_factor)
                
                # Adjust warning time based on stage difficulty
                new_gust.warning_time = int(new_gust.warning_time * warning_time_modifier)
                
                wind_gusts.append(new_gust)
                
                # Reset timers
                gust_timer = 0
                time_since_last_gust = 0
        
        # Update wind gusts
        for gust in wind_gusts[:]:
            accel_change = gust.update(bar_position, boat_speed)
            boat_acceleration += accel_change
            
            # Clamp acceleration to limits
            boat_acceleration = max(-MAX_ACCELERATION, min(MAX_ACCELERATION, boat_acceleration))
            
            # Check if this gust was just handled (collected, blocked, or missed)
            if not gust.active and (gust.collected or gust.blocked or gust.missed):
                # Add to inactive gusts for visual feedback
                inactive_gusts.append(gust)
                # Reset flash timer for visual feedback
                flash_timer = 15
                # Remove from active gusts list
                wind_gusts.remove(gust)
            elif not gust.active:
                wind_gusts.remove(gust)
        
        # Update visual feedback timer and clean up old inactive gusts
        if flash_timer > 0:
            flash_timer -= 1
        
        # Clean up old inactive gusts when feedback is complete
        if flash_timer == 0 and inactive_gusts:
            inactive_gusts = []
        
        # Update moving objects to simulate boat movement
        for obj in moving_objects:
            obj.update(boat_speed)
        
        # Fill the screen
        screen.fill(BLACK)
        
        # Draw terminal border
        draw_terminal_border(screen, boat_speed, boat_acceleration, glow_value)
        
        # Draw water
        draw_water(screen, ripples, water_offset)
        
        # Draw moving objects
        for obj in moving_objects:
            obj.draw(screen)
        
        # Draw the outer square border
        pygame.draw.rect(screen, DARK_GREEN, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], OUTER_SQUARE_SIZE, OUTER_SQUARE_SIZE), 1)
        
        # Draw the inner square border (primary play area)
        pygame.draw.rect(screen, GREEN, (SQUARE_POS[0], SQUARE_POS[1], SQUARE_SIZE, SQUARE_SIZE), 1)
        
        # Draw wind gusts
        for gust in wind_gusts:
            gust.draw(screen)
        
        # Draw visual feedback for collected, blocked, or missed gusts
        if inactive_gusts and flash_timer > 0:
            draw_gust_feedback(screen, inactive_gusts, flash_timer)
        
        # Draw the bar
        draw_bar(screen, bar_position, glow_value)
        
        # Draw the boat
        draw_boat(screen, boat_offset)
        
        # Draw meters (speed and progress) and get progress bar rect
        progress_rect = draw_meters(screen, boat_speed, boat_acceleration, current_distance, glow_value)
        
        # Draw hydras (they'll add themselves to the progress bar)
        if debug_mode and debug_frame_counter % 60 == 0:
            print(f"Drawing {len(hydras)} hydras. Progress rect: {progress_rect}")
            
        for hydra in hydras:
            hydra.draw(screen, current_distance, TOTAL_DISTANCE, progress_rect, debug_mode)
        
        # Display bar position
        draw_status_line(screen, bar_position)
        
        # Draw stage announcement if active
        if stage_announcement and stage_announcement_timer > 0:
            # Draw with fading effect
            alpha = min(255, stage_announcement_timer * 4)
            font = pygame.font.SysFont("Courier New", 24)
            announcement_surf = font.render(stage_announcement, True, 
                                            YELLOW if current_stage == "MEDIUM" else
                                            RED if current_stage == "HARD" else
                                            GREEN)
            
            # Create a temporary surface with alpha for fading
            temp_surf = pygame.Surface((announcement_surf.get_width(), announcement_surf.get_height()))
            temp_surf.fill(BLACK)
            temp_surf.set_alpha(255 - alpha)
            
            # Draw the announcement centered on screen
            screen.blit(announcement_surf, 
                        (WIDTH // 2 - announcement_surf.get_width() // 2, 
                         HEIGHT // 3 - announcement_surf.get_height() // 2))
            
            # Apply fading effect
            screen.blit(temp_surf, 
                        (WIDTH // 2 - announcement_surf.get_width() // 2, 
                         HEIGHT // 3 - announcement_surf.get_height() // 2))
        
        # Draw hydra warning if active
        if hydra_warning_active:
            # Flashing effect
            if (hydra_warning_timer // 5) % 2 == 0:  # Flash more frequently (every 5 frames)
                font = pygame.font.SysFont("Courier New", 26)  # Larger font
                warning_surf = font.render(hydra_warning_text, True, RED)
                
                # Draw warning text at top of screen with background
                # Draw background
                warning_bg = pygame.Surface((warning_surf.get_width() + 20, warning_surf.get_height() + 10))
                warning_bg.fill(BLACK)
                warning_bg.set_alpha(200)  # Semi-transparent
                screen.blit(warning_bg, (
                    WIDTH // 2 - (warning_surf.get_width() + 20) // 2,
                    BORDER_MARGIN + 35
                ))
                
                # Draw text
                screen.blit(warning_surf, (
                    WIDTH // 2 - warning_surf.get_width() // 2,
                    BORDER_MARGIN + 40
                ))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    return "menu"  # Default return to menu if loop exits

def main():
    """Main function to run the game"""
    current_state = "menu"
    
    # Main loop
    while True:
        if current_state == "menu":
            # Handle menu screen
            menu_running = True
            while menu_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            current_state = "game"
                            menu_running = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                
                # Draw menu
                draw_menu()
                pygame.display.flip()
                clock.tick(60)
                
        elif current_state == "game":
            # Run the game
            result = run_game()
            
            if result == "quit":
                pygame.quit()
                sys.exit()
            else:
                current_state = "menu"  # Return to menu

if __name__ == "__main__":
    main()
