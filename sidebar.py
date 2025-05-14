import pygame
from constants import FONT, DARK_GRAY, WHITE, GRAY

# Initialize Pygame
pygame.init()

class Sidebar:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(FONT, 16)
        self.title_font = pygame.font.Font(FONT, 24)
        self.commands = ["fish", "help", "todo", "man"]
        
        # Task list display
        self.show_tasks = False
        self.tasks = []
        self.tasks_title = "Tasks"
    
    def draw(self, screen: pygame.Surface) -> None:
        # Draw sidebar background
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        
        # Draw title
        title_surface = self.title_font.render("Commands", True, WHITE)
        screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw commands list
        y_offset = self.rect.y + 50
        for cmd in self.commands:
            cmd_surface = self.font.render(cmd, True, WHITE)
            screen.blit(cmd_surface, (self.rect.x + 20, y_offset))
            y_offset += 30
            
        # Draw separator
        pygame.draw.line(
            screen, 
            GRAY, 
            (self.rect.x + 10, y_offset), 
            (self.rect.x + self.rect.width - 10, y_offset),
            2
        )
        y_offset += 20
        
        # Draw task list if available
        if self.show_tasks and self.tasks:
            task_title = self.title_font.render(self.tasks_title, True, WHITE)
            screen.blit(task_title, (self.rect.x + 10, y_offset))
            y_offset += 40
            
            for task in self.tasks:
                if y_offset + 30 < self.rect.bottom:  # Ensure we don't go off screen
                    task_surface = self.font.render(task, True, WHITE)
                    screen.blit(task_surface, (self.rect.x + 15, y_offset))
                    y_offset += 25
    
    def set_tasks(self, tasks, title="Tasks"):
        self.tasks = tasks
        self.tasks_title = title
        self.show_tasks = True
        
    def hide_tasks(self):
        self.show_tasks = False