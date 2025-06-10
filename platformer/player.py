# player.py

import pygame
from utils import load_sprite_sheets
from config import PLAYER_VEL, FPS

class Player(pygame.sprite.Sprite):
    """
    The Player class represents the main character.
    Handles movement, jumping, sprite animation, collision, and drawing.
    """
    MAX_HEALTH = 16
    DAMAGE_INTERVAL = 1000  # milliseconds
    COLOR = (255, 0, 0)
    GRAVITY = 0.98
    SPRITES = None  # Will be set after pygame.display is initialized
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        """
        Initializes the player at (x, y) with specified width and height.
        Loads sprites if not already loaded.
        """
        super().__init__()
        if Player.SPRITES is None:
            Player.SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = self.MAX_HEALTH
        self.last_fire_damage_time = 0 

    def take_damage(self, amount):
        """Reduces health and clamps at zero."""
        self.health = max(0, self.health - amount)
        # Optional: Add respawn/death logic here

    def heal(self, amount):
        """Increases health but doesn't exceed max."""
        self.health = min(self.MAX_HEALTH, self.health + amount)

    def jump(self):
        """
        Makes the player jump if allowed (double jump).
        """
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def make_hit(self):
        """
        Sets the player's hit status (for collision with hazards).
        """
        self.hit = True
        self.hit_count = 0

    def move(self, dx, dy):
        """
        Moves the player by (dx, dy).
        """
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        """
        Sets horizontal velocity for moving left.
        """
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        """
        Sets horizontal velocity for moving right.
        """
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        """
        Updates player's movement, gravity, hit status, and sprite animation each frame.
        """
        self.y_vel += min(0.98, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 0.8:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        """
        Resets counters when player lands on ground.
        """
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        """
        Handles head collision with a block (reverse velocity).
        """
        self.fall_count = 0
        self.y_vel *= -1

    def update_sprite(self):
        """
        Selects and updates the current sprite frame based on movement state.
        """
        sprite_sheet = "idle"

        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """
        Updates the player's rect and mask based on the current sprite.
        """
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        """
        Draws the player on the window, offset by camera.
        """
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
