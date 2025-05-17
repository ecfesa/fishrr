import pygame

# Window settings
WIDTH, HEIGHT = 800, 600
SQUARE_SIZE = 300  # Reduced square size
SQUARE_POS = ((WIDTH - SQUARE_SIZE) // 2, (HEIGHT - SQUARE_SIZE) // 2)
BOAT_SIZE = 10
BOAT_POS = (WIDTH // 2 - BOAT_SIZE // 2, HEIGHT // 2 - BOAT_SIZE // 2)
BOAT_CENTER = (WIDTH // 2, HEIGHT // 2)  # Center point of the boat
BAR_THICKNESS = 8

# Outer square for bar indicators
OUTER_SQUARE_MARGIN = 30  # Distance between inner and outer squares
OUTER_SQUARE_SIZE = SQUARE_SIZE + (OUTER_SQUARE_MARGIN * 2)
OUTER_SQUARE_POS = (
    (WIDTH - OUTER_SQUARE_SIZE) // 2,
    (HEIGHT - OUTER_SQUARE_SIZE) // 2
)

# Colors - simplified for terminal-like aesthetic
WHITE = (220, 220, 220)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
TERM_GREEN = (0, 210, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Physics variables - extreme difficulty settings
MAX_SPEED = 250  # Significantly increased max speed
MAX_ACCELERATION = 4.0  # Extreme acceleration
MIN_SPEED = -50  # Significant backward movement
ACCELERATION_DECAY = 0.006  # Very low decay for challenging control
DRAG = 0.01  # Minimal drag for extreme speeds

# Destination/progress variables - extreme distance
TOTAL_DISTANCE = 75000  # Massive journey distance 

# Wind gust parameters
GUST_INTERVAL_BASE = 120  # Base interval for gusts
GUST_MIN_INTERVAL = 30  # Minimum interval between gusts
GUST_BASE_SPEED = 3.5  # Base movement speed

# Border parameters
BORDER_THICKNESS = 2
BORDER_MARGIN = 10
CORNER_SIZE = 10 