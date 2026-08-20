import pygame
from sprite import Sprite
from input import is_key_pressed

class Player(Sprite): 
    def __init__(self, image, x, y): 
        super().__init__(image, x, y)
        self.movement_speed = 2

        self.inventory = {
            "paleta": 3, 
            "esquite": 3, 
            "raspado": 3
        }
        self.profit = 0

    # give player collision rectangle
    def get_rect(self): 
        return pygame.Rect(
            self.x, 
            self.y, 
            self.image.get_width(), 
            self.image.get_height()
        )
    def update(self, obstacles): 
        dx = 0
        dy = 0

        if is_key_pressed(pygame.K_w):
            dy -= self.movement_speed
        if is_key_pressed(pygame.K_a): 
           dx -= self.movement_speed
        if is_key_pressed(pygame.K_s): 
            dy += self.movement_speed
        if is_key_pressed(pygame.K_d): 
            dx += self.movement_speed

        # define blocked rectangles on map
        # move left/right first
        self.x += dx 
        player_rect = self.get_rect()

        for obstacle in obstacles: 
            if player_rect.colliderect(obstacle): 

                if dx > 0: 
                    self.x = obstacle.left - self.image.get_width()

                elif dx < 0: 
                    self.x = obstacle.right

                player_rect = self.get_rect()

        # move up/down second 
        self.y += dy 
        player_rect = self.get_rect()
        
        for obstacle in obstacles: 
            if player_rect.colliderect(obstacle): 

                if dy > 0: 
                    self.y = obstacle.top - self.image.get_height()

                elif dy < 0: 
                    self.y = obstacle.bottom

                player_rect = self.get_rect()
    # make pygame capable of executing command list 
    def execute_command(self, command, obstacles): 
        old_x = self.x
        old_y = self.y
        distance = 20
        if command == "up": 
            self.y -= distance
        elif command == "down": 
            self.y += distance 
        elif command == "left": 
            self.x -= distance 
        elif command == "right": 
            self.x += distance 

        #collision check / reuse collision system 
        player_rect = self.get_rect()

        for obstacle in obstacles: 
            if player_rect.colliderect(obstacle): 
                self.x = old_x 
                self.y = old_y 
                break 
