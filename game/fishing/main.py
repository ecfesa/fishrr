import pygame
import sys
import random
# from enum import Enum # GameState is in settings, Fish Enums are in items

from .settings import (
    # screen, # Screen is now created in run_fishing_game
    SCREEN_WIDTH, SCREEN_HEIGHT, 
    GameState, 
    font, small_font, tutorial_font, # For direct use if any, though mostly used in drawing
    WHITE, BLACK, GREEN, RED, BLUE, DARK_BLUE, GRAY, # Colors might be needed for some logic bits not in drawing
    CAST_PERFECTION_ZONES # For determining cast quality
)
from .items import (
    Fish, TrashItem, FishableType, FishDifficulty, 
    AVAILABLE_FISH, AVAILABLE_TRASH
)
from .drawing import (
    draw_idle_screen, draw_tutorial_screen, draw_casting_screen, 
    draw_waiting_screen_content, draw_qte_screen, draw_battle_screen, draw_result_screen,
    draw_text # If needed directly in main, though unlikely now
)
from .minigames import FishingMinigame # Import the new class
from .assets import load_all_assets, LONG_BAIT_SPRITE # Import the asset loader

# Initialize Pygame (moved to settings.py or run_fishing_game)
# pygame.init()

# Screen dimensions (moved to settings.py)
# Fonts (moved to settings.py)
# Colors (moved to settings.py)
# Game States (moved to settings.py)
# Fish and Trash Definitions (moved to items.py)
# Drawing Functions for Each Stage (moved to drawing.py)

# Load assets once at the beginning
# load_all_assets() # Moved to run_fishing_game

