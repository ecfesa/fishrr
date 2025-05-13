import pygame
from manager import constantmanager

class Sidebar:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(constantmanager.FONT, 16)
        self.title_font = pygame.font.Font(constantmanager.FONT, 24)
        self.commands = ["fish"]

    def draw(self, screen: pygame.Surface) -> None:
        # Draw sidebar background
        pygame.draw.rect(screen, constantmanager.DARK_GRAY, self.rect)

        # Draw title
        title_surface = self.title_font.render("Commands", True, constantmanager.WHITE)
        screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))

        # Draw commands list
        y_offset = self.rect.y + 50
        for cmd in self.commands:
            cmd_surface = self.font.render(cmd, True, constantmanager.WHITE)
            screen.blit(cmd_surface, (self.rect.x + 20, y_offset))
            y_offset += 30
