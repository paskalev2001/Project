# utils.py

import pygame
from os import listdir
from os.path import isfile, join

def flip(sprites):
    """
    Flips each sprite horizontally.
    :param sprites: List of Pygame surfaces to flip
    :return: List of flipped surfaces
    """
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    Loads and splits a spritesheet into individual sprites.
    Optionally generates left/right versions by flipping.
    :param dir1: Main asset directory (e.g. 'MainCharacters')
    :param dir2: Subdirectory (e.g. 'NinjaFrog')
    :param width: Width of each sprite frame
    :param height: Height of each sprite frame
    :param direction: If True, generate left/right animations
    :return: Dictionary of lists of sprites
    """
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    """
    Loads and returns a terrain block sprite of a given size.
    :param size: Size of the block (square)
    :return: Scaled block surface
    """
    from os.path import join
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 128, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)
