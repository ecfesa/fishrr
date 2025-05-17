import pygame
import random
from .settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GameState, # screen removed, passed in constructor
    font, small_font, WHITE, RED, BLACK,
    DARK_BLUE # For clearing screen or specific backgrounds if needed
)
from .drawing import draw_qte_screen, draw_battle_screen, draw_text
from .items import Fish, TrashItem, FishDifficulty # For type checking and difficulty access

class FishingMinigame:
    def __init__(self, current_item, screen_surface_param):
        self.current_item = current_item
        self.screen_surface = screen_surface_param # Use passed screen surface

        # QTE variables
        self.qte_active = False
        self.qte_key = pygame.K_SPACE # QTE is always SPACE now
        self.qte_key_display = pygame.key.name(self.qte_key)
        self.qte_timer_max = 2.0
        self.qte_timer_current = 0
        self.qte_success = False

        # Battle variables (can be initialized here or when battle starts)
        self.fish_y = (SCREEN_HEIGHT * 0.6 - 30) / 2
        self.player_bar_y = (SCREEN_HEIGHT * 0.6 - 80) / 2
        self.player_bar_lift_speed = 300
        self.player_bar_gravity = 150
        
        self.fish_movement_speed = 3
        self.fish_movement_direction = 1
        self.fish_target_y = self.fish_y
        self.fish_move_timer = 0
        self.fish_behavior_change_interval = 1.0
        
        self.catch_progress = 10.0
        self.catch_rate = 0.5
        self.penalty_rate = 0.02

        self.minigame_state = None # To track if we are in 'QTE' or 'BATTLE' part
        self.battle_outcome = None # True for win, False for loss

    def _setup_battle_parameters(self):
        if isinstance(self.current_item, Fish):
            if self.current_item.difficulty == FishDifficulty.EASY:
                self.fish_movement_speed = 2
                self.fish_behavior_change_interval = 1.5
                self.catch_rate = 0.5 # Easier fish, faster catch
            elif self.current_item.difficulty == FishDifficulty.MEDIUM:
                self.fish_movement_speed = 4
                self.fish_behavior_change_interval = 1.0
                self.catch_rate = 0.4
            elif self.current_item.difficulty == FishDifficulty.HARD:
                self.fish_movement_speed = 6
                self.fish_behavior_change_interval = 0.3
                self.catch_rate = 0.3
            elif self.current_item.difficulty == FishDifficulty.LEGENDARY:
                self.fish_movement_speed = 8
                self.fish_behavior_change_interval = 0.5
                self.catch_rate = 0.09 # Harder fish, slower catch
        else: # Should ideally not happen for battle, but as a safe default
            self.fish_movement_speed = 0
            self.catch_rate = 0.05 # e.g. for trash if it somehow enters battle
        
        # Reset positions and progress for a new battle
        self.fish_y = (SCREEN_HEIGHT * 0.6 - 30) / 2
        self.player_bar_y = (SCREEN_HEIGHT * 0.6 - 80) / 2
        
        if isinstance(self.current_item, Fish):
            self.catch_progress = 0.15 # Start fish battles with 15% progress
        elif isinstance(self.current_item, TrashItem): 
             self.catch_progress = 0.1 # Small initial for trash if it ever got here
        else:
            self.catch_progress = 0.0 # Default for any other case

    def start(self):
        # Decide if QTE happens (e.g. 50% chance for Fish)
        if isinstance(self.current_item, Fish) and random.random() < 0.5:
            self.minigame_state = 'QTE'
            self.qte_active = True
            self.qte_timer_current = self.qte_timer_max
            self.qte_success = False
        elif isinstance(self.current_item, Fish): # Fish, but no QTE
            self.minigame_state = 'BATTLE'
            self._setup_battle_parameters()
        else: # Not a fish (e.g. Trash), should not start minigame via this class usually.
              # This path assumes the main loop directs trash to RESULT directly.
              # If this class were to handle trash, it would return success immediately.
            print("Warning: FishingMinigame started with non-Fish item and no QTE path.")
            return True # Or handle as error/immediate success for trash
        
        return self.run_minigame_loop() # Returns True for win, False for loss

    def run_minigame_loop(self):
        running_minigame = True
        clock = pygame.time.Clock()

        while running_minigame:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if event.type == pygame.KEYDOWN:
                    if self.minigame_state == 'QTE' and self.qte_active:
                        if event.key == self.qte_key:
                            self.qte_success = True
                            self.qte_active = False
                            # Transition to BATTLE if QTE was for a Fish
                            if isinstance(self.current_item, Fish):
                                self.minigame_state = 'BATTLE'
                                self._setup_battle_parameters()
                            else: # QTE success for non-fish (should not happen with current item types)
                                running_minigame = False
                                self.battle_outcome = True # QTE success = overall win
                        else: # Wrong key for QTE
                            self.qte_success = False
                            self.qte_active = False
                            running_minigame = False
                            self.battle_outcome = False # QTE fail = overall loss
            
            # Logic Updates
            if self.minigame_state == 'QTE' and self.qte_active:
                self.qte_timer_current -= dt
                if self.qte_timer_current <= 0:
                    self.qte_active = False
                    self.qte_success = False
                    running_minigame = False
                    self.battle_outcome = False # QTE timeout = overall loss
            
            elif self.minigame_state == 'BATTLE':
                keys = pygame.key.get_pressed()
                battle_area_height = SCREEN_HEIGHT * 0.6
                player_bar_h = 80

                if keys[pygame.K_SPACE]:
                    self.player_bar_y -= self.player_bar_lift_speed * dt
                else:
                    self.player_bar_y += self.player_bar_gravity * dt
                self.player_bar_y = max(0, min(self.player_bar_y, battle_area_height - player_bar_h))

                self.fish_move_timer -= dt
                if self.fish_move_timer <= 0:
                    self.fish_move_timer = self.fish_behavior_change_interval
                    self.fish_target_y = random.uniform(0, battle_area_height - 30)
                    self.fish_movement_direction = 1 if self.fish_y < self.fish_target_y else -1
                
                if self.fish_movement_speed > 0:
                    self.fish_y += self.fish_movement_speed * self.fish_movement_direction * dt * 10
                self.fish_y = max(0, min(self.fish_y, battle_area_height - 30))

                fish_center_y = self.fish_y + 15
                player_bar_top = self.player_bar_y
                player_bar_bottom = self.player_bar_y + player_bar_h

                if player_bar_top < fish_center_y < player_bar_bottom:
                    self.catch_progress += self.catch_rate * dt
                else:
                    self.catch_progress -= self.penalty_rate * dt
                self.catch_progress = max(0, min(self.catch_progress, 1.0))

                if self.catch_progress >= 1.0:
                    running_minigame = False
                    self.battle_outcome = True
                elif self.catch_progress <= 0:
                    running_minigame = False
                    self.battle_outcome = False

            # Drawing
            self.screen_surface.fill(BLACK) # Default background for minigame states
            if self.minigame_state == 'QTE':
                qte_timer_ratio = self.qte_timer_current / self.qte_timer_max if self.qte_timer_max > 0 else 0
                draw_qte_screen(self.screen_surface, self.qte_key_display, qte_timer_ratio)
            elif self.minigame_state == 'BATTLE':
                fish_name_display = self.current_item.name if self.current_item else "Unknown Fish"
                draw_battle_screen(self.screen_surface, self.fish_y, self.player_bar_y, self.catch_progress, fish_name_display)
            
            pygame.display.flip()
        
        return self.battle_outcome 