# objects.py

import pygame
from utils import get_block, load_sprite_sheets

class Object(pygame.sprite.Sprite):
    """
    Base class for all static and dynamic objects (platforms, hazards, etc).
    """
    def __init__(self, x, y, width, height, name=None):
        """
        Initialize object at (x, y) with given size.
        """
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        """
        Draw the object on the window, offset by camera.
        """
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    """
    A solid terrain block/platform.
    """
    def __init__(self, x, y, size):
        """
        Creates a terrain block at (x, y) with a specific size.
        """
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    """
    An animated fire hazard that can hurt the player.
    """
    ANIMATION_DELAY = 3
    FIRE_SPRITES = None  # Loaded after pygame display initialized

    def __init__(self, x, y, width, height):
        """
        Initializes fire at (x, y) with given size, loads sprites if needed.
        """
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        """
        Turns the fire animation on.
        """
        self.animation_name = "on"

    def off(self):
        """
        Turns the fire animation off.
        """
        self.animation_name = "off"

    def loop(self):
        """
        Updates the fire animation each frame.
        """
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count = (self.animation_count + 1) % (self.ANIMATION_DELAY * len(sprites))
        self.mask = pygame.mask.from_surface(self.image)
