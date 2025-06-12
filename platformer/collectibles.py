import pygame

class Coin(pygame.sprite.Sprite):
    
    COLOR = (255, 223, 0)  # Gold/yellow

    def __init__(self, x, y, size=24):
        super().__init__()
        self.rect = pygame.Rect(x, y, size, size)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.COLOR, (size // 2, size // 2), size // 2)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))