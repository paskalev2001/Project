# level_loader.py

import csv
from objects import Block, Fire
from player import Player
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
            # Add more symbols as you add more objects!

    # If no player defined, spawn at 100,100 by default
    if player is None:
        player = Player(100, 100, 50, 50)

    return player, objects
