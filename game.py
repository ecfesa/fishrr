import pygame
import sys
from terminal import Terminal
from sidebar import Sidebar
from states import State, MainMenu
from world import Island
from minigames import FishingMinigame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, FPS

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.running = True
        
        # Create sidebar (200px width)
        self.sidebar = Sidebar(0, 0, 200, WINDOW_HEIGHT)
        
        # Create terminal (remaining width)
        self.terminal = Terminal(
            200, 0,  # Position after sidebar
            WINDOW_WIDTH - 200, WINDOW_HEIGHT  # Remaining space
        )
        
        # Set up islands
        self.setup_islands()
        
        # Set initial state to main menu
        self.state = MainMenu(self)

    def setup_islands(self):
        """Configura as ilhas do jogo"""
        self.islands = {}
        
        # Primeira ilha - Fish Island
        island1_todo = [
            "Get a fishing rod",
            "Get fishing line",
            "Get can (worms)",
            "Get worms",
            "Get bucket",
            "Fish 5 fish",
            "Get coordinates for the next island"
        ]
        
        # Inicializa minigame de pesca (o island será associado depois)
        fishing_minigame = FishingMinigame(self, 1, rods=1, worms=5)
        
        island1 = Island(
            id=1,
            name="Fish Island",
            color=(70, 130, 180),  # Azul cadete para o terminal
            minigame=fishing_minigame,
            password="rod123",
            todo=island1_todo
        )
        
        # Agora que o island1 foi criado, podemos associá-lo ao minigame
        fishing_minigame.island = island1
        
        self.islands[1] = island1
        
        # Poderíamos adicionar mais ilhas aqui...
        # Por exemplo:
        # island2_todo = ["Get wood (boat)", "Get sails (boat)", "Craft a boat", "Find navigation map", "Navigate to next island"]
        # island2_minigame = CraftingMinigame(self, 2)
        # island2 = Island(2, "Craft Island", (100, 160, 100), island2_minigame, "craft456", island2_todo)
        # island2_minigame.island = island2
        # self.islands[2] = island2

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000  # delta time em segundos
            self.state.handle_events()
            self.state.update(dt)
            self.state.render(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
        
    def change_state(self, new_state: State):
        """Muda o estado atual do jogo"""
        self.state = new_state