import pygame

class Enemy(pygame.sprite.Sprite):
    """
    Simple enemy: red square that patrols horizontally between two bounds.
    """
    COLOR = (255, 0, 0)  # Red

    def __init__(self, x, y, width, height, left_bound, right_bound, speed=2):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(self.COLOR)
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.x_vel = speed
        self.direction = "right" if speed > 0 else "left"
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """
        Move the enemy left and right between the two bounds.
        """
        self.rect.x += self.x_vel
        if self.rect.x <= self.left_bound:
            self.rect.x = self.left_bound
            self.x_vel = abs(self.x_vel)
            self.direction = "right"
        elif self.rect.x + self.rect.width >= self.right_bound:
            self.rect.x = self.right_bound - self.rect.width
            self.x_vel = -abs(self.x_vel)
            self.direction = "left"

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))