def run_fishing_game():
    pygame.init()
    
    # Screen setup needs to happen after pygame.init()
    # We can re-use the screen object from settings if it's set up there after init,
    # or create it here. For now, assuming settings.py's screen is valid.
    # If settings.py doesn't call pygame.display.set_mode(), it must be done here.
    # For safety, let's ensure the screen is set up. The screen variable from settings
    # might be None before pygame.init() and pygame.display.set_mode() are called.
    # It's better if settings.py provides the dimensions, and main.py sets the mode.
    
    # Re-import screen from settings, as it might be initialized there
    # or we define it here.
    # from settings import screen # This might cause issues if settings.py also runs pygame.init()
    # Let's explicitly set up the screen here to avoid conflicts
    screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fishrr - Fishing Minigame")

    load_all_assets() # Load assets each time the game starts

    # --- Main Game Loop ---
    current_state = GameState.IDLE
    running = True
    clock = pygame.time.Clock()

    # Casting variables
    cast_power = 0
    casting_speed = 1.5
    casting_direction = 1 
    is_casting_meter_active = False

    # Waiting variables
    wait_timer_start = 0
    time_to_wait_for_bite = 0 
    fish_is_biting = False
    cast_quality_feedback = None # To store feedback like "Perfect!"
    cast_quality_feedback_timer = 0 # Timer for how long to show feedback
    CAST_QUALITY_FEEDBACK_DURATION = 2.0 # Show for 2 seconds

    # Bite reaction timer (when fish_is_biting is True)
    bite_reaction_timer_max = 1.75 # Seconds player has to react
    bite_reaction_timer_current = 0
    bite_timer_active = False # True when the reaction timer is running

    # QTE variables
    qte_active = False
    qte_key = None
    qte_key_display = ""
    qte_timer_max = 2.0 
    qte_timer_current = 0
    qte_success = False

    # Battle variables
    fish_y = 0
    player_bar_y = (SCREEN_HEIGHT * 0.6 - 80) / 2 
    player_bar_lift_speed = 300  
    player_bar_gravity = 200  

    fish_movement_speed = 3 
    fish_movement_direction = 1
    fish_target_y = 0 
    fish_move_timer = 0 
    fish_behavior_change_interval = 1.0 

    catch_progress = 0.0
    catch_rate = 10.0 
    penalty_rate = 0.02 
    current_caught_item = None 

    # Result screen
    last_caught_item = None
    last_catch_success = False
    player_inventory = [] # Initialize player inventory


    def start_new_fishing_attempt():
        nonlocal current_state, cast_power, casting_direction, is_casting_meter_active
        nonlocal wait_timer_start, time_to_wait_for_bite, fish_is_biting
        nonlocal qte_active, qte_key, qte_timer_current, qte_success
        nonlocal fish_y, player_bar_y, catch_progress, current_caught_item
        nonlocal cast_quality_feedback, cast_quality_feedback_timer, bite_timer_active, bite_reaction_timer_current # Reset feedback and bite timer vars
        
        cast_power = 0
        casting_direction = 1
        is_casting_meter_active = False 
        
        wait_timer_start = 0
        fish_is_biting = False
        cast_quality_feedback = None # Reset on new attempt
        cast_quality_feedback_timer = 0 # Reset feedback timer
        
        qte_active = False
        qte_key = None
        qte_timer_current = 0
        qte_success = False
        
        fish_y = (SCREEN_HEIGHT * 0.6 - 30) / 2 
        player_bar_y = (SCREEN_HEIGHT * 0.6 - 80) / 2 
        catch_progress = 0.0
        current_caught_item = None
        
        bite_timer_active = False
        bite_reaction_timer_current = 0
        
        current_state = GameState.IDLE


    while running:
        dt = clock.tick(60) / 1000.0 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if current_state == GameState.IDLE:
                    if event.key == pygame.K_SPACE:
                        is_casting_meter_active = True
                        cast_power = 0
                        casting_direction = 1
                        current_state = GameState.CASTING
                    elif event.key == pygame.K_t:
                        current_state = GameState.TUTORIAL
                    elif event.key == pygame.K_ESCAPE: # Allow ESC from IDLE to quit
                        running = False
                elif current_state == GameState.TUTORIAL:
                    if event.key == pygame.K_ESCAPE:
                        current_state = GameState.IDLE
                
                elif current_state == GameState.CASTING:
                    if event.key == pygame.K_SPACE and is_casting_meter_active:
                        is_casting_meter_active = False
                        current_state = GameState.WAITING
                        wait_timer_start = pygame.time.get_ticks()
                        
                        # Determine cast quality
                        cast_quality_feedback = ""
                        final_cast_power = int(cast_power) # Use the power at the moment of release
                        for zone in CAST_PERFECTION_ZONES:
                            if zone["min"] <= final_cast_power <= zone["max"]:
                                cast_quality_feedback = zone["label"]
                                break # Found the zone
                        if not cast_quality_feedback and final_cast_power > 0:
                            cast_quality_feedback = "Cast Away!" # Default for non-special zones
                        elif final_cast_power == 0:
                            cast_quality_feedback = "Oops! Try again."

                        if cast_quality_feedback: # If any feedback was set
                            cast_quality_feedback_timer = CAST_QUALITY_FEEDBACK_DURATION

                        base_wait = 1 + (100 - final_cast_power) / 100.0 * 7 
                        time_to_wait_for_bite = random.uniform(base_wait * 0.7, base_wait * 1.3)
                        fish_is_biting = False

                elif current_state == GameState.WAITING:
                    if fish_is_biting and event.key == pygame.K_SPACE: # Player reacts to bite
                        if bite_timer_active: # Check if reacting within the active bite window
                            bite_timer_active = False # Player reacted
                            fish_is_biting = False # Visual cue ends
                            # current_caught_item was already determined when bite_timer_active was set
                            last_caught_item = current_caught_item 
                            cast_quality_feedback = None # Clear feedback after successful reaction or attempt end
                            cast_quality_feedback_timer = 0 # Ensure timer is also zeroed
                            # current_state = GameState.RESULT # Logic for RESULT is handled below

                            if isinstance(current_caught_item, TrashItem):
                                last_catch_success = True 
                                if last_caught_item: 
                                    player_inventory.append(last_caught_item)
                                current_state = GameState.RESULT
                            elif isinstance(current_caught_item, Fish): 
                                # Pass the screen_surface to the minigame
                                minigame = FishingMinigame(current_caught_item, screen_surface) 
                                minigame_won = minigame.start() 
                                last_catch_success = minigame_won
                                if minigame_won and last_caught_item: 
                                    player_inventory.append(last_caught_item)
                                current_state = GameState.RESULT
                            else:
                                last_catch_success = False
                                current_state = GameState.RESULT
                
                elif current_state == GameState.QTE: # This state is now managed by FishingMinigame
                    pass # QTE logic is inside FishingMinigame.start() which includes its own event loop
                
                elif current_state == GameState.BATTLE: # This state is now managed by FishingMinigame
                    pass # Battle logic is inside FishingMinigame.start()

                elif current_state == GameState.RESULT:
                    if event.key == pygame.K_SPACE:
                        start_new_fishing_attempt() 
                    elif event.key == pygame.K_ESCAPE:
                        # Instead of going to IDLE, quit the fishing minigame
                        running = False 

            if event.type == pygame.KEYUP:
                if current_state == GameState.CASTING:
                    if event.key == pygame.K_SPACE and is_casting_meter_active: # This logic might be redundant if SPACE down already handles it
                        is_casting_meter_active = False
                        current_state = GameState.WAITING
                        wait_timer_start = pygame.time.get_ticks()
                        # Determine cast quality (repeated from KEYDOWN, should consolidate or ensure one path)
                        cast_quality_feedback = ""
                        final_cast_power = int(cast_power) 
                        for zone in CAST_PERFECTION_ZONES:
                            if zone["min"] <= final_cast_power <= zone["max"]:
                                cast_quality_feedback = zone["label"]
                                break
                        if not cast_quality_feedback and final_cast_power > 0:
                            cast_quality_feedback = "Cast Away!"
                        elif final_cast_power == 0:
                            cast_quality_feedback = "Oops! Try again."
                        if cast_quality_feedback:
                            cast_quality_feedback_timer = CAST_QUALITY_FEEDBACK_DURATION
                        
                        base_wait = 1 + (100 - final_cast_power) / 100.0 * 7 # Use final_cast_power
                        time_to_wait_for_bite = random.uniform(base_wait * 0.7, base_wait * 1.3)
                        fish_is_biting = False

        # --- Game Logic Updates (outside event loop) ---
        # General updates that happen regardless of state (or before state-specific logic)
        if cast_quality_feedback_timer > 0:
            cast_quality_feedback_timer -= dt
            if cast_quality_feedback_timer <= 0:
                cast_quality_feedback = None 
                cast_quality_feedback_timer = 0

        if current_state == GameState.CASTING and is_casting_meter_active:
            cast_power += casting_speed * casting_direction
            if cast_power >= 100:
                cast_power = 100
                casting_direction = -1
            elif cast_power <= 0:
                cast_power = 0
                casting_direction = 1
        
        elif current_state == GameState.WAITING:
            if wait_timer_start > 0 and not fish_is_biting and not bite_timer_active: 
                current_time_waiting = (pygame.time.get_ticks() - wait_timer_start) / 1000.0
                if current_time_waiting >= time_to_wait_for_bite:
                    fish_is_biting = True # Start "FISH ON!" visual
                    bite_timer_active = True
                    bite_reaction_timer_current = bite_reaction_timer_max
                    # Determine the hooked item as soon as fish bites
                    if random.random() < 0.8: 
                        item_lambda = random.choice(AVAILABLE_FISH)
                    else: 
                        item_lambda = random.choice(AVAILABLE_TRASH)
                    current_caught_item = item_lambda()
            
            if bite_timer_active: # If bite reaction window is active
                bite_reaction_timer_current -= dt
                if bite_reaction_timer_current <= 0:
                    # Time ran out for player to react
                    fish_is_biting = False # Stop "FISH ON!" visual
                    bite_timer_active = False
                    last_caught_item = current_caught_item # This was set when bite started
                    last_catch_success = False
                    cast_quality_feedback = None # Clear feedback
                    cast_quality_feedback_timer = 0 # Ensure timer is also zeroed
                    current_state = GameState.RESULT
        
        # QTE and BATTLE logic updates are handled by FishingMinigame if it's active
        # No need for QTE/BATTLE state logic here anymore as FishingMinigame.start() is blocking.

        # --- Drawing ---

        if current_state == GameState.IDLE:
            draw_idle_screen(screen_surface)
        elif current_state == GameState.TUTORIAL:
            draw_tutorial_screen(screen_surface)
        elif current_state == GameState.CASTING:
            draw_casting_screen(screen_surface, cast_power)
        elif current_state == GameState.WAITING:
            screen_surface.fill(BLACK) 

            time_display = (pygame.time.get_ticks() - wait_timer_start) / 1000.0 if wait_timer_start > 0 else 0

            if cast_quality_feedback and cast_quality_feedback_timer > 0:
                feedback_color = WHITE
                for zone in CAST_PERFECTION_ZONES:
                    if zone["label"] == cast_quality_feedback:
                        feedback_color = zone["color"]
                        break
                draw_text(cast_quality_feedback, font, feedback_color, screen_surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2)

            if not fish_is_biting:
                draw_waiting_screen_content(screen_surface, time_display) 
            else: 
                if int(time_display * 10) % 2 == 0: 
                     draw_text("FISH ON!", font, RED, screen_surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20) 
                else:
                     draw_text("FISH ON!", font, (150,0,0), screen_surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20) 
                draw_text("Press SPACE to reel!", font, WHITE, screen_surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
                
                if bite_timer_active:
                    bar_width = SCREEN_WIDTH * 0.6
                    bar_height = 15
                    bar_x = (SCREEN_WIDTH - bar_width) // 2
                    bar_y = SCREEN_HEIGHT // 2 + 80 
                    
                    ratio = bite_reaction_timer_current / bite_reaction_timer_max
                    current_bar_width = int(bar_width * ratio)
                    
                    pygame.draw.rect(screen_surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
                    pygame.draw.rect(screen_surface, RED, (bar_x, bar_y, current_bar_width, bar_height))
                    pygame.draw.rect(screen_surface, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

        # QTE and BATTLE drawing is handled by FishingMinigame class loop
        # The FishingMinigame.start() method handles its own drawing loop.

        elif current_state == GameState.RESULT:
            draw_result_screen(screen_surface, last_caught_item, last_catch_success)

        pygame.display.flip()

    # pygame.quit() # Removed this line
    # sys.exit() # Do not exit the whole application

# If you want to run this file directly for testing:
if __name__ == '__main__':
    run_fishing_game()
    sys.exit() # Exit after the game if run directly 