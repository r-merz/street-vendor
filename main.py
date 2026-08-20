import pygame
import asyncio # web demo 
import platform # connect pygame ot localStorage 
import input
from player import Player
from sprite import sprites, Sprite
from map import TileKind, Map
from customer import Customer 
import random
from money import MoneyDrop

import json 

pygame.init()
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 20)

print(pygame.version.ver)
print(pygame.image.get_extended())

# setup 
pygame.display.set_caption("Street Vendor")
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clear_color = (30,150,50)
running = True 

# add timer / win/lose condition 

#PROFIT_GOAL = 50
day_start_time = pygame.time.get_ticks()
day_over = False
current_day = 1


inventory_open = False
prep_open = False
library_open = False

prep_message = ""
inventory_msg = ""
prep_customer = None
prep_step = 0
print("Loading vendor...")
player = Player("images/vendor.png", 100, 100)
print("Vendor loaded")
tile_kinds = [
    TileKind("lvl1", "images/lvl1.png", False),
]

# temp area player cannot enter 
obstacles = [
    pygame.Rect(0, 0, SCREEN_WIDTH, 60),
    pygame.Rect(0, 170, SCREEN_WIDTH, 60),
    pygame.Rect(270, 100, 300, 30), 
    pygame.Rect(450, 80, 100, 200)
]

# blockly constants 
blockly_commands = [ # temp test 
    "up", 
    "right", 
    "right", 
    "down"
]
blockly_command_index = 0
blockly_running = False 
blockly_last_command_time = 0
BLOCKLY_COMMAND_DELAY = 300 # commands no longer executed one frame at a time 
last_blockly_program = None 

customers = [
]
money_drops = []

customer_spawn_points = [
    (100,80), 
    (100,150), 
    (300,70), 
    (400,160), 
    (400,70), 
]

RESTOCK_COSTS = {
    "paleta": 2, 
    "esquite": 3, 
    "raspado": 3
}
## add duros/chicharrones, fruta picada, mangoneadas, tostilocos, etc later on  
SNACK_DATA = {
    "paleta": {
        "sale_price": 5, 
        "prep_type": "instant", 
        "unlock_level": 1, 
        "description": "Un postre congelado hecho de agua o leche en un palillo."
    }, 
    "esquite": {
        "sale_price": 7, 
        "prep_type": "sequence", 
        "unlock_level": 2, 
        "description": "Un antojito mexicano hecho de granos de elote tipicamente servido en un vaso con mayonesa, queso cotija, jugo de limon, y chile en polvo.",
        "steps": [
            {
                "text": "Agregar elote", 
                "key": pygame.K_1
            }, 
            {
                "text": "Agregar mayonesa", 
                "key": pygame.K_2
            }, 
            {
                "text": "Agregar queso", 
                "key": pygame.K_3
            }, 
            {
                "text": "Agregar tajin", 
                "key": pygame.K_4
            }, 
            {
                "text": "Agregar limon", 
                "key": pygame.K_5
            }

        ]
    }, 

    "raspado": {
        "sale_price": 6, 
        "prep_type": "flavor", 
        "unlock_level": 3, 
        "description": "Un postre frio y dulce hecho de hielo y un jarabe dulce de sabor frutal o dulce, servido en un vaso."
    }
}

LEVEL_DATA = {
    1: {
        "map": "maps/start.map", 
        "goal": 20, 
        "day_length": 60, 
        "customer_count": 3, 
        "snacks": ["paleta"], 
        "title": "Getting Started", 
        "description": [
            "- Serve customers around the neighborhood.", 
            "- Collect the money they leave behind.", 
            "- Restock your paletas when you run out."
        ]
    }, 
    2: {
        "map": "maps/start.map", 
        "goal": 35, 
        "day_length": 60, 
        "customer_count": 4, 
        "snacks": ["paleta", "esquite"], 
        "title": "Esquites are now unlocked!", 
        "description":[
            "- Prep ingredients in the correct order.", 
            "- Keep serving customers to reach your goal."
        ]
    }, 
    3: {
        "map": "maps/start.map", 
        "goal": 50, 
        "day_length": 60, 
        "customer_count": 5, 
        "snacks": ["paleta", "esquite", "raspado"], 
        "title": "Raspados are now unlocked!", 
        "description": [
            "- Read each customer's requested flavor.", 
            "- Choose the correct syrup before serving."
        ]
    }
}

