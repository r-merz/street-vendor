from sprite import Sprite
import pygame

class Customer(Sprite): 
    def __init__(self, image, x, y, wanted_snack, price, flavor=None): 
        super().__init__(image, x, y)

        self.wanted_snack = wanted_snack
        self.price = price
        self.sold = False
        self.flavor = flavor 

    def distance_to(self, player): 
        dx = self.x - player.x
        dy = self.y - player.y

        return (dx ** 2 + dy ** 2) ** 0.5

    def try_sell(self, player): 
        if self.sold: 
            return "Already served"

        if self.distance_to(player) > 50: 
            return "Too far away"

        if player.inventory[self.wanted_snack] <= 0: 
            return "Out of " + self.wanted_snack

        player.inventory[self.wanted_snack] -= 1
        #player.profit += self.price

        self.sold = True
        self.delete()

        return "Sold " + self.wanted_snack 

    # request bubbles for snacks
    def draw_request(self, screen, snack_icons): 
        icon = snack_icons[self.wanted_snack]
        #print("Customer wants:", self.wanted_snack)

        # main thought bubble 
        bubble_x = self.x - 5
        bubble_y = self.y - 45
        bubble_width = icon.get_width() + 18
        bubble_height = icon.get_height() + 14

        bubble_rect = pygame.Rect(
            bubble_x, 
            bubble_y, 
            bubble_width, 
            bubble_height
        )

        # large white oval 
        pygame.draw.ellipse(
            screen, 
            (255, 255, 255), 
            bubble_rect
        )

        # black outline
        pygame.draw.ellipse(
            screen, 
            (0,0,0), 
            bubble_rect, 
            2
        )

        # thought circles
        pygame.draw.circle(
            screen, 
            (255, 255, 255), 
            (int(self.x + 10), int(self.y - 12)), 
            5
        )

        pygame.draw.circle(
            screen, 
            (0,0,0), 
            (int(self.x + 10), int(self.y - 12)), 
            5, 
            1
        )

        pygame.draw.circle(
            screen, 
            (255, 255, 255), 
            (int(self.x + 5), int(self.y - 3)), 
            3
        )

        pygame.draw.circle(
            screen, 
            (0,0,0), 
            (int(self.x + 5), int(self.y -3)), 
            3, 
            1
        )

        # snack inside bubble 
        icon_x = bubble_x + (bubble_width - icon.get_width()) // 2
        icon_y = bubble_y + (bubble_height - icon.get_height()) // 2

        # original 
        # bubble = pygame.Rect(
        #     self.x, 
        #     self.y - 30, 
        #     icon.get_width() + 10, 
        #     icon.get_height() + 6
        # )

        # pygame.draw.rect(
        #     screen, 
        #     (0, 0, 0), 
        #     bubble, 
        #     border_radius=8
        # )

        screen.blit(
            icon, 
            (icon_x, icon_y)
        )

