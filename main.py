from tiles import * 
from spritesheet import Spritesheet

# load up a basic window and clock 
pygame.init()
DISPLAY_W, DISPLAY_H = 480, 270
canvas = pygame.Surface((DISPLAY_W, DISPLAY_H))
window = pygame.display.set_mode(((DISPLAY_W, DISPLAY_H)))
running = True
clock = pygame.time.Clock()

# load player and spritesheet
spritesheet = Spritesheet('spritesheet.png')
player_img = spritesheet.parse_sprite('vendor.png')
player_rect = player_img.get_rect()

# load the lvl 
map = TileMap('lvl1.csv', spritesheet)
player_rect, player_rect.y = map.start_x, map.start_y

# game loop 
while running: 
    clock.tick(60)
    # check player input 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN: 
            pass 
        #     if event.key == pygame.K_LEFT: 
        #         player.LEFT_KEY, player.FACING_LEFT = True, True
        #     elif event.key == pygame.K_LEFT: 
        #         player.RIGHT_KEY, player.FACING_LEFT = True, False
        # if event.type == pygame.KEYUP: 
        #     if event.key == pygame.K_LEFT: 
        #         player.LEFT_KEY = False
        #     elif event.key == pygame.K_RIGHT: 
        #         player.RIGHT_KEY = False

    # update window and display
    canvas.fill((0,180,240)) # fills the entire screen with light blue 
    map.draw_map(canvas)
    canvas.blit(player_img, player_rect)
    window.blit(canvas, (0,0))
    pygame.display.update()
            