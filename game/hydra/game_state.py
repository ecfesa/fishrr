import pygame
import sys
import random
from game.hydra.constants import *
from game.hydra.entities import WindGust, MovingObject, Hydra
from game.hydra.renderer import draw_terminal_border, draw_water, draw_bar, draw_boat, draw_meters, draw_status_line, draw_gust_feedback
from game.hydra.ui import draw_menu, draw_pause_menu, draw_victory_screen, draw_game_over
from game.hydra.audio import sounds, play_sound
from game.assets import get_font

class GameState:
    """Class to manage the game state and transitions"""
    
    def __init__(self, screen, clock, hydra_game_main_instance):
        self.screen = screen
        self.clock = clock
        self.hydra_game_main_instance = hydra_game_main_instance
        self.current_state = "menu"
        self.victory_sound_played = False
        self.game_over_flag = False
        
        # Game variables
        self.reset_game_variables()
    
    def reset_game_variables(self):
        """Reset all game variables to their initial state"""
        # Bar position: 0 = top, 1 = right, 2 = bottom, 3 = left
        self.bar_position = 0
        self.game_over_flag = False

        # Tutorial variables - NEW SECTION
        self.tutorial_active = True
        self.tutorial_timer = 300  # 5 seconds at 60fps
        self.tutorial_messages = [
            {"text": "Use ARROW KEYS to position the bar in the CONTROL ZONE", "position": (WIDTH // 2, SQUARE_POS[1] - 40)},
            {"text": "Position the bar on the OPPOSITE SIDE of incoming wind", "position": (WIDTH // 2, SQUARE_POS[1] - 70)},
            {"text": "Watch for RED WARNING INDICATORS on the outer zone", "position": (WIDTH // 2, SQUARE_POS[1] + SQUARE_SIZE + 30)},
        ]

        # Animation variables
        self.glow_value = 0
        self.glow_direction = 1
        self.water_offset = 0
        self.boat_offset = 0

        # Physics variables 
        self.boat_acceleration = 0  # Current acceleration
        self.boat_speed = 0  # Current speed
        self.current_distance = 0  # Distance traveled so far

        # Current difficulty stage
        self.current_stage = "EASY"
        
        # Difficulty parameters based on stage
        self.difficulty_factor = 0.8
        self.gust_frequency_modifier = 0.8
        self.gust_pattern_predictability = 0.9
        self.warning_time_modifier = 1.6
        self.wobble_intensity = 0.4

        # Hydras chasing the boat
        self.hydras = []
        
        # Hydra spawn parameters
        self.initial_hydra_spawn_distance = 15000
        self.next_hydra_spawn = self.initial_hydra_spawn_distance
        self.hydra_spawn_distance_range = (2000, 4000)
        self.max_active_hydras = 3
        
        # Debugging flag
        self.debug_mode = False
        self.debug_frame_counter = 0

        # Water ripples
        self.ripples = []
        for _ in range(5):
            self.ripples.append({
                'x': random.randint(SQUARE_POS[0], SQUARE_POS[0] + SQUARE_SIZE),
                'y': random.randint(SQUARE_POS[1], SQUARE_POS[1] + SQUARE_SIZE),
                'radius': random.randint(5, 15),
                'speed': random.uniform(0.1, 0.2)
            })

        # Wind gusts
        self.wind_gusts = []
        self.inactive_gusts = []
        self.flash_timer = 0
        self.gust_timer = 0
        self.next_gust_direction = None
        
        # Minimum time between gusts
        self.min_gust_spacing = 30
        self.time_since_last_gust = self.min_gust_spacing

        # Moving objects
        self.moving_objects = []
        for i in range(8):
            self.moving_objects.append(MovingObject())

        # Result message
        self.result_message = None
        self.result_timer = 0
        
        # Stage transition announcement
        self.stage_announcement = None
        self.stage_announcement_timer = 0
        
        # Hydra warning system
        self.hydra_warning_active = False
        self.hydra_warning_timer = 0
        self.hydra_warning_text = "!!! HYDRA APPROACHING !!!"
        
        # Pause state
        self.paused = False
        
        # Sound reset
        self.volume_reset_pending = False
        self.original_calm_volume = sounds['startGame'].get_volume() if 'startGame' in sounds else 0.2
    
    def handle_events(self, events):
        """Handle pygame events based on current state"""
        for event in events:
            if event.type == pygame.QUIT:
                if self.hydra_game_main_instance:
                    self.hydra_game_main_instance.is_running = False
                    self.hydra_game_main_instance.game_over = True
                return
                
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
                    
            elif event.type == pygame.USEREVENT + 1:
                if 'startGame' in sounds:
                    sounds['startGame'].set_volume(self.original_calm_volume)
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
    
    def handle_keydown(self, event):
        """Handle key down events based on current state"""
        if self.current_state == "menu":
            if event.key == pygame.K_RETURN:
                play_sound('startGame')
                self.current_state = "game"
                self.reset_game_variables()
                self.game_over_flag = False
            elif event.key == pygame.K_ESCAPE:
                if self.hydra_game_main_instance:
                    self.hydra_game_main_instance.is_running = False
                    self.hydra_game_main_instance.game_over = True
                
        elif self.current_state == "game":
            if event.key == pygame.K_UP:
                self.bar_position = 0  # Top
            elif event.key == pygame.K_RIGHT:
                self.bar_position = 1  # Right
            elif event.key == pygame.K_DOWN:
                self.bar_position = 2  # Bottom
            elif event.key == pygame.K_LEFT:
                self.bar_position = 3  # Left
            elif event.key == pygame.K_ESCAPE:
                if self.paused:
                    self.current_state = "menu"
                else:
                    self.paused = True
            elif event.key == pygame.K_SPACE:
                if self.paused:
                    self.paused = False
                    
        elif self.current_state == "victory":
            self.current_state = "menu"
            self.game_over_flag = True
            if self.hydra_game_main_instance:
                self.hydra_game_main_instance.game_over = True
    
    def update(self):
        """Update game state based on current state"""
        if self.current_state == "menu":
            self.update_menu()
        elif self.current_state == "game":
            self.update_game()
        elif self.current_state == "victory":
            self.update_victory()
    
    def update_menu(self):
        """Update menu state"""
        self.victory_sound_played = False
    
    def update_victory(self):
        """Update victory state"""
        if not self.victory_sound_played:
            play_sound('victory')
            self.victory_sound_played = True
    
    def update_game(self):
        """Update game state"""
        if self.paused:
            return
            
        if self.result_message:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.current_state = "menu"
                self.game_over_flag = True
                if self.hydra_game_main_instance:
                    self.hydra_game_main_instance.game_over = True
                return
            
        if self.tutorial_active:
            self.tutorial_timer -= 1
            if self.tutorial_timer <= 0:
                self.tutorial_active = False
            
        self.glow_value += 0.1 * self.glow_direction
        if self.glow_value >= 3.14 or self.glow_value <= 0:
            self.glow_direction *= -1
        
        self.water_offset += 0.02
        self.boat_offset += 0.08
        
        self.update_physics()
        
        self.current_distance += self.boat_speed / 10
        
        self.current_distance = max(0, self.current_distance)
        
        if self.current_distance >= TOTAL_DISTANCE:
            self.current_state = "victory"
            return
        
        self.update_difficulty_stage()
        
        if self.stage_announcement_timer > 0:
            self.stage_announcement_timer -= 1
        
        self.update_hydras()
        
        self.debug_frame_counter = (self.debug_frame_counter + 1) % 60
        
        self.update_wind_gusts()
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        if self.flash_timer == 0 and self.inactive_gusts:
            self.inactive_gusts = []
        
        for obj in self.moving_objects:
            obj.update(self.boat_speed)
    
    def update_physics(self):
        """Update physics variables"""
        speed_factor = 1.0 + (abs(self.boat_speed) / MAX_SPEED) * 0.5
        self.boat_acceleration *= (1 - ACCELERATION_DECAY * speed_factor)
        
        if abs(self.boat_speed) > MAX_SPEED * 0.7:
            jitter_base = (abs(self.boat_speed) - MAX_SPEED * 0.7) / (MAX_SPEED * 0.3) * 0.1
            jitter_amount = jitter_base * self.difficulty_factor
            self.boat_acceleration += random.uniform(-jitter_amount, jitter_amount)
        
        accel_effect = self.boat_acceleration
        if abs(self.boat_acceleration) > 1.0:
            exponent = 1.0 + (self.difficulty_factor - 1.0) * 0.2
            accel_sign = 1 if self.boat_acceleration > 0 else -1
            accel_effect = accel_sign * (1.0 + (abs(self.boat_acceleration) - 1.0) ** exponent)
        
        self.boat_speed += accel_effect
        
        drag_effect = DRAG * (1.0 + (abs(self.boat_speed) / MAX_SPEED)) * self.difficulty_factor
        if self.boat_speed > 0:
            self.boat_speed -= drag_effect
        elif self.boat_speed < 0:
            self.boat_speed += drag_effect
            
        self.boat_speed = max(MIN_SPEED, min(MAX_SPEED, self.boat_speed))
    
    def update_difficulty_stage(self):
        """Update difficulty parameters based on current distance"""
        EASY_THRESHOLD = TOTAL_DISTANCE / 3
        MEDIUM_THRESHOLD = TOTAL_DISTANCE * 2 / 3
        
        if self.current_distance < EASY_THRESHOLD:
            if self.current_stage != "EASY":
                self.current_stage = "EASY"
                self.stage_announcement = "NAVIGATION: CALM WATERS"
                self.stage_announcement_timer = 120
                calm_sound = sounds['startGame']
                self.original_calm_volume = calm_sound.get_volume()
                calm_sound.set_volume(0.1)
                calm_sound.play()
                pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                
            self.difficulty_factor = 0.8
            self.gust_frequency_modifier = 0.7
            self.gust_pattern_predictability = 0.95
            self.warning_time_modifier = 1.8
            self.wobble_intensity = 0.2
            self.min_gust_spacing = 50
            
        elif self.current_distance < MEDIUM_THRESHOLD:
            if self.current_stage != "MEDIUM":
                self.current_stage = "MEDIUM"
                self.stage_announcement = "WARNING: INCREASING TURBULENCE"
                self.stage_announcement_timer = 120
                play_sound('warning_turbulence')
                
            self.difficulty_factor = 1.1
            self.gust_frequency_modifier = 0.9
            self.gust_pattern_predictability = 0.7
            self.warning_time_modifier = 1.2
            self.wobble_intensity = 0.5
            self.min_gust_spacing = 40
            
        else:
            if self.current_stage != "HARD":
                self.current_stage = "HARD"
                self.stage_announcement = "DANGER: NAVIGATING STORM WATERS"
                self.stage_announcement_timer = 120
                play_sound('warning_storm')
                
            self.difficulty_factor = 1.4
            self.gust_frequency_modifier = 1.1
            self.gust_pattern_predictability = 0.5
            self.warning_time_modifier = 0.9
            self.wobble_intensity = 0.8
            self.min_gust_spacing = 35
    
    def update_hydras(self):
        """Update hydras and check for collisions"""
        closest_hydra_distance = float('inf')
        for hydra in self.hydras[:]:
            defeated = hydra.update(self.boat_speed, self.difficulty_factor, self.debug_mode)
            
            if self.debug_mode and self.debug_frame_counter % 60 == 0:
                print(f"Hydra: pos={hydra.distance:.1f}, boat={self.current_distance:.1f}, diff={self.current_distance-hydra.distance:.1f}, speed={hydra.speed:.1f}")
            
            if defeated:
                if self.debug_mode:
                    print(f"Hydra defeated and removed!")
                self.hydras.remove(hydra)
                continue
                
            distance_to_boat = self.current_distance - hydra.distance
            
            if distance_to_boat < closest_hydra_distance:
                closest_hydra_distance = distance_to_boat
                
            if distance_to_boat < 100:
                if self.debug_mode:
                    print(f"GAME OVER: Hydra caught the boat! Distance: {distance_to_boat:.1f}")
                self.result_message = "DEVOURED BY HYDRA!"
                self.result_timer = 180
                play_sound('gameOver')
                return
        
        if len(self.hydras) < self.max_active_hydras and self.current_distance > self.next_hydra_spawn:
            spawn_distance = self.current_distance - random.randint(self.hydra_spawn_distance_range[0], self.hydra_spawn_distance_range[1])
            new_hydra = Hydra(spawn_distance)
            self.hydras.append(new_hydra)
            play_sound('hydra')
            if self.debug_mode:
                print(f"New hydra spawned at distance {new_hydra.distance}, boat at {self.current_distance}, difference: {self.current_distance - new_hydra.distance}")
            self.next_hydra_spawn = self.current_distance + random.randint(10000, 20000)
        
        if closest_hydra_distance < 1000 and not self.hydra_warning_active:
            self.hydra_warning_active = True
            self.hydra_warning_timer = 120
            play_sound('hydra')
        
        if self.hydra_warning_timer > 0:
            self.hydra_warning_timer -= 1
            
        if self.hydra_warning_timer <= 0 and self.hydra_warning_active:
            self.hydra_warning_active = False
    
    def update_wind_gusts(self):
        """Update wind gusts"""
        self.time_since_last_gust += 1
        
        self.gust_timer += 1
        
        effective_interval = max(
            GUST_MIN_INTERVAL,
            GUST_INTERVAL_BASE / self.gust_frequency_modifier - (abs(self.boat_speed) / 2) - (abs(self.boat_acceleration) * 20 * self.difficulty_factor)
        )
        
        if self.gust_timer >= effective_interval and self.time_since_last_gust >= self.min_gust_spacing:
            any_warnings_active = any(gust.warning for gust in self.wind_gusts)
            
            if not any_warnings_active:
                accel_threshold = MAX_ACCELERATION * 0.6 * self.gust_pattern_predictability
                
                if abs(self.boat_acceleration) < accel_threshold:
                    if self.next_gust_direction is None:
                        self.next_gust_direction = random.randint(0, 3)
                    else:
                        if random.random() < (1 - self.gust_pattern_predictability):
                            self.next_gust_direction = random.randint(0, 3)
                        else:
                            if random.random() < 0.2:
                                self.next_gust_direction = (self.next_gust_direction + 2) % 4
                            else:
                                self.next_gust_direction = (self.next_gust_direction + 1) % 4
                else:
                    randomness_factor = min(1.0, (abs(self.boat_acceleration) - accel_threshold) / (MAX_ACCELERATION - accel_threshold))
                    randomness_factor *= (2 - self.gust_pattern_predictability)
                    
                    if random.random() < randomness_factor:
                        self.next_gust_direction = random.randint(0, 3)
                    else:
                        self.next_gust_direction = (self.next_gust_direction + random.choice([1, 2, 3])) % 4
                        
                new_gust = WindGust(self.next_gust_direction, self.boat_acceleration * self.wobble_intensity, self.difficulty_factor)
                
                new_gust.warning_time = int(new_gust.warning_time * self.warning_time_modifier)
                
                self.wind_gusts.append(new_gust)
                
                self.gust_timer = 0
                self.time_since_last_gust = 0
        
        for gust in self.wind_gusts[:]:
            accel_change = gust.update(self.bar_position, self.boat_speed)
            self.boat_acceleration += accel_change
            
            self.boat_acceleration = max(-MAX_ACCELERATION, min(MAX_ACCELERATION, self.boat_acceleration))
            
            if not gust.active and (gust.collected or gust.blocked or gust.missed):
                self.inactive_gusts.append(gust)
                self.flash_timer = 15
                self.wind_gusts.remove(gust)
            elif not gust.active:
                self.wind_gusts.remove(gust)
    
    def draw(self):
        """Draw the current game state"""
        if self.current_state == "menu":
            draw_menu(self.screen)
        elif self.current_state == "game":
            self.draw_game()
        elif self.current_state == "victory":
            draw_victory_screen(self.screen)
        
        # pygame.display.flip() # Removed: Main game loop should handle display updates
        # self.clock.tick(60) # Removed: Main game loop should handle clock ticking
    
    def draw_game(self):
        """Draw the game state"""
        if self.paused:
            draw_pause_menu(self.screen)
            return
        
        if self.result_message:
            draw_game_over(self.screen, self.result_message)
            return
        
        self.screen.fill(BLACK)
        
        draw_terminal_border(self.screen, self.boat_speed, self.boat_acceleration, self.glow_value)
        
        draw_water(self.screen, self.ripples, self.water_offset)
        
        for obj in self.moving_objects:
            obj.draw(self.screen)
        
        pygame.draw.rect(self.screen, DARK_GREEN, (OUTER_SQUARE_POS[0], OUTER_SQUARE_POS[1], OUTER_SQUARE_SIZE, OUTER_SQUARE_SIZE), 1)
        
        pygame.draw.rect(self.screen, GREEN, (SQUARE_POS[0], SQUARE_POS[1], SQUARE_SIZE, SQUARE_SIZE), 1)
        
        for gust in self.wind_gusts:
            gust.draw(self.screen)
        
        if self.inactive_gusts and self.flash_timer > 0:
            draw_gust_feedback(self.screen, self.inactive_gusts, self.flash_timer)
        
        draw_bar(self.screen, self.bar_position, self.glow_value)
        
        draw_boat(self.screen, self.boat_offset)
        
        progress_rect = draw_meters(self.screen, self.boat_speed, self.boat_acceleration, self.current_distance, self.glow_value)
        
        if self.debug_mode and self.debug_frame_counter % 60 == 0:
            print(f"Drawing {len(self.hydras)} hydras. Progress rect: {progress_rect}")
            
        for hydra in self.hydras:
            hydra.draw(self.screen, self.current_distance, TOTAL_DISTANCE, progress_rect, self.debug_mode)
        
        draw_status_line(self.screen, self.bar_position)
        
        if self.tutorial_active:
            self.draw_tutorial()
        
        if self.stage_announcement and self.stage_announcement_timer > 0:
            alpha = min(255, self.stage_announcement_timer * 4)
            font = get_font(24)
            announcement_surf = font.render(self.stage_announcement, True, 
                                        YELLOW if self.current_stage == "MEDIUM" else
                                        RED if self.current_stage == "HARD" else
                                        GREEN)
            
            temp_surf = pygame.Surface((announcement_surf.get_width(), announcement_surf.get_height()))
            temp_surf.fill(BLACK)
            temp_surf.set_alpha(255 - alpha)
            
            self.screen.blit(announcement_surf, 
                        (WIDTH // 2 - announcement_surf.get_width() // 2, 
                         HEIGHT // 3 - announcement_surf.get_height() // 2))
            
            self.screen.blit(temp_surf, 
                        (WIDTH // 2 - announcement_surf.get_width() // 2, 
                         HEIGHT // 3 - announcement_surf.get_height() // 2))
        
        if self.hydra_warning_active:
            if (self.hydra_warning_timer // 5) % 2 == 0:
                font = get_font(26)
                warning_surf = font.render(self.hydra_warning_text, True, RED)
                
                warning_bg = pygame.Surface((warning_surf.get_width() + 20, warning_surf.get_height() + 10))
                warning_bg.fill(BLACK)
                warning_bg.set_alpha(200)
                self.screen.blit(warning_bg, (
                    WIDTH // 2 - (warning_surf.get_width() + 20) // 2,
                    BORDER_MARGIN + 35
                ))
                
                self.screen.blit(warning_surf, (
                    WIDTH // 2 - warning_surf.get_width() // 2,
                    BORDER_MARGIN + 40
                ))
    
    def draw_tutorial(self):
        """Draw the tutorial instructions with fading effect"""
        fade_start = self.tutorial_timer / 2
        if self.tutorial_timer <= fade_start:
            alpha = int(255 * (self.tutorial_timer / fade_start))
        else:
            alpha = 255
            
        font = get_font(18)
        
        def draw_arrow(direction, pos, color):
            """Draw an arrow in the specified direction"""
            x, y = pos
            size = 12
            
            if direction == 0:  # Up
                points = [(x, y-size), (x-size, y), (x+size, y)]
            elif direction == 1:  # Right
                points = [(x+size, y), (x, y-size), (x, y+size)]
            elif direction == 2:  # Down
                points = [(x, y+size), (x-size, y), (x+size, y)]
            elif direction == 3:  # Left
                points = [(x-size, y), (x, y-size), (x, y+size)]
                
            arrow_surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            pygame.draw.polygon(arrow_surf, (*color, alpha), [(p[0]-x+size*1.5, p[1]-y+size*1.5) for p in points])
            
            self.screen.blit(arrow_surf, (x-size*1.5, y-size*1.5))
            
        highlight_surf = pygame.Surface((SQUARE_SIZE+20, SQUARE_SIZE+20), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (0, 255, 0, min(40, alpha//6)), (0, 0, SQUARE_SIZE+20, SQUARE_SIZE+20), 2)
        self.screen.blit(highlight_surf, (SQUARE_POS[0]-10, SQUARE_POS[1]-10))
        
        for message in self.tutorial_messages:
            text = message["text"]
            position = message["position"]
            
            text_surf = font.render(text, True, GREEN)
            
            bg_width = text_surf.get_width() + 20
            bg_height = text_surf.get_height() + 10
            bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, min(180, alpha - 75)))
            
            self.screen.blit(bg_surf, (position[0] - bg_width//2, position[1] - bg_height//2))
            
            text_alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            text_alpha_surf.fill((255, 255, 255, alpha))
            text_surf.blit(text_alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            self.screen.blit(text_surf, (position[0] - text_surf.get_width()//2, position[1] - text_surf.get_height()//2))
            
        arrow_positions = [
            (SQUARE_POS[0] + SQUARE_SIZE//2, SQUARE_POS[1] - 20),  # Top
            (SQUARE_POS[0] + SQUARE_SIZE + 20, SQUARE_POS[1] + SQUARE_SIZE//2),  # Right
            (SQUARE_POS[0] + SQUARE_SIZE//2, SQUARE_POS[1] + SQUARE_SIZE + 20),  # Bottom
            (SQUARE_POS[0] - 20, SQUARE_POS[1] + SQUARE_SIZE//2)   # Left
        ]
        
        for i, pos in enumerate(arrow_positions):
            color = (0, 255, 0) if i == self.bar_position else (0, 180, 0)
            draw_arrow(i, pos, color)
        
        if alpha > 150:
            help_font = get_font(14)
            help_text = "Press ESC to pause"
            help_surf = help_font.render(help_text, True, (0, 180, 0))
            self.screen.blit(help_surf, (WIDTH - help_surf.get_width() - 20, HEIGHT - help_surf.get_height() - 15)) 