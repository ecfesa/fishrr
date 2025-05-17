import pygame
import game.assets as assets
import game.globals as g
from game.state import GAME_STATE_INSTANCE

# Animation state for the bulb
_is_bulb_animating = False
_bulb_animation_alpha = 255 # Current alpha value for the animation
BULB_FADE_RATE = 15         # How much alpha decreases per frame (higher is faster fade)
_bulb_animation_start_time = None # Timestamp for when the animation should start after delay
_bulb_animation_pending = False   # True if a flash is requested and delay is active
BULB_ANIMATION_DELAY = 500     # Delay in milliseconds (1 second)

def draw_logo():
    g.WIN.blit(assets.LOGO_TRANSPARENT_64PX, (g.WIN.get_width() - (64+g.PADDING), g.PADDING))

def draw_terminal():
    buffer = g.SYSTEM.get_buffer()
    font = assets.TERMINAL_FONT  # Assuming you have a font in assets
    y_offset = g.PADDING  # Starting Y position for the text
    line_height = font.get_linesize()

    for i, chars in enumerate(buffer):
        line = "".join(chars)
        text_surface = font.render(line, True, g.WHITE)  # Assuming g.WHITE is defined
        g.WIN.blit(text_surface, (g.PADDING, y_offset + i * line_height))

def draw_window():
    global _is_bulb_animating, _bulb_animation_alpha, _bulb_animation_start_time, _bulb_animation_pending

    g.WIN.fill(g.BLACK)
    draw_logo()
    draw_terminal() # Call the function to draw the terminal

    # Check if a new bulb flash is requested
    if GAME_STATE_INSTANCE.show_bulb and not _is_bulb_animating and not _bulb_animation_pending:
        _bulb_animation_pending = True
        _bulb_animation_start_time = pygame.time.get_ticks() + BULB_ANIMATION_DELAY
        GAME_STATE_INSTANCE.show_bulb = False # Reset trigger, delay has started

    # Check if a pending animation is ready to start after delay
    if _bulb_animation_pending and pygame.time.get_ticks() >= _bulb_animation_start_time:
        pygame.mixer.Sound.play(assets.NEW_TIP_SOUND)
        _is_bulb_animating = True
        _bulb_animation_alpha = 255  # Pop in: Start at full opacity
        _bulb_animation_pending = False
        _bulb_animation_start_time = None # Clear the start time

    # Handle active bulb animation (drawing and fading)
    if _is_bulb_animating:
        temp_bulb_surface = assets.BULB_IMAGE.copy()
        temp_bulb_surface.set_alpha(_bulb_animation_alpha)
        
        bulb_x = g.WIN.get_width() - (64 + g.PADDING)
        bulb_y = g.WIN.get_height() - 100 - g.PADDING
        g.WIN.blit(temp_bulb_surface, (bulb_x, bulb_y))

        _bulb_animation_alpha -= BULB_FADE_RATE
        if _bulb_animation_alpha < 0:
            _bulb_animation_alpha = 0
            _is_bulb_animating = False

    pygame.display.update()