level_data = LEVEL_DATA[current_day]
PROFIT_GOAL = level_data["goal"]
DAY_LENGTH = level_data["day_length"]

map = Map(
    level_data["map"], 
    tile_kinds, 
    512
)

RASPADO_FLAVORS = [
    "vainilla", 
    "fresa", 
    "limon", 
    "chicle azul"
]

PREP_STEPS = {
    "paleta": [
        "Unwrap paleta", 
        "Hand to customer"
    ], 

    "esquite": [
        "Add corn", 
        "Add toppings", 
        "Serve esquite"
    ], 

    "raspado": [
        "Shave ice", 
        "Add syrup", 
        "Serve raspado"
    ]

}

# randomly pick location of kid + snack they want
def spawn_customer(): 
    avaiable_points = []
    # check customer spawn point 
    for point in customer_spawn_points: 
        point_x, point_y = point
        occupied = False

        for customer in customers: 
            # don't use spawn point if customer already there 
            if customer.x == point_x and customer.y == point_y: 
                occupied = True 
                break 
        if not occupied: 
            # add to available_points 
            avaiable_points.append(point) 
    if len(avaiable_points) == 0: 
        print("No available customer spawn points.")
        return 
    # randomly choose from available points only
    x, y = random.choice(avaiable_points)
    available_snacks = level_data["snacks"]
    snack = random.choice(available_snacks)
    price = SNACK_DATA[snack]["sale_price"]
    flavor = None 
    if snack == "raspado": 
        flavor = random.choice(RASPADO_FLAVORS) 

    customer = Customer(
        "images/kid3.png", 
        x, 
        y, 
        snack, 
        price, 
        flavor 
    )
    customers.append(customer)

print("Loading paleta...")
paleta_image = pygame.image.load("images/paleta.png").convert_alpha()
print("Paleta loaded")

print("Loading esquite...")
esquite_image = pygame.image.load("images/esquite.png").convert_alpha()
print("Esquite loaded")

print("Loading raspado...")
raspado_image = pygame.image.load("images/raspado.png").convert_alpha()
print("Raspado loaded")

snack_icons = {
    "paleta": pygame.transform.scale(paleta_image, (24, 24)),
    "esquite": pygame.transform.scale(esquite_image, (24, 24)),
    "raspado": pygame.transform.scale(raspado_image, (24, 24))
}

def load_blockly_commands(): 
    global blockly_commands
    global last_blockly_program

    # browser javascript 
    if platform.system() != "Emscripten": 
        return False
    try: 
        window = platform.window 
        stored = window.localStorage.getItem(
            "streetVendorProgram"
        )
        if not stored: 
            return False 
        stored = str(stored)

        program = json.loads(stored) 
        run_id = program["runId"]
        commands = program["commands"]

        if run_id == last_blockly_program: 
            return False
        last_blockly_program = run_id 
        blockly_commands = commands 
        print(
            "New Blockly program:", 
            blockly_commands
        )
        return True
    except Exception as error: 
        print(
            "Could not load Blockly commands:", 
            error 
        )
        return False 
def draw_inventory_card(
    screen, 
    x, 
    y, 
    width, 
    height, 
    snack_name, 
    amount, 
    cost, 
    key, 
    icon
): 
    # card background 
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(
        screen, 
        (245, 240, 220), 
        card_rect, 
        border_radius=10
    )
    pygame.draw.rect(
        screen, 
        (60, 60, 60), 
        card_rect,
        2, 
        border_radius=10
    )
    # snack icon
    icon_x = x+15
    icon_y = y + (height - icon.get_height()) //2
    screen.blit(icon, (icon_x, icon_y))

    # snack name 
    name_text = font.render(
        snack_name.capitalize(), 
        True, 
        (30, 30, 30)
    )
    screen.blit(
        name_text, 
        (x+60, y+12)
    )
    # inventory amt 
    amount_text = small_font.render(
        f"In stock: {amount}", 
        True, 
        (60, 60, 60)
    )
    screen.blit(
        amount_text, 
        (x+60, y+40)
    )
    # price
    price_text = small_font.render(
        f"Restock: ${cost}", 
        True, 
        (60, 60, 60)
    )
    screen.blit(
        price_text, 
        (x+180, y+40)
    )
    # keyboard button 
    button_rect = pygame.Rect(
        x+width - 55, 
        y+18, 
        35, 
        35
    )
    pygame.draw.rect(
        screen, 
        (70, 120, 80), 
        button_rect, 
        border_radius=6
    )
    key_text = font.render(
        str(key), 
        True, 
        (255, 255, 255)
    )
    key_rect = key_text.get_rect(
        center=button_rect.center
    )
    screen.blit(key_text, key_rect)

