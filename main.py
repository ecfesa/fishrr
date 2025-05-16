import pygame
import sys
from fishing.example_scene import run_fishing_scene
from utils.txtlib import Text, BEGIN, END, COLOR, BOLD

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
font_path = "font/JetBrainsMono-Regular.ttf"
pygame.display.set_caption("Fishing Game")

# Run the fishing scene
caught_items = run_fishing_scene(screen, font_path)

# Display results if there are any caught items
if caught_items:
    # Create text renderer
    result_text = Text((600, 400), font_path, 24)
    result_text.background_color = (20, 20, 40)  # Dark background
    
    # Create inventory text
    inventory_str = "YOUR CATCH:\n\n"
    for item in caught_items:
        inventory_str += f"- {item.name}\n"
    
    # Render text
    result_text.clear()
    result_text.html(inventory_str)
    result_text.add_style(0, len("YOUR CATCH:"), BOLD)
    result_text.add_style(0, len("YOUR CATCH:"), COLOR, (240, 240, 0))  # Yellow
    result_text.update()
    
    # Display results
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
        
        # Clear screen
        screen.fill((20, 20, 40))
        
        # Draw text
        text_rect = result_text.area.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(result_text.area, text_rect)
        
        # Update display
        pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()

