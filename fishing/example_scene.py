import pygame
from .fishing_minigame import FishingMinigame

class FishingScene:
    def __init__(self, screen: pygame.Surface, font_path: str):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Create fishing minigame instance
        self.fishing_minigame = FishingMinigame(screen, font_path)
        
        # Colors - Terminal style
        self.BACKGROUND = (20, 20, 40)
        self.GRID_COLOR = (40, 40, 60)
        
    def draw_background(self):
        # Fill with dark background color
        self.screen.fill(self.BACKGROUND)
        
        # Draw terminal-style grid lines
        grid_spacing = 20
        
        # Draw horizontal grid lines
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.width, y), 1)
        
        # Draw vertical grid lines
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.height), 1)
    
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
        
        scene.update()
        scene.draw()
        pygame.display.flip()
        clock.tick(60)
    
    return scene.fishing_minigame.inventory 