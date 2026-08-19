import pygame

sprites = []
loaded = {}

class Sprite: 
    def __init__(self, image, x, y): 
        if image in loaded: 
            self.image = loaded[image]
        else: 
            self.image = pygame.image.load(image)
            loaded[image] = self.image

        self.x = x
        self.y = y

        # detect when vendor is close to customer
        self.rect = self.image.get_rect(topleft=(x,y))
        sprites.append(self)
    def delete(self): 
        sprites.remove(self)

    def draw(self, screen): 
        # every character has a collision rectangle
        self.rect.topleft = (self.x, self.y)
        screen.blit(self.image, (self.x, self.y))