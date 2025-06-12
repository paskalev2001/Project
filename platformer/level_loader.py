# level_loader.py

import csv
from objects import Block, Fire, Flag
from player import Player
from enemy import Enemy
from collectibles import Coin
from config import WIDTH, HEIGHT

def load_level_csv(filename, block_size=96):
    """
    Loads a level from a CSV file and returns player, objects.
    Returns:
        player: Player instance at specified location
        objects: List of Block, Fire, etc.
    """
    objects = []
    player = None

    # Open CSV and parse it row by row
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Loop through the CSV grid
    for row_idx, row in enumerate(rows):
        for col_idx, cell in enumerate(row):
            x = col_idx * block_size
            y = row_idx * block_size
            if cell == 'B':
                objects.append(Block(x, y, block_size))
            elif cell == 'F':
                objects.append(Fire(x, y, 16, 32))  # Adjust size as needed
            elif cell == 'P':
                player = Player(x, y, 50, 50)  # Adjust player size as needed
            elif 'E' in cell:
                enemy_data = cell.split('E')
                print(enemy_data)
                left_bound = int(enemy_data[0])
                right_bound = int(enemy_data[1])
                speed = int(enemy_data[2])
                width = int(enemy_data[3])
                height = int(enemy_data[4])
                objects.append(Enemy(x, y, width, height, left_bound, right_bound, speed))
            elif cell == 'C':
                objects.append(Coin(x, y, 24))
            elif cell == 'G':
                objects.append(Flag(x, y, 48))
            # Add more symbols as you add more objects!
            

    # If no player defined, spawn at 100,100 by default
    if player is None:
        player = Player(100, 100, 50, 50)

    return player, objects
