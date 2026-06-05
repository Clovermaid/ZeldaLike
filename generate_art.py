import pygame
import os

pygame.init()
script_dir = os.path.dirname(__file__)

def create_heart():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Classic pixel heart shape
    pygame.draw.rect(surface, (255, 0, 0), (4, 0, 4, 2))
    pygame.draw.rect(surface, (255, 0, 0), (12, 0, 4, 2))
    pygame.draw.rect(surface, (255, 0, 0), (2, 2, 8, 2))
    pygame.draw.rect(surface, (255, 0, 0), (10, 2, 8, 2))
    pygame.draw.rect(surface, (255, 0, 0), (0, 4, 20, 2))
    pygame.draw.rect(surface, (255, 0, 0), (2, 6, 16, 2))
    pygame.draw.rect(surface, (255, 0, 0), (4, 8, 12, 2))
    pygame.draw.rect(surface, (255, 0, 0), (6, 10, 8, 2))
    pygame.draw.rect(surface, (255, 0, 0), (8, 12, 4, 2))
    pygame.image.save(surface, os.path.join(script_dir, "heart.png"))

def create_ui_key():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Tiny key for UI
    pygame.draw.circle(surface, (255, 215, 0), (7, 7), 4, 2)
    pygame.draw.line(surface, (255, 215, 0), (11, 7), (18, 7), 2)
    pygame.draw.line(surface, (255, 215, 0), (15, 7), (15, 11), 2)
    pygame.image.save(surface, os.path.join(script_dir, "ui_key.png"))

def create_ui_sword():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Tiny sword for UI
    pygame.draw.line(surface, (200, 200, 200), (10, 2), (10, 14), 2)
    pygame.draw.line(surface, (255, 140, 0), (6, 6), (14, 6), 2)
    pygame.draw.line(surface, (139, 69, 19), (10, 14), (10, 18), 2)
    pygame.image.save(surface, os.path.join(script_dir, "ui_sword.png"))

def create_ui_pendant():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Tiny pendant for UI
    pygame.draw.polygon(surface, (255, 105, 180), [(10, 6), (5, 16), (15, 16)])
    pygame.image.save(surface, os.path.join(script_dir, "ui_pendant.png"))

# Don't forget to call them at the bottom!
create_heart()
create_ui_key()
create_ui_sword()
create_ui_pendant()

print("\nAll art generated! Check your folder.")