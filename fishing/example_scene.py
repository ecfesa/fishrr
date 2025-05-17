import pygame
from .fishing_minigame import FishingMinigame
from utils.txtlib import Text, BEGIN, END, COLOR, BOLD

class FishingScene:
    def __init__(self, screen: pygame.Surface, font_path: str):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Create fishing minigame instance
        print("Creating fishing minigame instance")
        self.fishing_minigame = FishingMinigame(screen, font_path)
        
        # Create text renderer
        self.info_text = Text((self.width, 40), font_path, 24)
        self.info_text.background_color = (0, 0, 0, 0)  # Transparent background
        
        # Colors - Terminal style
        self.BACKGROUND = (20, 20, 40)
        self.GRID_COLOR = (40, 40, 60)
        self.TEXT_COLOR = (180, 180, 220)

        self.background = pygame.Surface((self.width, self.height))
        
    def draw_background(self):
        # Fill with dark background color
        self.screen.fill(self.BACKGROUND)
            
        # Draw info text at the bottom
        self.info_text.clear()
        self.info_text.html("SPACE to start fishing | ESC to exit")
        self.info_text.add_style(0, len("SPACE to start fishing | ESC to exit"), COLOR, self.TEXT_COLOR)
        self.info_text.update()
        
        text_rect = self.info_text.area.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(self.info_text.area, text_rect)
    
    def update(self):
        self.fishing_minigame.update()
    
    def draw(self):
        self.draw_background()
        self.fishing_minigame.draw()
    
    def handle_event(self, event: pygame.event.Event):
        self.fishing_minigame.handle_event(event)

def run_fishing_scene(screen: pygame.Surface, font_path: str):
    """
    Run the fishing minigame scene.
    
    Args:
        screen: The pygame surface to render to
        font_path: Path to the font file to use
    
    Returns:
        The list of caught items when the scene ends
    """
    clock = pygame.time.Clock()
    scene = FishingScene(screen, font_path)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            scene.handle_event(event)
        
        scene.draw()
        scene.update()
        pygame.display.flip()
        clock.tick(60)
    
    return scene.fishing_minigame.inventory 