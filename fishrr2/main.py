import pygame
import sys
import random
# from enum import Enum # GameState is in settings, Fish Enums are in items

from settings import (
    screen, SCREEN_WIDTH, SCREEN_HEIGHT, 
    GameState, 
    font, small_font, tutorial_font, # For direct use if any, though mostly used in drawing
    WHITE, BLACK, GREEN, RED, BLUE, DARK_BLUE, GRAY, # Colors might be needed for some logic bits not in drawing
    CAST_PERFECTION_ZONES # For determining cast quality
)
from items import (
    Fish, TrashItem, FishableType, FishDifficulty, 
    AVAILABLE_FISH, AVAILABLE_TRASH
)
from drawing import (
    draw_idle_screen, draw_tutorial_screen, draw_casting_screen, 
    draw_waiting_screen_content, draw_qte_screen, draw_battle_screen, draw_result_screen,
    draw_text # If needed directly in main, though unlikely now
)
from minigames import FishingMinigame # Import the new class
from assets import load_all_assets, LONG_BAIT_SPRITE # Import the asset loader

# Initialize Pygame (moved to settings.py)
# pygame.init()

# Screen dimensions (moved to settings.py)
# Fonts (moved to settings.py)
# Colors (moved to settings.py)
# Game States (moved to settings.py)
# Fish and Trash Definitions (moved to items.py)
# Drawing Functions for Each Stage (moved to drawing.py)