def wrap_text(text, font, max_width):
    words = text.split()

    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "

        test_surface = font.render(
            test_line,
            True,
            (0, 0, 0)
        )

        if test_surface.get_width() > max_width:
            if current_line:
                lines.append(current_line.strip())

            current_line = word + " "

        else:
            current_line = test_line

    if current_line:
        lines.append(current_line.strip())

    return lines

# def start_next_day(): 
#     global current_day
#     global PROFIT_GOAL
#     global day_start_time 
#     global day_over 

#     current_day += 1

#     if current_day in DAY_GOALS: 
#         PROFIT_GOAL = DAY_GOALS[current_day]

#     day_start_time = pygame.time.get_ticks()
#     day_over = False 

#     player.profit = 0

#     player.inventory = {
#         "paleta": 3, 
#         "esquite": 3, 
#         "raspado": 3
#     }

#     player.x = 100
#     player.y = 100

def complete_sale(customer): 
    if player.inventory[customer.wanted_snack] <= 0: 
        return 
    player.inventory[customer.wanted_snack] -= 1

    money = MoneyDrop(
        "images/money.png", 
        customer.x, 
        customer.y, 
        customer.price
    )
    money_drops.append(money)
    customer.sold = True
    customer.delete()

    if customer in customers: 
        customers.remove(customer)

    spawn_customer()

def load_level(level_number): 
    global current_day
    global level_data
    global PROFIT_GOAL
    global DAY_LENGTH
    global day_start_time
    global day_over
    global map 
    global level_intro_open

    current_day = level_number 
    level_data = LEVEL_DATA[current_day]
    PROFIT_GOAL = level_data["goal"]
    DAY_LENGTH = level_data["day_length"]
    day_start_time = None
    day_over = False 

    # reset player position 
    player.x = 100
    player.y = 100

    # load map 
    print("Loading map...")
    map = Map(
        level_data["map"], 
        tile_kinds, 
        512
    )
    print("Map loaded")

    # remove existing customers 
    for customer in customers[:]: 
        customer.delete()

    customers.clear()

    # spawn correct # in lvl 
    for i in range(level_data["customer_count"]):
        spawn_customer()

    level_intro_open = True


def start_next_day(): 
    next_level = current_day + 1

    if next_level in LEVEL_DATA: 
        load_level(next_level)
