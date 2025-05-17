import pygame
import math
from game.hydra.constants import *

def draw_terminal_style_corner(screen, color, x, y, size, is_top=True, is_left=True):
    """Draw a terminal-style corner (L-shape) with given parameters"""
    # Horizontal line
    pygame.draw.line(screen, color, 
                    (x, y), 
                    (x + (size if is_left else -size), y), 2)
    # Vertical line
    pygame.draw.line(screen, color, 
                    (x, y), 
                    (x, y + (size if is_top else -size)), 2)

def draw_glow_color(base_color, glow_value, intensity=100):
    """Calculate a glowing color based on the base color and glow value"""
    if isinstance(base_color, tuple) and len(base_color) >= 3:
        glow_intensity = 155 + int(intensity * math.sin(glow_value))
        # Modify only the components that exist in the base color
        if len(base_color) == 3:
            return (
                min(255, base_color[0] + (glow_intensity if base_color[0] > 0 else 0)), 
                min(255, base_color[1] + (glow_intensity if base_color[1] > 0 else 0)), 
                min(255, base_color[2] + (glow_intensity if base_color[2] > 0 else 0))
            )
        return base_color
    return base_color 