# Load assets once at the beginning
load_all_assets()

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
    global current_state, cast_power, casting_direction, is_casting_meter_active
    global wait_timer_start, time_to_wait_for_bite, fish_is_biting
    global qte_active, qte_key, qte_timer_current, qte_success
    global fish_y, player_bar_y, catch_progress, current_caught_item
    global cast_quality_feedback, cast_quality_feedback_timer, bite_timer_active, bite_reaction_timer_current # Reset feedback and bite timer vars
    
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
                        current_state = GameState.RESULT

                        if isinstance(current_caught_item, TrashItem):
                            last_catch_success = True 
                            if last_caught_item: 
                                player_inventory.append(last_caught_item)
                            current_state = GameState.RESULT
                        elif isinstance(current_caught_item, Fish): 
                            minigame = FishingMinigame(current_caught_item)
                            minigame_won = minigame.start() 
                            last_catch_success = minigame_won
                            if minigame_won and last_caught_item: 
                                player_inventory.append(last_caught_item)
                            current_state = GameState.RESULT
                        else:
                            last_catch_success = False
                            current_state = GameState.RESULT
            
            elif current_state == GameState.QTE:
                if qte_active:
                    if event.key == qte_key:
                        qte_success = True
                        qte_active = False 
                        
                        if isinstance(current_caught_item, TrashItem): 
                            last_caught_item = current_caught_item
                            last_catch_success = True
                            current_state = GameState.RESULT
                        elif isinstance(current_caught_item, Fish): 
                            if current_caught_item.difficulty == FishDifficulty.EASY: fish_movement_speed = 2
                            elif current_caught_item.difficulty == FishDifficulty.MEDIUM: fish_movement_speed = 4
                            elif current_caught_item.difficulty == FishDifficulty.HARD: fish_movement_speed = 6
                            elif current_caught_item.difficulty == FishDifficulty.LEGENDARY: fish_movement_speed = 8
                            
                            fish_y = (SCREEN_HEIGHT * 0.6 - 30) / 2
                            catch_progress = 0.0
                            current_state = GameState.BATTLE
                        else: 
                            print("Error: Unknown item type after QTE success")
                            start_new_fishing_attempt()

                    else: 
                        qte_success = False
                        qte_active = False
                        last_caught_item = current_caught_item 
                        last_catch_success = False
                        current_state = GameState.RESULT
            
            elif current_state == GameState.BATTLE:
                pass 

            elif current_state == GameState.RESULT:
                if event.key == pygame.K_SPACE:
                    start_new_fishing_attempt() 
                elif event.key == pygame.K_ESCAPE:
                    start_new_fishing_attempt()
                    current_state = GameState.IDLE

        if event.type == pygame.KEYUP:
            if current_state == GameState.CASTING:
                if event.key == pygame.K_SPACE and is_casting_meter_active:
                    is_casting_meter_active = False
                    current_state = GameState.WAITING
                    wait_timer_start = pygame.time.get_ticks()
                    base_wait = 1 + (100 - cast_power) / 100.0 * 7 
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
    
    elif current_state == GameState.QTE and qte_active:
        qte_timer_current -= dt
        if qte_timer_current <= 0:
            qte_active = False
            qte_success = False
            last_caught_item = current_caught_item # Persist the item that was being QTE'd for result screen
            last_catch_success = False
            current_state = GameState.RESULT

    elif current_state == GameState.BATTLE:
        keys = pygame.key.get_pressed()
        battle_area_height = SCREEN_HEIGHT * 0.6
        player_bar_h = 80 

        if keys[pygame.K_SPACE]:
            player_bar_y -= player_bar_lift_speed * dt
        else:
            player_bar_y += player_bar_gravity * dt
        
        player_bar_y = max(0, min(player_bar_y, battle_area_height - player_bar_h))

        fish_move_timer -= dt
        if fish_move_timer <= 0:
            fish_move_timer = fish_behavior_change_interval
            fish_target_y = random.uniform(0, battle_area_height - 30) 
            if fish_y < fish_target_y:
                fish_movement_direction = 1
            else:
                fish_movement_direction = -1
        
        # Trash should not enter battle state due to earlier logic.
        # If it does, it will behave like a very easy fish based on default fish_movement_speed.
        # Consider adding specific handling here if trash *could* enter battle, but ideally it won't.
        
        if fish_movement_speed > 0 : 
            fish_y += fish_movement_speed * fish_movement_direction * dt * 10 
        
        fish_y = max(0, min(fish_y, battle_area_height - 30))

        fish_center_y = fish_y + 15 
        player_bar_top = player_bar_y
        player_bar_bottom = player_bar_y + player_bar_h

        if player_bar_top < fish_center_y < player_bar_bottom:
            catch_progress += catch_rate * dt
        else:
            catch_progress -= penalty_rate * dt
        
        catch_progress = max(0, min(catch_progress, 1.0))

        if catch_progress >= 1.0:
            last_caught_item = current_caught_item
            last_catch_success = True
            current_state = GameState.RESULT
        elif catch_progress <= 0: # No distinction for fish/trash here, if it's in battle and progress is 0, it's lost.
            last_caught_item = current_caught_item 
            last_catch_success = False
            current_state = GameState.RESULT

    # --- Drawing ---

    if current_state == GameState.IDLE:
        # screen.fill(DARK_BLUE) # Now handled in draw_idle_screen
        draw_idle_screen(screen)
    elif current_state == GameState.TUTORIAL:
        # screen.fill(DARK_BLUE) # Tutorial background is part of its draw function
        draw_tutorial_screen(screen)
    elif current_state == GameState.CASTING:
        # screen.fill(DARK_BLUE) # Now handled in draw_casting_screen
        draw_casting_screen(screen, cast_power)
    elif current_state == GameState.WAITING:
        # Background fill and content drawing are now more coordinated for this state
        screen.fill(BLACK) # Keep a base fill here, then layer feedback and content

        time_display = (pygame.time.get_ticks() - wait_timer_start) / 1000.0 if wait_timer_start > 0 else 0

        if cast_quality_feedback and cast_quality_feedback_timer > 0:
            feedback_color = WHITE
            for zone in CAST_PERFECTION_ZONES:
                if zone["label"] == cast_quality_feedback:
                    feedback_color = zone["color"]
                    break
            draw_text(cast_quality_feedback, font, feedback_color, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2)

        if not fish_is_biting:
            draw_waiting_screen_content(screen, time_display) # This draws on top of the DARK_BLUE fill
        else: 
            # "FISH ON!" and timer bar are drawn directly here, also on top of DARK_BLUE fill
            if int(time_display * 10) % 2 == 0: 
                 draw_text("FISH ON!", font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20) 
            else:
                 draw_text("FISH ON!", font, (150,0,0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20) 
            draw_text("Press SPACE to reel!", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            
            if bite_timer_active:
                bar_width = SCREEN_WIDTH * 0.6
                bar_height = 15
                bar_x = (SCREEN_WIDTH - bar_width) // 2
                bar_y = SCREEN_HEIGHT // 2 + 80 
                
                ratio = bite_reaction_timer_current / bite_reaction_timer_max
                current_bar_width = int(bar_width * ratio)
                
                pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, RED, (bar_x, bar_y, current_bar_width, bar_height))
                pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

    # QTE and BATTLE drawing is handled by FishingMinigame class loop
    # The FishingMinigame.run_minigame_loop() handles its own background via draw_qte_screen/draw_battle_screen

    elif current_state == GameState.RESULT:
        # screen.fill(DARK_BLUE) # Now handled in draw_result_screen
        draw_result_screen(screen, last_caught_item, last_catch_success)

    pygame.display.flip()

pygame.quit()
sys.exit() 