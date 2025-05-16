import pygame
import math
import random
from constants import *

# Wind gust class - Significantly harder with extreme speed/complexity at high accelerations
class WindGust:
    def __init__(self, direction=None, boat_acceleration=0, difficulty_factor=1.0):
        # Direction: 0=top, 1=right, 2=bottom, 3=left
        self.direction = direction if direction is not None else random.randint(0, 3)
        
        # Base speed increases dramatically with acceleration
        accel_factor = 1.0 + min(3.0, abs(boat_acceleration) * 1.5)  # Higher multiplier, higher cap
        self.speed = GUST_BASE_SPEED * accel_factor
        
        # Add slight random variance to speed
        self.speed *= random.uniform(0.9, 1.1)
        
        self.active = True
        self.collected = False
        self.blocked = False
        self.missed = False  # New flag to track if gust was missed
        
        # Warning time decreases with speed, acceleration, and difficulty (progressively less reaction time)
        warning_base = 30 / difficulty_factor  # Base time decreases as difficulty increases
        warning_min = max(3, 10 - int(abs(boat_acceleration) * 1.5 * difficulty_factor))  # Can go as low as 3 frames at extreme difficulty
        self.warning_time = max(warning_min, int(warning_base / accel_factor))
        self.warning = True
        
        # At high acceleration, add wobble to make prediction harder
        self.wobble = 0
        self.wobble_amount = 0
        if abs(boat_acceleration) > MAX_ACCELERATION * 0.5:
            self.wobble = random.uniform(0, 2 * math.pi)
            self.wobble_amount = random.uniform(0, min(15, abs(boat_acceleration) * 5))
        
        # Set position based on direction - always from edge of square
        if self.direction == 0:  # From top
            self.x = BOAT_CENTER[0]
            self.y = SQUARE_POS[1]
        elif self.direction == 1:  # From right
            self.x = SQUARE_POS[0] + SQUARE_SIZE
            self.y = BOAT_CENTER[1]
        elif self.direction == 2:  # From bottom
            self.x = BOAT_CENTER[0]
            self.y = SQUARE_POS[1] + SQUARE_SIZE
        elif self.direction == 3:  # From left
            self.x = SQUARE_POS[0]
            self.y = BOAT_CENTER[1]
            
        # Calculate movement vector directly to boat
        dx = BOAT_CENTER[0] - self.x
        dy = BOAT_CENTER[1] - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else:
            self.vx = 0
            self.vy = 0
    
    def update(self, bar_position, boat_speed):
        # Handle warning phase
        if self.warning:
            self.warning_time -= 1
            if self.warning_time <= 0:
                self.warning = False
            return 0
        
        # Update wobble if active
        if self.wobble_amount > 0:
            self.wobble += 0.2
            if self.wobble > 2 * math.pi:
                self.wobble -= 2 * math.pi
        
        # Move gust toward boat center with wobble effect
        wobble_x = math.sin(self.wobble) * self.wobble_amount
        wobble_y = math.cos(self.wobble) * self.wobble_amount
        
        self.x += self.vx + wobble_x
        self.y += self.vy + wobble_y
        
        # Check if gust hit the boat
        distance = math.sqrt((self.x - BOAT_CENTER[0])**2 + (self.y - BOAT_CENTER[1])**2)
        
        # If gust is near the boat (collision detection)
        if distance < BOAT_SIZE / 2:
            # Check if bar is facing the opposite direction of the gust
            # For bar to successfully collect the wind, it should be on the opposite side
            if (self.direction == 0 and bar_position == 2) or \
               (self.direction == 1 and bar_position == 3) or \
               (self.direction == 2 and bar_position == 0) or \
               (self.direction == 3 and bar_position == 1):
                # Successfully collected - increase acceleration
                # Higher speed boost at high speeds (risk/reward)
                boost_amount = 0.5
                if abs(boat_speed) > MAX_SPEED * 0.6:
                    boost_amount = 0.7  # Greater reward at high speeds
                
                self.collected = True
                self.active = False
                return boost_amount
                
            # If the bar is facing the same direction as the gust, it blocks it
            elif (self.direction == 0 and bar_position == 0) or \
                 (self.direction == 1 and bar_position == 1) or \
                 (self.direction == 2 and bar_position == 2) or \
                 (self.direction == 3 and bar_position == 3):
                # Blocked by bar - decrease acceleration
                # Higher penalty at high speeds
                penalty_amount = -0.3
                if abs(boat_speed) > MAX_SPEED * 0.6:
                    penalty_amount = -0.5  # Greater penalty at high speeds
                
                self.blocked = True
                self.active = False
                return penalty_amount
            else:
                # Neither collected nor blocked - wind passes by
                # Apply smaller penalty (half of blocked penalty)
                self.missed = True
                self.active = False
                
                # Calculate penalty as half of what a blocked gust would cause
                miss_penalty = -0.15  # Half of -0.3
                if abs(boat_speed) > MAX_SPEED * 0.6:
                    miss_penalty = -0.25  # Half of -0.5
                
                return miss_penalty
        
        # Check if gust is outside the square completely
        if (distance > SQUARE_SIZE):
            self.active = False
        
        return 0  # No effect on acceleration
    
    def draw(self, screen):
        if not self.active:
            return
            
        if self.warning:
            # Draw warning indicator based on direction
            warn_length = 20
            warn_thickness = 2
            
            if self.direction == 0:  # Top
                x, y = BOAT_CENTER[0], SQUARE_POS[1] + warn_thickness
                pygame.draw.rect(screen, RED, (x - warn_length//2, y, warn_length, warn_thickness))
            elif self.direction == 1:  # Right
                x, y = SQUARE_POS[0] + SQUARE_SIZE - warn_thickness, BOAT_CENTER[1]
                pygame.draw.rect(screen, RED, (x - warn_thickness, y - warn_length//2, warn_thickness, warn_length))
            elif self.direction == 2:  # Bottom
                x, y = BOAT_CENTER[0], SQUARE_POS[1] + SQUARE_SIZE - warn_thickness
                pygame.draw.rect(screen, RED, (x - warn_length//2, y - warn_thickness, warn_length, warn_thickness))
            elif self.direction == 3:  # Left
                x, y = SQUARE_POS[0], BOAT_CENTER[1]
                pygame.draw.rect(screen, RED, (x, y - warn_length//2, warn_thickness, warn_length))
        else:
            # Draw wind gust as arrow - simple triangle shape
            # Triangle base size
            size = 10
            
            # Calculate triangle points based on direction
            if self.direction == 0:  # From top
                points = [
                    (self.x, self.y),  # tip
                    (self.x - size, self.y - size),  # left base
                    (self.x + size, self.y - size)   # right base
                ]
            elif self.direction == 1:  # From right
                points = [
                    (self.x, self.y),  # tip
                    (self.x + size, self.y - size),  # top base
                    (self.x + size, self.y + size)   # bottom base
                ]
            elif self.direction == 2:  # From bottom
                points = [
                    (self.x, self.y),  # tip
                    (self.x - size, self.y + size),  # left base
                    (self.x + size, self.y + size)   # right base
                ]
            elif self.direction == 3:  # From left
                points = [
                    (self.x, self.y),  # tip
                    (self.x - size, self.y - size),  # top base
                    (self.x - size, self.y + size)   # bottom base
                ]
                
            # Draw wind arrow
            pygame.draw.polygon(screen, GREEN, points)

# Moving objects to simulate movement
class MovingObject:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.size = random.randint(3, 6)
        # Position it randomly within the square but outside the center area where the boat is
        while True:
            self.x = random.randint(SQUARE_POS[0] + 20, SQUARE_POS[0] + SQUARE_SIZE - 20)
            self.y = random.randint(SQUARE_POS[1] + 20, SQUARE_POS[1] + SQUARE_SIZE - 20)
            # Check if it's not too close to the boat center
            dist_to_center = math.sqrt((self.x - BOAT_CENTER[0])**2 + (self.y - BOAT_CENTER[1])**2)
            if dist_to_center > BOAT_SIZE * 1.5:
                break
                
        self.type = random.choice(['rock', 'buoy', 'debris'])
        
    def update(self, speed):
        # Objects move from top to bottom to simulate forward movement
        # Speed determines how fast they move down
        self.y += speed / 10
        
        # If objects go below the square, reset them to the top
        if self.y > SQUARE_POS[1] + SQUARE_SIZE:
            self.y = SQUARE_POS[1]
            self.x = random.randint(SQUARE_POS[0] + 20, SQUARE_POS[0] + SQUARE_SIZE - 20)
        
        # If objects go above the square (when moving backward), reset to bottom
        if self.y < SQUARE_POS[1]:
            self.y = SQUARE_POS[1] + SQUARE_SIZE
            self.x = random.randint(SQUARE_POS[0] + 20, SQUARE_POS[0] + SQUARE_SIZE - 20)
            
    def draw(self, screen):
        if self.type == 'rock':
            # Draw as X
            pygame.draw.line(screen, GRAY, (self.x - self.size, self.y - self.size), 
                            (self.x + self.size, self.y + self.size), 1)
            pygame.draw.line(screen, GRAY, (self.x + self.size, self.y - self.size), 
                            (self.x - self.size, self.y + self.size), 1)
        elif self.type == 'buoy':
            # Draw as O
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size, 1)
        elif self.type == 'debris':
            # Draw as triangle
            pygame.draw.polygon(screen, DARK_GREEN, [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ], 1)

# Hydra enemy that chases the boat
class Hydra:
    def __init__(self, start_distance, width=120, height=60):
        self.distance = start_distance  # Distance from start (position on the progress track)
        self.width = width
        self.height = height
        self.speed = 0  # Base speed, will be adjusted based on difficulty
        self.glow_timer = 0  # For pulsing effect
        self.glow_direction = 1
        self.defeated = False  # Flag for when hydra is left behind
        
        # Load sprite image
        self.original_image = pygame.image.load("sprites/hydra.png").convert_alpha()
        # Calculate scale to match desired width/height while preserving aspect ratio
        img_width, img_height = self.original_image.get_size()
        scale_factor = min(width / img_width, height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        
        # Store actual dimensions after scaling
        self.actual_width = new_width
        self.actual_height = new_height
    
    def update(self, boat_speed, difficulty_factor, debug_mode=False):
        # Update glow effect
        self.glow_timer += 0.1 * self.glow_direction
        if self.glow_timer >= 3.14 or self.glow_timer <= 0:
            self.glow_direction *= -1
        
        # Chase logic - hydra moves at a speed based on difficulty and boat speed
        # At higher difficulties, the hydra gets closer to the boat's speed
        if difficulty_factor < 1.3:  # Easy - Hydra is quite slow
            self.speed = max(20, boat_speed * 0.7)
        elif difficulty_factor < 1.6:  # Medium - Hydra is faster
            self.speed = max(30, boat_speed * 0.8)
        else:  # Hard - Hydra is very fast
            self.speed = max(40, boat_speed * 0.9)
            
        # If boat goes backward, hydra catches up faster
        if boat_speed < 0:
            self.speed += abs(boat_speed * 0.5)
            
        # Move hydra based on speed
        self.distance += self.speed / 10
        
        # Check if boat left the hydra far behind (only after hydra has fallen very far behind)
        # The hydra is defeated if it's more than 10000 units behind the starting point
        if self.distance < -10000:
            self.defeated = True
            if debug_mode:
                print(f"Hydra defeated at distance {self.distance}")
        else:
            self.defeated = False
            
        return self.defeated
    
    def draw(self, screen, current_distance, total_distance, progress_rect, debug_mode=False):
        # Calculate relative position (how close hydra is to boat)
        distance_between = current_distance - self.distance
        rel_position = distance_between / 2000  # Scale for visual purposes
        
        # Debug output only if debug mode is on
        if debug_mode:
            print(f"Hydra distance check: distance={self.distance:.1f}, boat={current_distance:.1f}, " +
                  f"between={distance_between:.1f}, rel_pos={rel_position:.2f}")
        
        # Only draw if it's within visible range - increased from 3 to 5 for better visibility
        if rel_position < 5:
            # Calculate position based on distance from boat
            # Higher rel_position = further away from boat = lower on screen
            # Adjusted formula to keep hydras visible within the square
            center_y = BOAT_CENTER[1] + (SQUARE_SIZE / 2) * (rel_position / 5)
            
            # Debug output only if debug mode is on
            if debug_mode:
                print(f"Hydra drawing: rel_pos={rel_position:.2f}, center_y={center_y:.2f}, " +
                      f"dist_between={distance_between:.2f}, boat_center_y={BOAT_CENTER[1]}")
            
            # Determine alpha based on distance (fade out as it gets further)
            alpha = max(30, min(255, int(255 * (1 - rel_position/5))))
            
            # Create a copy of the image with pulsing effect
            # Create a pulsing scale factor
            pulse_scale = 1.0 + 0.05 * math.sin(self.glow_timer * 2)
            pulse_width = int(self.actual_width * pulse_scale)
            pulse_height = int(self.actual_height * pulse_scale)
            
            # Create pulsing image
            pulsed_image = pygame.transform.scale(self.image, (pulse_width, pulse_height))
            
            # Apply alpha for distance fade effect
            if alpha < 255:
                # Create a copy for alpha modification
                temp_surf = pygame.Surface((pulse_width, pulse_height), pygame.SRCALPHA)
                temp_surf.fill((255, 255, 255, alpha))  # Fill with alpha value
                pulsed_image.blit(temp_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Blit to screen - centered on x, position depends on relative distance
            screen.blit(pulsed_image, 
                       (BOAT_CENTER[0] - pulse_width//2, center_y - pulse_height//2))
            
            if debug_mode:
                print(f"Hydra drawn at coords: ({BOAT_CENTER[0] - self.width//2}, {center_y - self.height//2})")
        elif debug_mode:
            print(f"Hydra not drawn: rel_pos={rel_position:.2f} too far")
        
        # Draw hydra position on progress bar
        if progress_rect:
            # Calculate position on progress bar - ensure it's visible by clamping to at least 0
            progress_percentage = min(1.0, max(0.0, self.distance / total_distance))
            progress_height = progress_rect.height
            progress_y = progress_rect.y + progress_height - int(progress_percentage * progress_height)
            
            # Draw larger, more visible hydra indicator
            pygame.draw.polygon(screen, (255, 0, 0), [
                (progress_rect.x - 10, progress_y - 6),  # Top point
                (progress_rect.x - 10, progress_y + 6),  # Bottom point
                (progress_rect.x - 2, progress_y)       # Tip point
            ])
            
            # Add a red flash effect when hydra is close to boat
            if current_distance - self.distance < 1500:
                # Create a pulsing effect
                flash_intensity = int(128 + 127 * math.sin(self.glow_timer * 2))
                pygame.draw.rect(screen, (255, 0, 0, flash_intensity), 
                              (progress_rect.x, progress_y - 8, progress_rect.width, 16), 2)
            
            if debug_mode:
                print(f"Hydra progress indicator drawn at y={progress_y}")
        elif debug_mode:
            print("Cannot draw hydra on progress bar: progress_rect is None") 