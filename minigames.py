import pygame
from constants import WHITE, FONT

class Minigame:
    """Superclasse genérica de minigame."""
    def __init__(self, game, island_id):
        self.game = game
        self.island_id = island_id
        self.island = None  # Será associado depois

    def start(self):
        """Chama cena ou lógica específica do minigame."""
        raise NotImplementedError

class FishingMinigame(Minigame):
    def __init__(self, game, island_id, rods=1, worms=5):
        super().__init__(game, island_id)
        self.rods = rods
        self.worms = worms
        self.hooked_fish = 0
        self.required_fish = 5
        self.font = pygame.font.Font(FONT, 24)
        
        # Estado dos elementos visuais
        self.fishing_rod_position = (400, 400)
        self.fish_positions = []
        self.bite_status = False
        self.timer = 0
        self.bite_window = 0
        
        # Sons (usando placeholders por enquanto)
        # self.cast_sound = pygame.mixer.Sound('sounds/cast.wav')
        # self.splash_sound = pygame.mixer.Sound('sounds/splash.wav')
        # self.catch_sound = pygame.mixer.Sound('sounds/catch.wav')

    def start(self):
        # Interface para o minigame de pesca
        screen = self.game.screen
        clock = self.game.clock
        
        running = True
        self.hooked_fish = 0
        game_state = "ready"  # estados: ready, casting, waiting, reeling
        
        # Preparar tela
        screen.fill((0, 100, 150))  # Fundo azul para o oceano
        pygame.display.flip()
        
        # Loop do minigame
        while running and self.hooked_fish < self.required_fish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                    return self.island.password
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # Lógica de pesca com base no estado atual
                    if event.key == pygame.K_SPACE:
                        if game_state == "ready":
                            # Lançar a isca
                            game_state = "casting"
                            # self.cast_sound.play()
                            self.timer = 0
                        elif game_state == "waiting" and self.bite_status:
                            # Puxar o peixe quando ele morder
                            game_state = "reeling"
                            # self.catch_sound.play()
                            self.hooked_fish += 1
                            game_state = "ready"  # Volta ao início
                    
            # Atualizar o jogo com base no estado
            if game_state == "casting":
                self.timer += 1
                if self.timer > 30:  # Esperar meio segundo
                    game_state = "waiting"
                    # self.splash_sound.play()
                    self.timer = 0
                    
            elif game_state == "waiting":
                self.timer += 1
                # A cada poucos segundos, gerar uma chance de mordida
                if self.timer % 60 == 0:
                    self.bite_status = pygame.time.get_ticks() % 3 == 0  # 33% de chance
                    self.bite_window = 45  # Janela de 45 frames para pegar o peixe
                
                # Se o peixe estiver mordendo, diminuir a janela
                if self.bite_status:
                    self.bite_window -= 1
                    if self.bite_window <= 0:
                        self.bite_status = False
                        game_state = "ready"  # Perdeu a chance
            
            # Renderizar a tela
            screen.fill((0, 100, 150))  # Fundo azul para o oceano
            
            # Desenhar a água
            pygame.draw.rect(screen, (0, 80, 120), (0, 400, 1280, 320))
            
            # Desenhar uma vara de pescar simples
            rod_x, rod_y = 640, 320
            pygame.draw.line(screen, (139, 69, 19), (rod_x, rod_y), (rod_x + 100, rod_y - 50), 3)
            pygame.draw.line(screen, (139, 69, 19), (rod_x + 100, rod_y - 50), (rod_x + 100, rod_y + 100), 2)
            
            # Desenhar linha de pesca
            if game_state in ["waiting", "reeling"]:
                pygame.draw.line(screen, WHITE, (rod_x + 100, rod_y - 50), (rod_x + 150, rod_y + 200), 1)
                
                # Desenhar isca/boia
                pygame.draw.circle(screen, (255, 0, 0), (rod_x + 150, rod_y + 200), 5)
                
                # Se um peixe estiver mordendo, desenhar uma animação
                if self.bite_status:
                    for i in range(3):
                        radius = (pygame.time.get_ticks() // 100) % 5 + 3
                        pygame.draw.circle(
                            screen, 
                            WHITE, 
                            (rod_x + 150 + i*5, rod_y + 200 + i*3), 
                            radius, 
                            1
                        )
            
            # Desenhar contador de peixes
            fish_text = self.font.render(f"Fish caught: {self.hooked_fish}/{self.required_fish}", True, WHITE)
            screen.blit(fish_text, (50, 50))
            
            # Instruções
            if game_state == "ready":
                instruction = self.font.render("Press SPACE to cast your line", True, WHITE)
            elif game_state == "casting":
                instruction = self.font.render("Casting...", True, WHITE)
            elif game_state == "waiting":
                if self.bite_status:
                    instruction = self.font.render("BITE! Press SPACE to reel!", True, (255, 255, 0))
                else:
                    instruction = self.font.render("Waiting for fish...", True, WHITE)
            elif game_state == "reeling":
                instruction = self.font.render("Reeling...", True, WHITE)
            
            screen.blit(instruction, (50, 100))
            
            # Verificar se o objetivo foi atingido
            if self.hooked_fish >= self.required_fish:
                success_text = self.font.render("Minigame completed! Returning to game...", True, (255, 255, 0))
                screen.blit(success_text, (350, 150))
            
            # Instrução para sair
            exit_text = self.font.render("Press ESC to exit", True, WHITE)
            screen.blit(exit_text, (1000, 50))
            
            pygame.display.flip()
            clock.tick(self.game.fps)
            
            # Se terminou o minigame, facilitar a saída
            if self.hooked_fish >= self.required_fish:
                pygame.event.clear()  # Limpar eventos acumulados
        
        # Ao finalizar, marca a tarefa como completa se pegou peixes suficientes
        if self.hooked_fish >= self.required_fish:
            self.island.complete_task("Fish 5 fish")
        
        # Retorna a senha se completou todas as tarefas
        password = self.island.unlock_next()
        return password
