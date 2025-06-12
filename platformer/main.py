# main.py

import sys
import pygame
import pygame.time
import wx
from config import WIDTH, HEIGHT, FPS, BG_COLOR, PLAYER_VEL
from utils import load_sprite_sheets, get_block
from player import Player
from objects import Block, Fire
from enemy import Enemy
from level_loader import load_level_csv
import os
import thread

def get_background(name):
    """
    Loads the background image and calculates tile positions to fill the screen.
    :param name: Filename of the background image.
    :return: Tuple (list of tile positions, background image surface)
    """
    from os.path import join
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image

def draw_health_bar(window, health, max_health):
    """Draws a health bar at the top left of the screen."""
    bar_width = 200
    bar_height = 25
    x, y = 20, 20
    fill = (health / max_health) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(window, (255, 0, 0), fill_rect)
    pygame.draw.rect(window, (0, 0, 0), outline_rect, 2)

def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    """
    Draws the entire game scene (background, objects, player) on the window.
    :param window: The pygame display window.
    :param background: List of tile positions for the background.
    :param bg_image: The background image surface.
    :param player: Player object.
    :param objects: List of game objects (blocks, hazards, etc).
    :param offset_x: Horizontal camera offset.
    :param offset_y: Vertical camera offset.
    """
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    draw_health_bar(window, player.health, player.MAX_HEALTH)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    """
    Handles collisions for vertical movement (jumping/falling).
    Adjusts player position if collision occurs, and triggers landing or head hit.
    :param player: Player object.
    :param objects: List of objects to check collision against.
    :param dy: Vertical velocity (direction of movement).
    :return: List of collided objects.
    """
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects

def collide(player, objects, dx):
    """
    Checks for collision in the horizontal direction.
    Moves player temporarily, checks for mask collision, then reverts move.
    :param player: Player object.
    :param objects: List of objects to check.
    :param dx: Amount to move horizontally for collision check.
    :return: The first collided object or None.
    """
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    """
    Handles player movement based on key input and prevents movement through obstacles.
    Also handles player being hit by hazards (e.g., fire).
    :param player: Player object.
    :param objects: List of objects to interact with.
    """
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 1.6)
    collide_right = collide(player, objects, PLAYER_VEL * 1.6)

    # Move left/right if no collision
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not collide_right:
        player.move_right(PLAYER_VEL)

    # Handle vertical collision (jump/fall)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    fire_touched = False  # track if player is touching fire

    # If player collides with fire, set hit state
    for obj in to_check:
        if obj and getattr(obj, 'name', None) == "fire":
            player.make_hit()
            fire_touched = True

        if isinstance(obj, Enemy):
            player.make_hit()
            fire_touched = True

    if fire_touched:
        current_time = pygame.time.get_ticks()  # milliseconds since pygame.init()
        if current_time - player.last_fire_damage_time >= player.DAMAGE_INTERVAL:
            player.take_damage(1)  # or whatever amount per tick
            player.last_fire_damage_time = current_time
    else:
        # Reset timer if player is not on fire
        # (so they take damage immediately next time they touch)
        player.last_fire_damage_time = 0

def main(level_file=None):
    """
    Main game loop. Initializes pygame, sets up the scene, processes events,
    updates the player and objects, draws everything, and manages camera scrolling.
    """
    pygame.init()
    game_window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Platformer")
    clock = pygame.time.Clock()

    # Load background tiles
    background, bg_image = get_background("Purple.png")

    # Set up game world objects
    block_size = 96
    
    # If level_file is specified, load that level. Else, use a default.
    if level_file is not None:
        player, objects = load_level_csv(level_file)
        # Make sure all fire objects are ON
        for obj in objects:
            if isinstance(obj, Fire):
                obj.on()
        

    else:
        # Create a floor that covers the width of the level
        floor = [Block(i * block_size, HEIGHT - block_size, block_size)
                for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
        player = Player(100, 100, 50, 50)
        enemy = Enemy(x=300, y=HEIGHT - 96*2, width=40, height=40, left_bound=200, right_bound=500, speed=2)

        # Add a fire hazard and some extra blocks
        fire = Fire(200, HEIGHT - block_size - 64, 16, 32)

        objects = [
            *floor,
            Block(0, HEIGHT - block_size * 2, block_size),
            Block(block_size * 3, HEIGHT - block_size * 4, block_size),
            fire,
            enemy
        ]

    # Camera/scrolling offsets
    offset_x = 0
    scroll_area_width = WIDTH // 5

    offset_y = 0
    scroll_area_height = HEIGHT // 6

    run = True
    while run:
        clock.tick(FPS)
        # Handle window close and key events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        # Update player and hazard (fire) animations and movement
        player.loop(FPS)
        for obj in objects:
            if isinstance(obj, Fire):
                obj.loop()
            if isinstance(obj, Enemy):
                obj.move()

        # Handle user movement and object collisions
        handle_move(player, objects)

        # Draw the current frame
        draw(
            window=game_window,
            background=background,
            bg_image=bg_image,
            player=player,
            objects=objects,
            offset_x=offset_x,
            offset_y=offset_y,
        )
        # Handle horizontal camera scrolling
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0
        ):
            offset_x += player.x_vel

        # Handle vertical camera scrolling
        if ((player.rect.bottom - offset_y >= HEIGHT - scroll_area_height) and player.y_vel > 0) or (
            (player.rect.top - offset_y <= scroll_area_height) and player.y_vel < 0
        ):
            offset_y += player.y_vel

        if player.health <= 0:
            pygame.quit()
            show_game_over_dialog()
            return  # or break/run = False, as appropriate

    pygame.quit()
    quit()

def show_game_over_dialog():
    # wx must run on main thread! 
    app = wx.App(False)
    dialog = wx.MessageDialog(
        None,
        "Game Over!\nWhat do you want to do?",
        "Game Over",
        wx.YES_NO | wx.ICON_QUESTION
    )
    dialog.SetYesNoLabels("Return to Main Menu", "Exit Game")
    result = dialog.ShowModal()
    dialog.Destroy()
    if result == wx.ID_YES:
        # Return to main menu
        python = sys.executable
        os.execl(python, python, "menu.py")  # assumes menu.py is in same folder
    else:
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
