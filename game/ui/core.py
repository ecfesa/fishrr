import pygame

from game.ui.draw_window import draw_window
import game.assets as assets
import game.globals as g
import string
import game.manual as manual # Import manual module

pygame.init()
pygame.display.set_caption("fishrr")

# Whitelist for allowed input characters
ALLOWED_CHARS = frozenset(
    string.ascii_lowercase +
    string.ascii_uppercase +
    string.digits +
    " !@#$%^&*()_+-=[]{};':\",./<>?|~`" + # Common special characters
    "\r"  # Enter key
    "\b"  # Backspace key
)

def process_input(event: pygame.event.Event):
    if event.key == pygame.K_l and (
        event.mod & pygame.KMOD_CTRL or
        event.mod & pygame.KMOD_LCTRL or
        event.mod & pygame.KMOD_RCTRL
    ):
        g.SYSTEM.clear()
    else:
        if event.unicode == "" or event.unicode not in ALLOWED_CHARS:
            return
        assets.KEYBOARD_SOUND.play()
        g.SYSTEM.process_input(event.unicode)

def run():
    clock = pygame.time.Clock()
    running = True # Renamed run to running to avoid conflict with run function name
    
    clickable_areas_manual = [] # To store clickable areas from manual draw

    while running:
        clock.tick(g.FPS)
        mouse_pos = pygame.mouse.get_pos() # Get mouse position once per frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if g.GAME_STATE == g.GAME_STATE_MANUAL:
                if g.MANUAL_VIEW_INSTANCE:
                    keep_manual_open = manual.handle_manual_events(event, g.MANUAL_VIEW_INSTANCE, mouse_pos)
                    if not keep_manual_open: # e.g. ESC pressed in manual
                        g.GAME_STATE = g.GAME_STATE_TERMINAL
                    
                    # Handle manual-specific clicks (command toggling)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for rect, action in clickable_areas_manual: # Use stored clickable areas
                            if rect.collidepoint(event.pos):
                                if action != "scroll_up" and action != "scroll_down": # Already handled by handle_manual_events
                                    g.MANUAL_VIEW_INSTANCE.toggle_command(action)
                                break 
            
            elif g.GAME_STATE == g.GAME_STATE_TERMINAL:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # ESC in terminal quits game
                        running = False 
                    else:
                        process_input(event) # Process terminal input
        
        # This was inside KEYDOWN before, moved out for general ESC handling if not in terminal
        # keys_pressed = pygame.key.get_pressed()
        # if keys_pressed[pygame.K_ESCAPE]:
        #     if g.GAME_STATE == g.GAME_STATE_TERMINAL:
        #         running = False
        #     # If in manual, ESC is handled by handle_manual_events to switch state

        # Drawing logic based on game state
        g.WIN.fill(assets.BACKGROUND_COLOR if hasattr(assets, 'BACKGROUND_COLOR') else g.BLACK) # Clear screen

        if g.GAME_STATE == g.GAME_STATE_MANUAL:
            if g.MANUAL_VIEW_INSTANCE:
                clickable_areas_manual = manual.draw_manual_view(g.WIN, g.MANUAL_VIEW_INSTANCE, mouse_pos)
        elif g.GAME_STATE == g.GAME_STATE_TERMINAL:
            draw_window() # Draw the terminal window

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run()