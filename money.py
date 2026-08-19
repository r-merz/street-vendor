import pygame
from sprite import Sprite

# give money drop a position, image, and amount 
class MoneyDrop(Sprite): 
    def __init__(self, image, x, y, amount):
        super().__init__(image, x, y)

        self.amount = amount 

    def distance_to(self, player):
        dx = self.x - player.x
        dy = self.y - player.y

        return (dx ** 2 + dy ** 2) ** 0.5