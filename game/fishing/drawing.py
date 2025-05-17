import pygame
from .settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, 
    BLACK, WHITE, GREEN, RED, BLUE, DARK_BLUE, GRAY, 
    font, small_font, tutorial_font,
    CAST_PERFECTION_ZONES # Import the new zones
)
from .items import FishableType # For draw_result_screen
from .assets import *

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

def draw_idle_screen(surface):
    
    surface.fill(BLACK)
    
    # Check if PLAYER_IDLE_SPRITE is loaded (imported from assets)
    if 'PLAYER_IDLE_SPRITE' in globals() and PLAYER_IDLE_SPRITE:
        # Position player sprite (example: bottom center)
        player_rect = PLAYER_IDLE_SPRITE.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_IDLE_SPRITE.get_height() // 2 - 20))
        surface.blit(PLAYER_IDLE_SPRITE, player_rect)
    
    draw_text("Fishrr", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4) 
    draw_text("Press and hold SPACE to start fishing", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) 
    draw_text("Press T for Tutorial", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50) 

def draw_tutorial_screen(surface):
    surface.fill(DARK_BLUE) 
    draw_text("Tutorial", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8) 

    tutorial_text = [
        "Welcome to Fishrr!",
        "",
        "1. Press SPACE to start casting your line.",
        "2. Watch the CASTING METER. Release SPACE for a stronger cast.",
        "3. WAIT for a fish to bite. You'll get a notification!",
        "4. When a fish bites, a QUICK TIME EVENT (QTE) might appear. Press SPACE!", 
        "5. Then, the FISHING BATTLE begins!",
        "   Hold SPACE to raise your bar. Release to let it fall.", 
        "   Keep the fish icon inside your bar.",
        "   Fill the progress bar to catch the fish!",
        "6. See your RESULT - did you catch it or did it get away?",
        "",
        "Press ESC to return to the main menu."
    ]

    text_box_rect = pygame.Rect(SCREEN_WIDTH // 8, SCREEN_HEIGHT // 4, SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT * 5 // 8)
    pygame.draw.rect(surface, GRAY, text_box_rect) 
    pygame.draw.rect(surface, WHITE, text_box_rect, 3) 

    line_height = 25 
    for i, line in enumerate(tutorial_text):
        draw_text(line, tutorial_font, BLACK, surface, text_box_rect.x + 20, text_box_rect.y + 20 + i * line_height, center=False) 

def draw_casting_screen(surface, cast_power):
    
    surface.fill(BLACK) 
    
    # Check if CASTING_SPRITE is loaded (imported from assets)
    if 'CASTING_SPRITE' in globals() and CASTING_SPRITE:
        # Position player casting sprite (example: bottom center)
        # Corrected variable name from PLAYER_CASTING_SPRITE to CASTING_SPRITE
        player_rect = CASTING_SPRITE.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - CASTING_SPRITE.get_height() // 2 - 20))
        surface.blit(CASTING_SPRITE, player_rect)
    else: # Fallback text if player sprite not loaded
        draw_text("Player Casting", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

    draw_text("Casting!", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4) 

    meter_width = 300
    meter_height = 30
    meter_x = (SCREEN_WIDTH - meter_width) // 2
    meter_y = SCREEN_HEIGHT // 2
    
    # Draw base meter background
    pygame.draw.rect(surface, GRAY, (meter_x, meter_y, meter_width, meter_height))

    # Draw perfection zones first, so power bar draws over them
    for zone in CAST_PERFECTION_ZONES:
        zone_x_start = meter_x + int(meter_width * (zone["min"] / 100.0))
        zone_x_end = meter_x + int(meter_width * (zone["max"] / 100.0))
        zone_width = zone_x_end - zone_x_start
        pygame.draw.rect(surface, zone["color"], (zone_x_start, meter_y, zone_width, meter_height))

    # Draw the power bar itself
    power_width = int(meter_width * (cast_power / 100.0))
    pygame.draw.rect(surface, GREEN, (meter_x, meter_y, power_width, meter_height))
    
    # Draw outline for the main meter
    pygame.draw.rect(surface, BLACK, (meter_x, meter_y, meter_width, meter_height), 3)

    # Draw dividing lines for perfection zones for clarity (optional, but good for visual)
    for zone in CAST_PERFECTION_ZONES:
        # Line at the start of the zone (if not 0)
        if zone["min"] > 0:
            line_x_start = meter_x + int(meter_width * (zone["min"] / 100.0))
            pygame.draw.line(surface, zone.get("line_color", BLACK), (line_x_start, meter_y), (line_x_start, meter_y + meter_height), 1)
        # Line at the end of the zone (if not 100)
        if zone["max"] < 100:
            line_x_end = meter_x + int(meter_width * (zone["max"] / 100.0))
            pygame.draw.line(surface, zone.get("line_color", BLACK), (line_x_end, meter_y), (line_x_end, meter_y + meter_height), 1)

    draw_text(f"Power: {int(cast_power)}%", small_font, WHITE, surface, SCREEN_WIDTH // 2, meter_y + meter_height + 30) 
    draw_text("Release SPACE to cast", small_font, WHITE, surface, SCREEN_WIDTH // 2, meter_y + meter_height + 70) 

def draw_waiting_screen_content(surface, time_waited):
    draw_text("Waiting for a bite...", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) 
    draw_text(f"Time: {time_waited:.1f}s", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)     

def draw_qte_screen(surface, qte_key_display, qte_timer_display):
    surface.fill(BLACK)
    draw_text("QUICK!", font, RED, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3) 
    draw_text(f"Press: {qte_key_display.upper()}", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) 
    
    timer_bar_width = SCREEN_WIDTH * 0.8
    timer_bar_height = 20
    timer_bar_x = (SCREEN_WIDTH - timer_bar_width) // 2
    timer_bar_y = SCREEN_HEIGHT * 0.7
    
    pygame.draw.rect(surface, GRAY, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height))
    current_time_width = int(timer_bar_width * qte_timer_display)
    pygame.draw.rect(surface, RED, (timer_bar_x, timer_bar_y, current_time_width, timer_bar_height))
    pygame.draw.rect(surface, BLACK, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height), 2)

def draw_battle_screen(surface, fish_pos_y, player_bar_pos_y, catch_progress, target_fish_name):
    
    surface.fill(BLACK) # Fallback to solid color
    
    draw_text(f"Fighting: {target_fish_name}!", small_font, WHITE, surface, SCREEN_WIDTH // 2, 50)

    battle_area_height = SCREEN_HEIGHT * 0.6
    battle_area_width = 60 
    battle_area_x = SCREEN_WIDTH // 2 - battle_area_width // 2
    battle_area_y = SCREEN_HEIGHT * 0.2

    pygame.draw.rect(surface, GRAY, (battle_area_x, battle_area_y, battle_area_width, battle_area_height)) # Changed Light Blue to Gray for better contrast
    pygame.draw.rect(surface, BLACK, (battle_area_x, battle_area_y, battle_area_width, battle_area_height), 2)
    
    player_bar_height = 80 
    player_bar_rect = pygame.Rect(battle_area_x, battle_area_y + player_bar_pos_y, battle_area_width, player_bar_height)
    pygame.draw.rect(surface, GREEN, player_bar_rect)
    pygame.draw.rect(surface, BLACK, player_bar_rect, 1)

    # Fish icon (moves within the battle_area_height)
    fish_icon_size = 30 # This might be determined by the loaded sprite's dimensions
    fish_rect = pygame.Rect(battle_area_x + (battle_area_width - fish_icon_size) // 2, battle_area_y + fish_pos_y, fish_icon_size, fish_icon_size)
    
    # Check if FISH_ICON_PLACEHOLDER is loaded
    if 'FISH_ICON_PLACEHOLDER' in globals() and FISH_ICON_PLACEHOLDER: 
        surface.blit(FISH_ICON_PLACEHOLDER, fish_rect.topleft)
    else:     
        pygame.draw.ellipse(surface, RED, fish_rect) 
    pygame.draw.rect(surface, BLACK, fish_rect, 1)

    progress_bar_width = 30
    progress_bar_height = battle_area_height
    progress_bar_x = battle_area_x + battle_area_width + 20
    progress_bar_y = battle_area_y

    pygame.draw.rect(surface, GRAY, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
    current_progress_height = int(progress_bar_height * catch_progress)
    pygame.draw.rect(surface, GREEN, (progress_bar_x, progress_bar_y + (progress_bar_height - current_progress_height), progress_bar_width, current_progress_height))
    pygame.draw.rect(surface, BLACK, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 2)

    draw_text("Hold SPACE to raise bar!", tutorial_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40) 

def draw_result_screen(surface, caught_fish, success):
    
    surface.fill(BLACK) 
    
    icon_to_draw = None
    item_name_for_icon = ""

    # Check if sprites are loaded before trying to use them
    fish_icon_loaded = 'FISH_ICON_PLACEHOLDER' in globals() and FISH_ICON_PLACEHOLDER
    trash_icon_loaded = 'TRASH_ICON_PLACEHOLDER' in globals() and TRASH_ICON_PLACEHOLDER

    if caught_fish:
        item_name_for_icon = caught_fish.name
        if caught_fish.type == FishableType.FISH and fish_icon_loaded:
            icon_to_draw = FISH_ICON_PLACEHOLDER 
        elif caught_fish.type == FishableType.TRASH and trash_icon_loaded:
            icon_to_draw = TRASH_ICON_PLACEHOLDER
        
    if icon_to_draw:
        icon_rect = icon_to_draw.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
        surface.blit(icon_to_draw, icon_rect)

    if success:
        if caught_fish:
            if caught_fish.type == FishableType.FISH:
                # Display fish details on multiple lines
                draw_text(f"Caught a {caught_fish.name}!", font, GREEN, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
                draw_text(f"Species: {caught_fish.species}", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
                draw_text(f"Weight: {caught_fish.weight:.2f}kg", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
                draw_text(f"Difficulty: {caught_fish.difficulty.value.capitalize()}", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            elif caught_fish.type == FishableType.TRASH:
                # Display trash details (usually shorter, but can also be structured)
                draw_text(f"Reeled in: {caught_fish.name}", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
                draw_text(f"(It's trash)", small_font, GRAY, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10) # Using GRAY for subheading
                draw_text(f"Weight: {caught_fish.weight:.2f}kg", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        else: 
            draw_text("You caught something!", font, GREEN, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    else:
        if caught_fish and caught_fish.type == FishableType.FISH:
            draw_text("The fish got away!", font, RED, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3) 
            draw_text(f"It was a {caught_fish.name}... so close!", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        elif caught_fish and caught_fish.type == FishableType.TRASH: 
             # This case should ideally not be reached if trash is auto-caught.
             draw_text("The trash got away? Curious.", font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3) 
             draw_text(f"It was just a {caught_fish.name}.", small_font, GRAY, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else: 
            draw_text("Nothing hooked...", font, RED, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3) 

    draw_text("Press SPACE to fish again", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.75) 
    draw_text("Press ESC for Main Menu", small_font, WHITE, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.75 + 40) 
