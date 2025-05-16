import pygame
import random
import math
from typing import List, Optional, Tuple
from .fishable_items import FishableItem, get_random_fishable, FishableType

class FishingState:
    IDLE = 0         # Not fishing
    CASTING = 1      # Using the swing meter
    WAITING = 2      # Waiting for a bite
    QTE = 3          # Quick Time Event when fish bites
    BATTLE = 4       # Fishing battle with the bar mechanic
    RESULT = 5       # Showing result

class FishingMinigame:
    def __init__(self, screen: pygame.Surface, font_path: str):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Load font
        self.font = pygame.font.Font(font_path, 32)
        self.small_font = pygame.font.Font(font_path, 24)
        
        # Colors - Using a terminal-like color scheme
        self.WHITE = (230, 230, 230)
        self.BLACK = (10, 10, 10)
        self.GREEN = (0, 200, 0)
        self.RED = (240, 20, 20)
        self.YELLOW = (240, 240, 0)
        self.CYAN = (0, 240, 240)
        self.MAGENTA = (240, 0, 240)
        
        # Game state
        self.state = FishingState.IDLE
        
        # Fishing rod state
        self.rod_angle = 45
        self.rod_start_pos = (50, self.height - 50)
        self.cast_distance = 0
        self.max_cast_distance = 300
        
        # Casting meter state
        self.cast_power = 0
        self.max_power = 100
        self.power_increasing = True
        self.cast_quality = ""
        self.cast_quality_timer = 120  # Increased to show feedback longer
        
        # QTE state
        self.qte_start_time = 0
        self.qte_duration = 1500  # Increased for better response time
        self.qte_success_window = 750  # Increased for easier success
        self.qte_clicked = False
        
        # Fishing battle state
        self.battle_bar_pos = 50  # Position of the player's bar
        self.battle_bar_velocity = 0  # Velocity of the bar
        self.battle_zone_pos = 50  # Center position of the target zone
        self.battle_zone_size = 30  # Size of the target zone (increased)
        self.battle_difficulty = 1  # Multiplier for difficulty
        self.battle_score = 0  # Current score in the battle
        self.max_battle_score = 100  # Score needed to catch fish
        self.battle_timer = 0  # Timer for difficulty increases
        
        # Fishing line state
        self.line_end_pos = self.rod_start_pos
        
        # Fishing state
        self.current_fish: Optional[FishableItem] = None
        
        # Message display
        self.message = ""
        self.message_timer = 0
        
        # Inventory
        self.inventory: List[FishableItem] = []

    def draw_rod(self):
        # Draw fishing rod as a line
        length = 100
        end_x = self.rod_start_pos[0] + length * math.cos(math.radians(self.rod_angle))
        end_y = self.rod_start_pos[1] - length * math.sin(math.radians(self.rod_angle))
        rod_end = (end_x, end_y)
        pygame.draw.line(self.screen, self.GREEN, self.rod_start_pos, rod_end, 5)
        
        # Draw fishing line if cast
        if self.state in [FishingState.WAITING, FishingState.QTE, FishingState.BATTLE]:
            pygame.draw.line(self.screen, self.WHITE, rod_end, self.line_end_pos, 1)

    def draw_casting_meter(self):
        if self.state == FishingState.CASTING:
            # Draw meter frame
            meter_width = 40
            meter_height = 200
            x = 50
            y = (self.height - meter_height) // 2
            
            # Draw meter background
            pygame.draw.rect(self.screen, self.BLACK, (x, y, meter_width, meter_height), 0)
            pygame.draw.rect(self.screen, self.WHITE, (x, y, meter_width, meter_height), 2)
            
            # Draw zones
            # Weak zone: bottom 30%
            weak_zone_height = meter_height * 0.3
            pygame.draw.rect(self.screen, self.RED, (x, y + meter_height - weak_zone_height, meter_width, weak_zone_height))
            
            # Good zone: middle 50%
            good_zone_height = meter_height * 0.5
            pygame.draw.rect(self.screen, self.YELLOW, (x, y + meter_height - weak_zone_height - good_zone_height, meter_width, good_zone_height))
            
            # Perfect zone: top 20%
            perfect_zone_height = meter_height * 0.2
            pygame.draw.rect(self.screen, self.GREEN, (x, y, meter_width, perfect_zone_height))
            
            # Draw power indicator
            indicator_pos = y + meter_height - (self.cast_power / self.max_power) * meter_height
            indicator_height = 10
            pygame.draw.rect(self.screen, self.CYAN, (x - 10, indicator_pos - indicator_height // 2, meter_width + 20, indicator_height))
        
        # Always show cast quality message when it exists
        if self.cast_quality and self.cast_quality_timer > 0:
            # Set color based on quality
            if "PERFECT" in self.cast_quality:
                color = self.GREEN
            elif "GOOD" in self.cast_quality:
                color = self.YELLOW
            else:
                color = self.RED
                
            text = self.font.render(self.cast_quality, True, color)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(text, text_rect)

    def draw_qte(self):
        if self.state == FishingState.QTE:
            # Get elapsed time
            elapsed = pygame.time.get_ticks() - self.qte_start_time
            progress = min(1.0, elapsed / self.qte_duration)
            
            # Draw QTE bar
            bar_width = 400
            bar_height = 40
            x = (self.width - bar_width) // 2
            y = self.height // 2
            
            # Draw background
            pygame.draw.rect(self.screen, self.BLACK, (x, y, bar_width, bar_height), 0)
            pygame.draw.rect(self.screen, self.WHITE, (x, y, bar_width, bar_height), 2)
            
            # Draw progress
            pygame.draw.rect(self.screen, self.RED, (x, y, bar_width * progress, bar_height))
            
            # Draw success window
            success_start = (self.qte_duration - self.qte_success_window) / self.qte_duration
            success_width = (self.qte_success_window / self.qte_duration) * bar_width
            pygame.draw.rect(self.screen, self.GREEN, (x + bar_width * success_start, y, success_width, bar_height), 3)
            
            # Draw instruction
            text = self.font.render("PRESS SPACE!", True, self.YELLOW)
            text_rect = text.get_rect(center=(self.width // 2, y - 40))
            self.screen.blit(text, text_rect)

    def draw_battle(self):
        if self.state == FishingState.BATTLE:
            # Draw battle area
            bar_width = 50
            bar_height = 300
            area_x = (self.width - bar_width) // 2
            area_y = (self.height - bar_height) // 2
            
            # Draw background
            pygame.draw.rect(self.screen, self.BLACK, (area_x, area_y, bar_width, bar_height), 0)
            pygame.draw.rect(self.screen, self.WHITE, (area_x, area_y, bar_width, bar_height), 2)
            
            # Draw target zone
            zone_y = area_y + bar_height * (1 - self.battle_zone_pos / 100)
            zone_height = bar_height * (self.battle_zone_size / 100)
            zone_y -= zone_height / 2  # Center the zone
            pygame.draw.rect(self.screen, self.YELLOW, (area_x, zone_y, bar_width, zone_height))
            
            # Draw player bar
            bar_y = area_y + bar_height * (1 - self.battle_bar_pos / 100)
            pygame.draw.rect(self.screen, self.CYAN, (area_x - 10, bar_y - 5, bar_width + 20, 10))
            
            # Draw score
            score_width = 300
            score_height = 30
            score_x = (self.width - score_width) // 2
            score_y = area_y + bar_height + 30
            
            # Draw score background
            pygame.draw.rect(self.screen, self.BLACK, (score_x, score_y, score_width, score_height), 0)
            pygame.draw.rect(self.screen, self.WHITE, (score_x, score_y, score_width, score_height), 2)
            
            # Draw score progress
            progress = (self.battle_score / self.max_battle_score) * score_width
            pygame.draw.rect(self.screen, self.GREEN, (score_x, score_y, progress, score_height))
            
            # Draw score text
            score_text = f"{int(self.battle_score)}/{int(self.max_battle_score)}"
            text = self.font.render(score_text, True, self.WHITE)
            text_rect = text.get_rect(center=(score_x + score_width // 2, score_y + score_height // 2))
            self.screen.blit(text, text_rect)
            
            # Draw instruction
            text = self.font.render("HOLD SPACE TO RAISE BAR", True, self.YELLOW)
            text_rect = text.get_rect(center=(self.width // 2, area_y - 40))
            self.screen.blit(text, text_rect)

    def draw_message(self):
        if self.message and self.message_timer > 0:
            # Draw a background for the message
            text = self.font.render(self.message, True, self.WHITE)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 4))
            
            # Add padding
            padding = 20
            bg_rect = pygame.Rect(
                text_rect.left - padding,
                text_rect.top - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            # Draw background and text
            pygame.draw.rect(self.screen, self.BLACK, bg_rect, 0)
            pygame.draw.rect(self.screen, self.WHITE, bg_rect, 2)
            self.screen.blit(text, text_rect)

    def start_fishing(self):
        self.state = FishingState.CASTING
        self.cast_power = 0
        self.power_increasing = True
        self.cast_quality = ""
        self.cast_quality_timer = 0
        self.message = "Hold SPACE to charge, release to cast!"
        self.message_timer = 120

    def cast_line(self):
        # Determine cast quality based on power
        if self.cast_power >= 80:  # Top 20% - Perfect cast
            quality = "PERFECT CAST!"
            self.cast_distance = self.max_cast_distance
            quality_bonus = 1.5
        elif self.cast_power >= 30:  # Middle 50% - Good cast
            quality = "GOOD CAST!"
            self.cast_distance = self.max_cast_distance * 0.8
            quality_bonus = 1.0
        else:  # Bottom 30% - Weak cast
            quality = "WEAK CAST..."
            self.cast_distance = self.max_cast_distance * 0.5
            quality_bonus = 0.5
        
        # Set the fishing line end position based on cast distance
        angle = math.radians(self.rod_angle)
        end_x = self.rod_start_pos[0] + self.cast_distance * math.cos(angle)
        end_y = (self.height // 2) + 20  # Just below water surface
        self.line_end_pos = (end_x, end_y)
        
        # Update state
        self.state = FishingState.WAITING
        self.cast_quality = quality
        self.cast_quality_timer = 120  # Show quality longer
        self.message = "Waiting for a bite..."
        self.message_timer = 60
        
        # Adjust the bite chance based on cast quality
        self.bite_chance = 0.03 * quality_bonus  # Increased base chance

    def fish_bite(self):
        self.current_fish = get_random_fishable()
        
        # If trash, skip QTE and battle
        if self.current_fish.type == FishableType.TRASH:
            self.inventory.append(self.current_fish)
            self.message = f"You caught some trash: {self.current_fish.name}!"
            self.message_timer = 120
            self.state = FishingState.RESULT
        else:
            # Start QTE for fish
            self.state = FishingState.QTE
            self.qte_start_time = pygame.time.get_ticks()
            self.qte_clicked = False
            self.message = "Fish on! Press SPACE quickly!"
            self.message_timer = 60

    def start_battle(self):
        self.state = FishingState.BATTLE
        self.battle_bar_pos = 50
        self.battle_bar_velocity = 0
        self.battle_zone_pos = 50
        
        # Set difficulty based on fish rarity but with smaller differences
        fish_difficulty = self.current_fish.rarity  # 0.0 to 1.0
        self.battle_difficulty = 0.8 + (0.4 * (1 - fish_difficulty))  # Reduced range
        
        # Set zone size based on difficulty (increase min size)
        self.battle_zone_size = max(20, 35 - (self.battle_difficulty * 5))  # Larger zones
        
        # Set score needed based on fish weight and rarity (but reduced)
        base_score = 80
        weight_factor = min(5, self.current_fish.weight) / 10  # 0.0 to 0.5
        self.max_battle_score = base_score * (1 + weight_factor + (0.5 * (1 - fish_difficulty)))
        
        self.battle_score = 0
        self.battle_timer = 0
        
        self.message = "Keep the bar in the yellow zone!"
        self.message_timer = 120

    def complete_fishing(self, success: bool):
        if success and self.current_fish:
            self.inventory.append(self.current_fish)
            self.message = self.current_fish.get_description()
        else:
            self.message = "The fish got away!"
        
        self.message_timer = 120
        self.state = FishingState.RESULT
        self.current_fish = None

    def update_casting(self):
        # Update power when holding space
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.power_increasing:
                self.cast_power += 2
                if self.cast_power >= self.max_power:
                    self.power_increasing = False
            else:
                self.cast_power -= 2
                if self.cast_power <= 0:
                    self.power_increasing = True
    
    def update_waiting(self):
        # Check for a bite
        if random.random() < self.bite_chance:
            self.fish_bite()
    
    def update_qte(self):
        # Update QTE progress
        elapsed = pygame.time.get_ticks() - self.qte_start_time
        
        # Check if QTE is finished
        if elapsed >= self.qte_duration:
            # Failed QTE
            self.complete_fishing(False)
        
        # Check if in success window
        success_start = self.qte_duration - self.qte_success_window
        in_window = elapsed >= success_start
        
        # If player clicked in success window
        if self.qte_clicked and in_window:
            self.start_battle()
    
    def update_battle(self):
        # Update battle timer
        self.battle_timer += 1
        
        # Move the target zone occasionally
        if self.battle_timer % 90 == 0:  # Slowed down movement
            # Move target zone randomly, weighted toward the center more
            target = random.uniform(30, 70)  # More central range
                
            # Gradually move zone toward target
            zone_speed = 0.3 * self.battle_difficulty  # Slower movement
            if self.battle_zone_pos < target:
                self.battle_zone_pos = min(target, self.battle_zone_pos + zone_speed)
            else:
                self.battle_zone_pos = max(target, self.battle_zone_pos - zone_speed)
        
        # Apply gravity to the bar
        self.battle_bar_velocity += 0.15 * self.battle_difficulty  # Reduced gravity
        
        # Cap maximum velocity
        max_vel = 1.5 * self.battle_difficulty  # Reduced max velocity
        self.battle_bar_velocity = min(max_vel, self.battle_bar_velocity)
        
        # Move the bar with velocity
        self.battle_bar_pos -= self.battle_bar_velocity
        
        # Check if bar is in bounds
        if self.battle_bar_pos < 0:
            self.battle_bar_pos = 0
            self.battle_bar_velocity = 0
        
        if self.battle_bar_pos > 100:
            self.battle_bar_pos = 100
            self.battle_bar_velocity = 0
        
        # Check if bar is in target zone
        bar_top = self.battle_bar_pos - 3
        bar_bottom = self.battle_bar_pos + 3
        zone_top = self.battle_zone_pos - self.battle_zone_size / 2
        zone_bottom = self.battle_zone_pos + self.battle_zone_size / 2
        
        # Calculate overlap
        overlap = min(bar_bottom, zone_bottom) - max(bar_top, zone_top)
        
        # Add score based on overlap
        if overlap > 0:
            # Max score when centered in zone
            center_distance = abs(self.battle_bar_pos - self.battle_zone_pos)
            center_factor = 1.0 - (center_distance / (self.battle_zone_size / 2))
            center_factor = max(0, center_factor)
            
            # Add score - increased rate
            score_rate = 0.7 * (1 + center_factor)
            self.battle_score += score_rate
            
            # Check for completion
            if self.battle_score >= self.max_battle_score:
                self.complete_fishing(True)
    
    def update_result(self):
        # After showing result, go back to idle state
        if self.message_timer <= 0:
            self.state = FishingState.IDLE

    def update(self):
        # Update state-specific logic
        if self.state == FishingState.CASTING:
            self.update_casting()
        elif self.state == FishingState.WAITING:
            self.update_waiting()
        elif self.state == FishingState.QTE:
            self.update_qte()
        elif self.state == FishingState.BATTLE:
            self.update_battle()
        elif self.state == FishingState.RESULT:
            self.update_result()
        
        # Update timers
        if self.message_timer > 0:
            self.message_timer -= 1
            
        if self.cast_quality_timer > 0:
            self.cast_quality_timer -= 1

    def draw(self):
        # Draw rod and line
        self.draw_rod()
        
        # Draw state-specific elements
        if self.state == FishingState.CASTING:
            self.draw_casting_meter()
        elif self.state == FishingState.QTE:
            self.draw_qte()
        elif self.state == FishingState.BATTLE:
            self.draw_battle()
            
        # Draw messages
        self.draw_message()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            # Space key to start fishing if idle
            if event.key == pygame.K_SPACE and self.state == FishingState.IDLE:
                self.start_fishing()
            
            # Space key for QTE
            elif event.key == pygame.K_SPACE and self.state == FishingState.QTE:
                self.qte_clicked = True
                
        elif event.type == pygame.KEYUP:
            # Release space to cast when charging
            if event.key == pygame.K_SPACE and self.state == FishingState.CASTING:
                self.cast_line()
                
        # Handle space key press for battle (continuous input)
        keys = pygame.key.get_pressed()
        if self.state == FishingState.BATTLE and keys[pygame.K_SPACE]:
            # Apply upward force when space is held - increased significantly
            self.battle_bar_velocity -= 1.5 * self.battle_difficulty 