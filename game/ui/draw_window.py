import pygame
import game.assets as assets
import game.globals as g

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
    g.WIN.fill(g.BLACK)
    draw_logo()
    draw_terminal() # Call the function to draw the terminal

    pygame.display.update()