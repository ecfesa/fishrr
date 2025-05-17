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
    " !@#$%^&*()_+-=[]{};':\\\",./<>?|~`" + # Corrected: Ensure this is a valid string literal for the single quote
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
    g.CLOCK = clock # Store clock globally for Hydra game
    running = True # Renamed run to running to avoid conflict with run function name
    
    clickable_areas_manual = [] # To store clickable areas from manual draw

    while running:
        # Get events once for the frame
        current_events = pygame.event.get()

        for event in current_events:
            if event.type == pygame.QUIT:
                running = False
                # If Hydra game is running, tell it to quit too
                if g.GAME_STATE == g.GAME_STATE_HYDRA and g.HYDRA_GAME_INSTANCE:
                    g.HYDRA_GAME_INSTANCE.is_running = False 
                break # Exit event loop for this frame if QUIT
        
        if not running: # If QUIT event was processed
            break

        # State-specific event handling
        if g.GAME_STATE == g.GAME_STATE_MANUAL:
            if g.MANUAL_VIEW_INSTANCE:
                # Pass all current_events to manual handler
                # The manual.handle_manual_events needs to be adapted or we process one by one here
                # For now, assuming handle_manual_events processes a single event from the loop
                for event in current_events: # Iterate again for this specific handler
                    if event.type == pygame.QUIT: continue # Already handled
                    keep_manual_open = manual.handle_manual_events(event, g.MANUAL_VIEW_INSTANCE, pygame.mouse.get_pos()) # mouse_pos might need to be updated if loop changes
                    if not keep_manual_open:
                        g.GAME_STATE = g.GAME_STATE_TERMINAL
                        break # Stop processing more events for manual if it's closed
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Clickable areas should be up-to-date from previous frame's draw
                        for rect, action in clickable_areas_manual: 
                            if rect.collidepoint(event.pos):
                                if action != "scroll_up" and action != "scroll_down":
                                    g.MANUAL_VIEW_INSTANCE.toggle_command(action)
                                break 
            
        elif g.GAME_STATE == g.GAME_STATE_TERMINAL:
            for event in current_events: # Iterate again for this specific handler
                if event.type == pygame.QUIT: continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False 
                        break
                    else:
                        process_input(event)
            if not running: break

        elif g.GAME_STATE == g.GAME_STATE_HYDRA:
            if g.HYDRA_GAME_INSTANCE:
                # Pass all current events to Hydra game's run method
                if not g.HYDRA_GAME_INSTANCE.run(current_events):
                    # Hydra game is over (returned False) or requested quit
                    g.GAME_STATE = g.GAME_STATE_TERMINAL # Switch back to terminal
                    # Optionally, clean up Hydra instance or leave it for re-entry
                    # g.HYDRA_GAME_INSTANCE = None # To reinitialize next time
                    # For now, we assume re-entering will reset it via flee command logic
            else:
                # Should not happen if flee command initializes it properly
                print("Error: Hydra game instance not found while in Hydra state.")
                g.GAME_STATE = g.GAME_STATE_TERMINAL # Fallback

        # Drawing logic based on game state
        # Clear screen once before any drawing for the current state
        if g.GAME_STATE != g.GAME_STATE_HYDRA: # Only fill if not in Hydra game
            g.WIN.fill(assets.BACKGROUND_COLOR if hasattr(assets, 'BACKGROUND_COLOR') else g.BLACK)

        if g.GAME_STATE == g.GAME_STATE_MANUAL:
            if g.MANUAL_VIEW_INSTANCE:
                mouse_pos = pygame.mouse.get_pos() # Get fresh mouse pos for drawing
                clickable_areas_manual = manual.draw_manual_view(g.WIN, g.MANUAL_VIEW_INSTANCE, mouse_pos)
        elif g.GAME_STATE == g.GAME_STATE_TERMINAL:
            draw_window() # Draw the terminal window
        elif g.GAME_STATE == g.GAME_STATE_HYDRA:
            # Hydra game's run method (which calls its own draw methods that fill the screen)
            # has already been called. The main loop's flip will show it.
            pass 

        pygame.display.flip()
        clock.tick(g.FPS) # Tick the main game clock

    pygame.quit()

if __name__ == "__main__":
    run()