load_level(1) 
# game loop 
async def main(): 
    global day_start_time
    global day_over
    global level_intro_open
    global inventory_open
    global inventory_msg
    global library_open
    global prep_open
    global prep_customer
    global prep_step
    global prep_message

    global blockly_running
    global blockly_command_index
    global blockly_last_command_time
    global last_blockly_program
    pygame.init()

    running = True
    while running: 

        if day_start_time is None: 
            time_left = DAY_LENGTH # player doesn't lose time while reading intro

        else: 

            # calculate time remaining every frame 
            current_time = pygame.time.get_ticks() # returns ms
            elapsed_seconds = (current_time - day_start_time) // 1000 # convert to s
            time_left = DAY_LENGTH - elapsed_seconds
            if time_left <= 0: 
                time_left = 0
                day_over = True 
        # win condition 
        if player.profit >= PROFIT_GOAL: 
            day_over = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False 
            elif event.type == pygame.KEYDOWN: 
                input.keys_down.add(event.key)
                if level_intro_open: 
                    if event.key == pygame.K_SPACE: 
                        level_intro_open = False
                        day_start_time = pygame.time.get_ticks()

                        continue 
                if event.key == pygame.K_e and not day_over and not inventory_open and not prep_open: # can't keep making money after timer hits zero
                    collected_money = False
                    # check for money
                    for money in money_drops: 
                        if money.distance_to(player) <= 40:
                            player.profit += money.amount
                            money.delete()
                            money_drops.remove(money)
                            print(f"Collected ${money.amount}")
                            collected_money = True
                            break 
                    # money not collected, check customers
                    if not collected_money: 
                        for customer in customers: 
                            if not customer.sold and customer.distance_to(player) <= 50: 
                                snack = customer.wanted_snack
                                prep_type = SNACK_DATA[snack]["prep_type"]
                                if player.inventory[snack] <= 0: 
                                    print("Out of", snack)

                                elif prep_type == "instant": 
                                    complete_sale(customer) 
                                elif prep_type == "sequence": 
                                    prep_open = True
                                    prep_customer = customer
                                    prep_step = 0
                                    prep_message = ""
                                elif prep_type == "flavor": 
                                    prep_open = True 
                                    prep_customer = customer 
                                    prep_step = 0
                                    prep_message = ""

                                break 

                            # for every customer that disappears, a new random one appears
                            # if customer.sold: 
                            #     customers.remove(customer)
                            #     spawn_customer()
                            # break
                # snack prep keyboard controls 
                
                if prep_open and prep_customer is not None: 
                    snack = prep_customer.wanted_snack 
                    prep_type = SNACK_DATA[snack]["prep_type"]

                    if prep_type == "sequence": 
                        steps = SNACK_DATA[snack]["steps"]
                        current_step = steps[prep_step]

                        if event.key == current_step["key"]: 
                            prep_step += 1
                            prep_message = ""

                            if prep_step >= len(steps): 
                                complete_sale(prep_customer)

                                prep_open = False
                                prep_customer = None 
                                prep_step = 0

                        elif event.key in [
                            pygame.K_1, 
                            pygame.K_2, 
                            pygame.K_3, 
                            pygame.K_4, 
                            pygame.K_5
                        ]: 
                            prep_message = "Wrong ingredient!"
                    elif prep_type == "flavor": 
                        selected_flavor = None 
                        if event.key == pygame.K_1: 
                            selected_flavor = "vainilla"
            
                        elif event.key == pygame.K_2: 
                            selected_flavor = "fresa"
                        elif event.key == pygame.K_3: 
                            selected_flavor = "limon"
                        elif event.key == pygame.K_4: 
                            selected_flavor = "chicle azul"
            
                        if selected_flavor is not None: 
                            if selected_flavor == prep_customer.flavor: 
            
                                complete_sale(prep_customer)
            
                                prep_open = False
            
                                prep_customer = None 
                            else: 
                                prep_message = "Wrong flavor!"


                # restart day 
                if event.key == pygame.K_r and day_over: 
                    player.profit = 0
                    player.inventory = {
                        "paleta": 3, 
                        "esquite": 3, 
                        "raspado": 3
                    }
                    day_start_time = pygame.time.get_ticks()
                    day_over = False 
                
                # toggle inventory screen 
                if event.key == pygame.K_i and not library_open and not prep_open: 
                    inventory_open = not inventory_open 
                if inventory_open: 
                    unlocked_snacks = level_data["snacks"]
                    number_keys = [
                        pygame.K_1, 
                        pygame.K_2, 
                        pygame.K_3, 
                        pygame.K_4, 
                        pygame.K_5
                    ]

                    for index, snack in enumerate(unlocked_snacks): 
                        if event.key == number_keys[index]: 
                            cost = RESTOCK_COSTS[snack]

                            if player.profit >= cost: 
                                player.profit -= cost
                                player.inventory[snack] += 1

                                inventory_msg = f"Bought 1 {snack}!"
                            else: 
                                inventory_msg = "Not enough $$!"
                            break 
                if event.key == pygame.K_n and day_over: 
                    if player.profit >= PROFIT_GOAL: 
                        if current_day < max(LEVEL_DATA): 
                            start_next_day() 
                # toggle library
                if event.key == pygame.K_l and not inventory_open and not prep_open: 
                    library_open = not library_open

            elif event.type == pygame.KEYUP: 
                input.keys_down.discard(event.key)
            # show coordinates when clicking on screen to determine collision blocks
            # elif event.type == pygame.MOUSEBUTTONDOWN: 
            #     print("Mouse:", pygame.mouse.get_pos())

        # update code
        if(
            not day_over 
            and not inventory_open 
            and not prep_open
            and not library_open
            and not level_intro_open): # prevent movement while inventory open
                                    # vendor can't drive away while prepping order
            player.update(obstacles) # player stops moving once time runs out 
        if load_blockly_commands(): 
            blockly_command_index = 0
            blockly_running = True 
            blockly_last_command_time = 0
        if(
            blockly_running
            and not day_over 
            and not inventory_open
            and not prep_open 
            and not library_open 
            and not level_intro_open
        ): 
            current_blockly_time = pygame.time.get_ticks() 
            if(
                current_blockly_time - blockly_last_command_time
                >= BLOCKLY_COMMAND_DELAY
            ): 
                if blockly_command_index < len(blockly_commands):
                    command = blockly_commands[blockly_command_index]
                    player.execute_command(
                        command, 
                        obstacles
                    )

                    blockly_command_index += 1
                    blockly_last_command_time = current_blockly_time
                else: 
                    blockly_running = False
        # draw code 
        screen.fill(clear_color)
        map.draw(screen)

        # show collision boxes 
        # for obstacle in obstacles:
        #     # show collision area for walls/buildings/roads
        #     # pygame.draw.rect(screen, (255, 0, 0), obstacle, 2)
        #     # # show player's collision area 
        #     # pygame.draw.rect(
        #     #     screen, 
        #     #     (0, 0, 255), 
        #     #     player.get_rect(), 
        #     #     2
        #     # )
        for s in sprites: 
            s.draw(screen)
        for customer in customers: 
            customer.draw_request(screen, snack_icons)
        # add HUD to show profit and inventory on screen 
        profit_text = font.render(
            f"Profit: ${player.profit}", 
            True, 
            (255, 255, 255)
        )

        timer_text = font.render(
            f"Time: {time_left}", 
            True, 
            (255, 255, 255)
        )
        paleta_text = font.render(
            f"Paletas: {player.inventory['paleta']}", 
            True, 
            (255, 255, 255)
        )

        esquite_text = font.render(
                f"Esquites: {player.inventory['esquite']}", 
                True, 
                (255, 255, 255)
        )

        raspado_text = font.render(
                f"Raspados: {player.inventory['raspado']}", 
                True, 
                (255, 255, 255)
        )
        day_text = font.render(
            f"Day {current_day}", 
            True, 
            (255, 255, 255)
        )
        goal_text = font.render(
            f"Goal: ${PROFIT_GOAL}", 
            True, 
            (255, 255, 255)
        )
        money_nearby = False
        for money in money_drops: 
            if money.distance_to(player) <= 40: 
                money_nearby = True
                collect_text = font.render(
                    f"Press E to collect ${money.amount}", 
                    True, 
                    (255, 255, 255)
                )
                screen.blit(
                    collect_text, 
                    (200, 250)
                )
                        
                break
        if(
            not money_nearby 
            and not prep_open 
            and not inventory_open
            and not library_open
            and not level_intro_open
        ): 
            for customer in customers: 
                if not customer.sold and customer.distance_to(player) <= 50: 
                    if player.inventory[customer.wanted_snack] > 0: 
                        if customer.wanted_snack == "raspado": 
                            message = (
                                f"Press E - Prepare Raspado de ({customer.flavor})"
                            )
                        else: 
                            message = f"Press E - Prepare {customer.wanted_snack}"
                    else: 
                        message = f"Out of {customer.wanted_snack} - Press I to restock"
                    interact_text = font.render(
                        message, 
                        True, 
                        (255, 255, 255)
                    )
                    screen.blit(interact_text, (100, 250))
                    break
                
        # show results screen 
        if day_over: 
            overlay = pygame.Surface((600, 300))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0,0))
            if player.profit >= PROFIT_GOAL: 
                result_text = font.render(
                    f"Day {current_day} Complete! You reached your goal! c:", 
                    True, 
                    (255, 255, 255)
                )
                if current_day < max(LEVEL_DATA): 
                    next_text = font.render(
                        "Press N for next day", 
                        True, 
                        (255, 255, 255)
                    )
                else: 
                    next_text = font.render(
                        "You have completed all levels!", 
                        True, 
                        (255, 255, 255)
                        )
            else: 
                result_text = font.render(
                    f"Day {current_day} Over! You did not reach the profit goal. :c", 
                    True, 
                    (255, 255, 255)
                )
            profit_result = font.render(
                f"Final Profit: ${player.profit}", 
                True, 
                (255, 255, 255)
            )
            restart_text = font.render(
                "Press R to restart", 
                True, 
                (255, 255, 255)
            )
            screen.blit(restart_text, (220, 200))
            screen.blit(result_text, (120, 120))
            screen.blit(profit_result, (220, 160))
            screen.blit(next_text, (200, 250))

        # inventory overlay
        if inventory_open:

            # dark transparent background over entire game
            dark_overlay = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )

            dark_overlay.fill((0, 0, 0, 150))

            screen.blit(dark_overlay, (0, 0))


            # main inventory window
            unlocked_snacks = level_data["snacks"]
            panel_height = 95 + (len(unlocked_snacks) * 62)
            panel = pygame.Rect(
                70,
                25,
                460,
                panel_height
            )

            pygame.draw.rect(
                screen,
                (220, 205, 175),
                panel,
                border_radius=15
            )

            pygame.draw.rect(
                screen,
                (80, 65, 50),
                panel,
                3,
                border_radius=15
            )


            # title
            title = title_font.render(
                "Inventory",
                True,
                (45, 35, 25)
            )

            screen.blit(
                title,
                (95, 40)
            )


            # money
            money_text = font.render(
                f"Money: ${player.profit}",
                True,
                (45, 35, 25)
            )

            screen.blit(
                money_text,
                (390, 47)
            )


            # snack cards
            unlocked_snacks = level_data["snacks"]
            card_y = 80 

            for index, snack in enumerate(unlocked_snacks, start=1): 
                draw_inventory_card(
                    screen, 
                    95, 
                    card_y, 
                    410, 
                    55, 
                    snack, 
                    player.inventory[snack], 
                    RESTOCK_COSTS[snack], 
                    index, 
                    snack_icons[snack]
                )
                card_y += 62


            # close instruction
            close_text = small_font.render(
                "Press I to close",
                True,
                (255, 255, 255)
            )

            screen.blit(
                close_text,
                (10, 275)
            )

            if inventory_msg != "":
                message_text = small_font.render(
                    inventory_msg, 
                    True, 
                    (255, 255, 255)
                )
                screen.blit(
                    message_text, 
                    (350, 275)
                )
        

        # left hud background 
        hud_background = pygame.Surface((170, 30), pygame.SRCALPHA)
        hud_background.fill((0,0,0,160))
        screen.blit(hud_background, (150,5))

        # left hud text
        screen.blit(profit_text, (200, 10))

        # right hud background 
        right_hud_background = pygame.Surface((140, 80), pygame.SRCALPHA)
        right_hud_background.fill((0,0,0,160))
        screen.blit(right_hud_background, (SCREEN_WIDTH-150,5))


        # right hud text
        hud_x = SCREEN_WIDTH - 140
        screen.blit(day_text, (hud_x, 35))
        screen.blit(goal_text, (hud_x, 60))
        # screen.blit(paleta_text, (10, 35))
        # screen.blit(esquite_text, (10, 60))
        # screen.blit(raspado_text, (10, 85))
        screen.blit(timer_text, (hud_x, 10))

        # snack prep window
        if prep_open and prep_customer is not None:

            snack = prep_customer.wanted_snack
            prep_type = SNACK_DATA[snack]["prep_type"]

            # darken game behind prep window
            overlay = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            # main prep panel
            panel = pygame.Rect(
                70,
                40,
                460,
                300
            )

            pygame.draw.rect(
                screen,
                (245, 235, 210),
                panel,
                border_radius=12
            )

            # title
            title = title_font.render(
                f"Prepare {snack.capitalize()}",
                True,
                (40, 30, 20)
            )

            screen.blit(title, (100, 65))


            # =====================================
            # ESQUITE
            # =====================================
            if prep_type == "sequence":

                steps = SNACK_DATA[snack]["steps"]
                current_step = steps[prep_step]

                step_text = font.render(
                    f"Next: {current_step['text']}",
                    True,
                    (40, 30, 20)
                )

                corn_text = font.render(
                    "1 - Agregar elote", 
                    True, 
                    (40, 30, 20)
                )

                mayo_text = font.render(
                    "2 - Agregar mayonesa", 
                    True, 
                    (40, 30, 20)
                )

                cheese_text = font.render(
                    "3 - Agregar queso", 
                    True, 
                    (40, 30, 20)
                )


                tajin_text = font.render(
                    "4 - Agregar tajin", 
                    True, 
                    (40, 30, 20)
                )

                limon_text = font.render(
                    "5 - Agregar limon", 
                    True, 
                    (40, 30, 20)
                )


                progress_text = small_font.render(
                    f"Step {prep_step + 1} / {len(steps)}",
                    True,
                    (40, 30, 20)
                )

                instruction_text = small_font.render(
                    "Press SPACE to complete this step",
                    True,
                    (40, 30, 20)
                )

                screen.blit(step_text, (100, 115))
                screen.blit(corn_text, (100, 145))
                screen.blit(mayo_text, (100, 170))
                screen.blit(cheese_text, (100, 195))
                screen.blit(tajin_text, (100, 225))
                screen.blit(limon_text, (100, 250))
                screen.blit(progress_text, (100, 275))

                if prep_message != "": 
                    error_text = small_font.render(
                        prep_message, 
                        True, 
                        (180, 30, 30)
                    )
                    screen.blit(error_text, (300, 275))
                #screen.blit(instruction_text, (100, 195))


            # =====================================
            # RASPADO
            # =====================================
            elif prep_type == "flavor":

                request_text = font.render(
                    f"Customer wants: {prep_customer.flavor}",
                    True,
                    (40, 30, 20)
                )

                vainilla_text = font.render(
                    "1 - Vainilla",
                    True,
                    (40, 30, 20)
                )

                fresa_text = font.render(
                    "2 - Fresa",
                    True,
                    (40, 30, 20)
                )

                limon_text = font.render(
                    "3 - Limon",
                    True,
                    (40, 30, 20)
                )

                chicle_text = font.render(
                    "4 - Chicle Azul",
                    True,
                    (40, 30, 20)
                )

                screen.blit(request_text, (100, 110))
                screen.blit(vainilla_text, (100, 140))
                screen.blit(fresa_text, (100, 165))
                screen.blit(limon_text, (100, 190))
                screen.blit(chicle_text, (100, 215))

                if prep_message != "":
                    error_text = small_font.render(
                        prep_message,
                        True,
                        (180, 30, 30)
                    )

                    screen.blit(error_text, (300, 215))
        # draw snack library 
        if library_open:

            # darken background
            dark_overlay = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )

            dark_overlay.fill((0, 0, 0, 170))
            screen.blit(dark_overlay, (0, 0))

            # main library panel
            library_margin = 40
            panel = pygame.Rect(
                library_margin, 
                library_margin, 
                SCREEN_WIDTH - (library_margin * 2), 
                SCREEN_HEIGHT - (library_margin * 2)
            )

            pygame.draw.rect(
                screen,
                (235, 220, 190),
                panel,
                border_radius=14
            )

            pygame.draw.rect(
                screen,
                (80, 65, 50),
                panel,
                3,
                border_radius=14
            )

            title = title_font.render(
                "Snacks Library",
                True,
                (45, 35, 25)
            )

            screen.blit(title, (70, 70))

            # draw snacks
            snack_names = ["paleta", "esquite", "raspado"]

            card_x = 80
            card_y = 110 
            card_width = SCREEN_WIDTH - 160 

            for snack in snack_names:

                data = SNACK_DATA[snack]

                unlocked = snack in level_data["snacks"]

                description_lines = wrap_text(
                    data["description"], 
                    small_font, 
                    card_width - 110
                )
                card_height = 90 + (len(description_lines) * 18)
                card_rect = pygame.Rect(
                    card_x,
                    card_y, 
                    card_width, 
                    card_height
                )

                if unlocked:
                    card_color = (250, 245, 225)
                else:
                    card_color = (150, 160, 160)

                pygame.draw.rect(
                    screen,
                    card_color,
                    card_rect,
                    border_radius=10
                )

                pygame.draw.rect(
                    screen,
                    (70, 60, 50),
                    card_rect,
                    2,
                    border_radius=10
                )

                # make locked icons look locked
                icon = snack_icons[snack].copy()
                if not unlocked: 
                    icon.fill(
                        (90, 90, 90, 255), 
                        special_flags=pygame.BLEND_RGBA_MULT
                    )

                screen.blit(
                    icon,
                    (
                        card_x + 15,
                        card_y + 15
                    )
                )

                # snack name
                name_text = font.render(
                    snack.capitalize(),
                    True,
                    (40, 30, 20)
                )

                screen.blit(
                    name_text,
                    (
                        card_x + 55,
                        card_y + 12
                    )
                )

                # locked/unlocked
                if unlocked:
                    status = "Unlocked"
                else: 
                    status = f"Unlocks Level {data['unlock_level']}"
                status_text = small_font.render(
                    status, 
                    True, 
                    (70, 60, 50)
                )
                screen.blit(
                    status_text, 
                    (card_x + card_width - 140, card_y + 15)
                )
                # price
                price_text = small_font.render(
                    f"Sale price: ${data['sale_price']}",
                    True,
                    (60, 50, 40)
                )

                screen.blit(
                    price_text,
                    (
                        card_x + 55,
                        card_y + 40
                    )
                )

                # description
                description_y = card_y + 65

                for line in description_lines: 
                    description_text = small_font.render(
                        line, 
                        True, 
                        (60, 50, 40)
                    )
                    screen.blit(
                        description_text, 
                        (card_x + 55, description_y)
                    )

                    description_y += 18

                # automatically move next card down 
                card_y += card_height + 15

            close_text = small_font.render(
                "Press L to close",
                True,
                (255, 255, 255)
            )

            screen.blit(
                close_text,
                (20, SCREEN_HEIGHT - 30)
            )
        if level_intro_open:

            overlay = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            panel_width = 520
            panel_height = 320

            panel_x = (screen.get_width() - panel_width) // 2
            panel_y = (screen.get_height() - panel_height) // 2

            panel = pygame.Rect(
                panel_x,
                panel_y,
                panel_width,
                panel_height
            )

            pygame.draw.rect(
                screen,
                (245, 235, 210),
                panel,
                border_radius=14
            )

            pygame.draw.rect(
                screen,
                (80, 65, 50),
                panel,
                3,
                border_radius=14
            )

            # level number
            level_text = title_font.render(
                f"Level {current_day}",
                True,
                (45, 35, 25)
            )

            screen.blit(
                level_text,
                (panel_x + 30, panel_y + 25)
            )

            # level title
            intro_title = font.render(
                level_data["title"],
                True,
                (45, 35, 25)
            )

            screen.blit(
                intro_title,
                (panel_x + 30, panel_y + 70)
            )

            # goal
            goal_text = font.render(
                f"Goal: ${PROFIT_GOAL}",
                True,
                (45, 35, 25)
            )

            screen.blit(
                goal_text,
                (panel_x + 350, panel_y + 30)
            )

            # available snacks
            snack_names = ", ".join(
                snack.capitalize()
                for snack in level_data["snacks"]
            )

            snacks_text = small_font.render(
                f"Available: {snack_names}",
                True,
                (70, 55, 40)
            )

            screen.blit(
                snacks_text,
                (panel_x + 30, panel_y + 105)
            )

            # descriptions
            description_y = panel_y + 150

            for line in level_data["description"]:

                description_text = font.render(
                    line,
                    True,
                    (45, 35, 25)
                )

                screen.blit(
                    description_text,
                    (panel_x + 30, description_y)
                )

                description_y += 35

            # start instruction
            start_text = font.render(
                "Press SPACE to begin",
                True,
                (45, 35, 25)
            )

            start_rect = start_text.get_rect(
                center=(
                    panel.centerx,
                    panel.bottom - 35
                )
            )

            screen.blit(start_text, start_rect)

        pygame.display.flip()
        #pygame.time.delay(17)

        await asyncio.sleep(0) #yield control back to browser event loop every frame
    pygame.quit()

asyncio.run(main()) # run async main function 