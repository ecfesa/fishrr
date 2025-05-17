import pygame

from game.ui.draw_window import draw_window
import game.assets as assets
import game.globals as g
import string

pygame.init()
pygame.display.set_caption("fishrr")

# Whitelist for allowed input characters
ALLOWED_CHARS = frozenset(
    string.ascii_lowercase +
    string.ascii_uppercase +
    string.digits +
    " !@#$%^&*()_+-=[]{};':\",./<>?|~`" + # Common special characters
    "\r"  # Enter key
    "\b"  # Backspace key
)

def process_input(event: pygame.event.Event):
    if event.key == pygame.K_l and (
        event.mod & pygame.KMOD_CTRL or
        event.mod & pygame.KMOD_LCTRL or
        event.mod & pygame.KMOD_RCTRL
    ):
        g.SYSTEM.clear()
    else:
        if event.unicode == "" or event.unicode not in ALLOWED_CHARS:
            return
        assets.KEYBOARD_SOUND.play()
        g.SYSTEM.process_input(event.unicode)

def run():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(g.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                process_input(event)

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_ESCAPE]:
            run = False

        draw_window()

    pygame.quit()

if __name__ == "__main__":
    run()