import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, DARK_GRAY, FONT

class State:
    """Superclasse para os diferentes 'estados' do jogo."""
    def __init__(self, game):
        self.game = game

    def handle_events(self):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass

class MainMenu(State):
    """Menu inicial com opção de iniciar, carregar, sair."""
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Start", "Load", "Quit"]
        self.selected = 0
        self.font = pygame.font.Font(FONT, 36)
        self.title_font = pygame.font.Font(FONT, 48)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()

    def select_option(self):
        if self.options[self.selected] == "Start":
            # Iniciar com a primeira ilha
            first_island = self.game.islands[1]
            self.game.change_state(IslandScene(self.game, first_island))
        elif self.options[self.selected] == "Load":
            # Implementar carregamento de jogo
            pass
        elif self.options[self.selected] == "Quit":
            self.game.running = False

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        
        # Desenhar título
        title = self.title_font.render("Fishrr", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        screen.blit(title, title_rect)
        
        # Desenhar opções
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected else DARK_GRAY
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 60))
            screen.blit(text, text_rect)

class IslandScene(State):
    """
    Cena de exploração de uma ilha:
    terminal + TODO list + navegação por comandos.
    """
    def __init__(self, game, island):
        super().__init__(game)
        self.island = island
        self.sidebar = game.sidebar
        self.terminal = game.terminal
        
        # Configurar ilha atual
        self.configure_island()

    def configure_island(self):
        # Atualizar cor do terminal com base na ilha
        self.terminal.background_color = self.island.color
        
        # Atualizar comandos disponíveis na sidebar
        self.sidebar.commands = ["fish", "help", "todo", "man", "get", "use", "info"]
        
        # Adicionar comandos específicos da ilha ao terminal
        self.terminal.commands["fish"] = self.cmd_fish
        self.terminal.commands["help"] = self.cmd_help
        self.terminal.commands["todo"] = self.cmd_todo
        self.terminal.commands["man"] = self.cmd_man
        self.terminal.commands["get"] = self.cmd_get
        self.terminal.commands["use"] = self.cmd_use
        self.terminal.commands["info"] = self.cmd_info
        self.terminal.commands["menu"] = self.cmd_menu
        
        # Configurar a lista de tarefas na sidebar
        self.sidebar.set_tasks(self.island.get_formatted_tasks(), f"{self.island.name} Tasks")
        
        # Mostrar mensagem de boas-vindas
        welcome_msg = f"Welcome to {self.island.name}!"
        self.terminal.output_lines.append(welcome_msg)
        self.terminal.output_lines.append("-" * len(welcome_msg))
        self.terminal.output_lines.append("Type 'help' to see available commands.")
        self.terminal.output_lines.append("Type 'todo' to see your task list.")
    
    def cmd_get(self, *args):
        """Comando para pegar itens"""
        if not args:
            return "Usage: get <item>"
            
        item = " ".join(args).lower()
        
        # Itens relacionados à pesca
        fishing_items = {
            "rod": "Get a fishing rod",
            "fishing rod": "Get a fishing rod",
            "line": "Get fishing line",
            "fishing line": "Get fishing line", 
            "worms": "Get worms",
            "can": "Get can (worms)",
            "bucket": "Get bucket"
        }
        
        # Itens relacionados ao barco
        boat_items = {
            "wood": "Get wood (boat)",
            "sails": "Get sails (boat)"
        }
        
        if item in fishing_items:
            task = fishing_items[item]
            if self.island.complete_task(task):
                # Atualizar sidebar
                self.sidebar.set_tasks(self.island.get_formatted_tasks(), f"{self.island.name} Tasks")
                return f"You got the {item}!"
            else:
                # Ver se já foi concluído
                if task in self.island.task_progress.get_completed_tasks():
                    return f"You already have the {item}."
                else:
                    return f"Couldn't find {item} here."
        elif item in boat_items:
            task = boat_items[item]
            if self.island.complete_task(task):
                # Atualizar sidebar
                self.sidebar.set_tasks(self.island.get_formatted_tasks(), f"{self.island.name} Tasks")
                return f"You got the {item} for your boat!"
            else:
                # Ver se já foi concluído
                if task in self.island.task_progress.get_completed_tasks():
                    return f"You already have the {item}."
                else:
                    return f"Couldn't find {item} here."
        elif item == "coordinates":
            # Verificar se já pescou peixes suficientes
            fish_task = "Fish 5 fish"
            if fish_task in self.island.task_progress.get_completed_tasks():
                if self.island.complete_task("Get coordinates for the next island"):
                    self.sidebar.set_tasks(self.island.get_formatted_tasks(), f"{self.island.name} Tasks")
                    return f"You found coordinates to the next island! Password: {self.island.password}"
                else:
                    if "Get coordinates for the next island" in self.island.task_progress.get_completed_tasks():
                        return f"You already have the coordinates. Password: {self.island.password}"
                    else:
                        return "Something went wrong."
            else:
                return "You need to catch more fish before you can get coordinates."
        else:
            return f"There's no {item} here."
            
    def cmd_use(self, *args):
        """Comando para usar itens"""
        if not args:
            return "Usage: use <item>"
            
        item = " ".join(args).lower()
        
        if item in ["rod", "fishing rod"]:
            # Verificar se tem a vara de pesca
            if "Get a fishing rod" in self.island.task_progress.get_completed_tasks():
                return self.cmd_fish()
            else:
                return "You don't have a fishing rod yet. Try using 'get rod' first."
        else:
            return f"You can't use {item} right now."
    
    def cmd_info(self, *args):
        """Fornece informações sobre a ilha"""
        completion = self.island.get_completion_status()
        
        return "\n".join([
            f"Island: {self.island.name}",
            f"ID: {self.island.id}",
            f"Completion: {completion:.1f}%",
            f"Tasks completed: {len(self.island.task_progress.get_completed_tasks())}/{len(self.island.todo)}",
            f"Current objective: Catch fish and find coordinates to the next island."
        ])
        
    def cmd_menu(self, *args):
        """Retorna ao menu principal"""
        self.game.change_state(MainMenu(self.game))
        return "Returning to main menu..."

    def cmd_fish(self, *args):
        """Inicia o minigame de pesca"""
        # Verificar se tem a vara de pesca
        if "Get a fishing rod" not in self.island.task_progress.get_completed_tasks():
            return "You don't have a fishing rod yet. Try using 'get rod' first."
            
        # Verificar se tem linha de pesca
        if "Get fishing line" not in self.island.task_progress.get_completed_tasks():
            return "You need fishing line. Try using 'get line' first."
            
        # Verificar se tem minhocas
        if "Get worms" not in self.island.task_progress.get_completed_tasks():
            return "You need some bait. Try using 'get worms' first."
        
        self.terminal.output_lines.append("Starting fishing minigame...")
        password = self.island.minigame.start()
        
        # Marcar a tarefa de pescar como concluída se o jogador pegou peixes suficientes
        if self.island.minigame.hooked_fish >= self.island.minigame.required_fish:
            self.island.complete_task("Fish 5 fish")
            self.sidebar.set_tasks(self.island.get_formatted_tasks(), f"{self.island.name} Tasks")
            
        return f"Fishing complete! You caught {self.island.minigame.hooked_fish} fish."

    def cmd_help(self, *args):
        """Mostra comandos disponíveis"""
        return "\n".join([
            "Available commands:",
            "- fish: Start fishing minigame",
            "- todo: Show tasks for this island",
            "- man <page>: Show manual page",
            "- get <item>: Pick up an item",
            "- use <item>: Use an item",
            "- info: Show island information", 
            "- menu: Return to main menu",
            "- help: Show this help message"
        ])
    
    def cmd_todo(self, *args):
        """Mostra a lista de tarefas da ilha"""
        formatted_tasks = self.island.get_formatted_tasks()
        completion = self.island.get_completion_status()
        
        result = [
            f"Tasks for {self.island.name} ({completion:.1f}% complete):"
        ]
        
        for task in formatted_tasks:
            result.append(f"- {task}")
            
        # Atualizar também a sidebar
        self.sidebar.set_tasks(formatted_tasks, f"{self.island.name} Tasks")
            
        return "\n".join(result)
    
    def cmd_man(self, *args):
        """Mostra página do manual"""
        if not args:
            page_num = 1
        else:
            try:
                page_num = int(args[0])
            except (ValueError, IndexError):
                return "Usage: man <page_number>"
                
        from manual import Manual
        page = Manual.get_page(page_num)
        return f"{page['content']}\n\nHint: {page['hint']}"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            self.terminal.handle_input(event)

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        self.sidebar.draw(screen)
        self.terminal.draw(screen)