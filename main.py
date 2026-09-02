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

PANEL_YELLOW = (
    214,
    177,
    79
)

PANEL_BORDER = (
    72,
    50,
    25
)

PANEL_HIGHLIGHT = (
    247,
    220,
    132
)

PANEL_SHADOW = (
    145,
    104,
    45
)

PANEL_TEXT = (
    45,
    32,
    20
)

LIBRARY_BG = (
    235,
    220,
    190
)

LIBRARY_CARD = (
    250,
    245,
    225
)

LIBRARY_LOCKED = (
    170,
    165,
    145
)

LIBRARY_BORDER = (
    80,
    65,
    50
)

LIBRARY_HIGHLIGHT = (
    255,
    245,
    220
)

LIBRARY_SHADOW = (
    150,
    130,
    100
)

LIBRARY_TEXT = (
    45,
    35,
    25
)

GAME_WIDTH = 840
GAME_HEIGHT = 495
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
clear_color = (20, 40, 25)
running = True 

# add timer / win/lose condition 

#PROFIT_GOAL = 50
day_start_time = pygame.time.get_ticks()
day_over = False
current_day = 0


inventory_open = False
prep_open = False
library_open = False

prep_message = ""
inventory_msg = ""
prep_customer = None
prep_step = 0
paleta_customer = None 
paleta_message = "" 
paleta_order_open = False 

blockly_debug_message = ""
print("Loading vendor...")
PLAYER_START = (
    300,
    170
)
player = Player("images/vendor.png", PLAYER_START[0], PLAYER_START[1])
print("Vendor loaded")
tile_kinds = [
    TileKind("lvl1", "images/lvl1.png", False),
]

# coordinate conversion 
BASE_MAP_WIDTH = 512
BASE_MAP_HEIGHT = 512

SCALE_X = GAME_WIDTH / BASE_MAP_WIDTH
SCALE_Y = GAME_HEIGHT / BASE_MAP_HEIGHT 
def map_point(x, y): 
    return(
        int(x * SCALE_X), 
        int(y * SCALE_Y)
    )
def map_rect(x, y, width, height): 
    return pygame.Rect(
        int(x * SCALE_X), 
        int(y * SCALE_Y), 
        int(width * SCALE_X), 
        int(height * SCALE_Y)
    )
# Areas the vendor cannot walk through
# Coordinates are now based directly on the 840x495 game surface.
obstacles = [
    # Top-left building block
    pygame.Rect(
        0,
        0,
        265,
        145
    ),

    # Top-right building block
    pygame.Rect(
        365,
        0,
        475,
        145
    ),

    # Bottom-left building block
    pygame.Rect(
        0,
        340,
        265,
        155
    ),

    # Bottom-right building block
    pygame.Rect(
        395,
        340,
        445,
        155
    ),
]

# blockly constants 
blockly_commands = []
blockly_command_index = 0
blockly_running = False 
blockly_last_command_time = 0
BLOCKLY_COMMAND_DELAY = 300 # commands no longer executed one frame at a time 
last_blockly_program = None 

blockly_used_repeat = False
blockly_used_condition = False 
blockly_used_serve = False 

# tutorial constants
tutorial_step = 1
tutorial_message = ( 
"Bienvenido! Construye un progama usando los bloques abajo de la seccion de movimiento. "
"Cada bloque representa una instrucction que el paletero seguira. "
"Hace que el paletero se mueva a la izquierda, a la derecha, arriba, o hacia abajo. "
"Intenta agregar un bloque de movimiento, y luego presiona Run. "
)
tutorial_feedback = ""
tutorial_run_count = 0
tutorial_feedback_counter = 0
TUTORIAL_FEEDBACK_DURATION = 5000 
customers = [
]
money_drops = []

customer_spawn_points = [
    # Upper-left sidewalk
    (80, 165),
    (180, 165),

    # Upper-right sidewalk
    (430, 165),
    (560, 165),
    (700, 165),

    # Lower-left sidewalk
    (80, 315),
    (180, 315),

    # Lower-right sidewalk
    (430, 315),
    (560, 315),
    (700, 315),
]

def point_is_walkable(x, y): 
    test_rect = pygame.Rect(
        x,
        y, 
        20, 
        20
    )
    for obstacle in obstacles: 
        if test_rect.colliderect(obstacle): 
            return False
    return True 

RESTOCK_COSTS = {
    "paleta": 2, 
    "esquite": 3, 
    "raspado": 3
}
## add duros/chicharrones, fruta picada, mangoneadas, tostilocos, etc later on  
SNACK_DATA = {
    "paleta": {
        "sale_price": 5, 
        "prep_type": "paleta_flavor", 
        "unlock_level": 1, 
        "description": "Un postre congelado hecho de agua o leche en un palillo.", 
        "flavors": [
            "fresa", 
            "limon", 
            "mango", 
            "tamarindo"
        ]
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
    0: {
        "map": "maps/start.map", 
        "goal": 5, 
        "day_length": None, 
        "customer_count": 1, 
        "snacks": ["paleta"], 
        "timed": False, 
        "title": "Tutorial", 
        "description": [
            "- Learn how to use blocks to move around the neighborhood.", 
            "- Serve your 1st customer!", 
            "- Collect the $$ to finish the tutorial."
        ]
    }, 
    1: {
        "map": "maps/start.map", 
        "goal": 20, 
        "day_length": 60, 
        "customer_count": 3, 
        "snacks": ["paleta"], 
        "timed": True, 
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
        "timed": True, 
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
        "timed": True, 
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


def draw_pixel_panel(
    surface,
    rect,
    background=(235, 220, 190),
    border=(55, 45, 35),
    highlight=(255, 245, 220),
    shadow=(120, 95, 70)
):
    # Outer dark border
    pygame.draw.rect(
        surface,
        border,
        rect
    )

    # Shadow layer
    shadow_rect = pygame.Rect(
        rect.x + 4,
        rect.y + 4,
        rect.width - 4,
        rect.height - 4
    )

    pygame.draw.rect(
        surface,
        shadow,
        shadow_rect
    )

    # Main panel
    inner_rect = pygame.Rect(
        rect.x + 4,
        rect.y + 4,
        rect.width - 8,
        rect.height - 8
    )

    pygame.draw.rect(
        surface,
        background,
        inner_rect
    )

    # Top highlight
    pygame.draw.line(
        surface,
        highlight,
        (
            inner_rect.left + 2,
            inner_rect.top + 2
        ),
        (
            inner_rect.right - 3,
            inner_rect.top + 2
        ),
        2
    )

    pygame.draw.line(
        surface,
        highlight,
        (
            inner_rect.left + 2,
            inner_rect.top + 2
        ),
        (
            inner_rect.left + 2,
            inner_rect.bottom - 3
        ),
        2
    )
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
        if not occupied and point_is_walkable(point_x, point_y): 
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
    if snack == "paleta": 
        flavor = random.choice(
            SNACK_DATA["paleta"]["flavors"]
        )

    elif snack == "raspado": 
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
print("Loading customer portrait...")
customer_portrait_image = pygame.image.load(
    "images/kid3.png"

).convert_alpha()
print("Customer portrait loaded")
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
    global blockly_used_condition
    global blockly_used_repeat 
    global blockly_used_serve 

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

        # handle reset immediately 
        if commands == ['reset']: 
            print("Reset program received")
            reset_current_level()
            window.localStorage.removeItem(
                "streetVendorProgram"
            )

            last_blockly_program = run_id

            return False 
        blockly_used_repeat = program.get(
            "usedRepeat", 
            False 
        )
        blockly_used_condition = program.get(
            "usedCondition", 
            False 
        )
        blockly_used_serve = program.get(
            "usedServe", 
            False 
        )
        # consume the program so it cannot replay after another refresh 
        window.localStorage.removeItem(
            "streetVendorProgram"
        )

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
    game_surface.blit(icon, (icon_x, icon_y))

    # snack name 
    name_text = font.render(
        snack_name.capitalize(), 
        True, 
        (30, 30, 30)
    )
    game_surface.blit(
        name_text, 
        (x+60, y+12)
    )
    # inventory amt 
    amount_text = small_font.render(
        f"In stock: {amount}", 
        True, 
        (60, 60, 60)
    )
    game_surface.blit(
        amount_text, 
        (x+60, y+40)
    )
    # price
    price_text = small_font.render(
        f"Restock: ${cost}", 
        True, 
        (60, 60, 60)
    )
    game_surface.blit(
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
        PANEL_TEXT
    )
    key_rect = key_text.get_rect(
        center=button_rect.center
    )
    game_surface.blit(key_text, key_rect)

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

    # do not spawn another customer during tutorial
    if current_day != 0: 
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

    player.x, player.y = PLAYER_START

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
load_level(0) 

def update_tutorial():
    global tutorial_step
    global tutorial_message
    global tutorial_feedback 

    if current_day != 0: 
        return 

    # player has executed at least 1 blockly command / learn basic movement 
    if tutorial_step == 1: 
        if blockly_command_index > 0: 
            tutorial_step = 2
            tutorial_feedback = ""
            tutorial_message = (
                "Excelente! El paletero hizo lo que quisiste. "
                "Ahora agregar mas bloques para guiar al paletero hacia el cliente."
                "Se ejecutan en orden de arriba hacia abajo."
            )

    # player is close enough to interact
    elif tutorial_step == 2: 
        for customer in customers: 
            if customer.distance_to(player) <= 50: 
                tutorial_step = 3
                tutorial_feedback = ""
                tutorial_message = "Llegaste al cliente! Ahora usa una condicion. Agrega el bloque 'if customer nearby' y coloca 'serve customer' dentro de el. Luego presiona Run." 
                break 
    # customer has been served
    elif tutorial_step == 3: 
        if paleta_order_open and paleta_customer is not None: 

            tutorial_step = 4
            tutorial_feedback = ""
            tutorial_message = (
                "Muy bien! El cliente hizo su pedido. Observa el sabor de la paleta que quiere. Ahora agrega 'choose paleta flavor' y selecciona el sabor correcto."
            )
    elif tutorial_step == 4: 
        if len(money_drops) > 0: 
            tutorial_step = 5
            tutorial_feedback = ""
            tutorial_message = ("Venta completada! El cliente le dejo dinero. Agrega el bloque 'collect money' bajo la seccion de Movimento para recogerlo y presiona Run."
           
            )

    # tutorial ends

def give_tutorial_feedback():
    global tutorial_feedback
    global tutorial_feedback_timer
    global tutorial_run_count

    global blockly_used_repeat
    global blockly_used_condition  

    if current_day != 0:
        return

    if day_over:
        return

    tutorial_run_count += 1

    # Step 1: no movement / ineffective first attempt
    if tutorial_step == 1:
        tutorial_feedback = (
            "Pista: comienza con un bloque de Movimiento. "
            "Cada bloque mueve al paletero un paso."
        )

    # Still trying to reach customer
    elif tutorial_step == 2:
        customer_nearby = any(
            customer.distance_to(player) <= 50
            for customer in customers 
        )
        if customer_nearby: 
            tutorial_feedback = ""
        elif blockly_used_repeat:

            tutorial_feedback = (
                "¡Excelente! Usaste Repeat para repetir una instrucción "
                "sin tener que agregar el mismo bloque muchas veces."
            )

        elif tutorial_run_count >= 3:

            tutorial_feedback = (
                "Pista: si necesitas repetir el mismo movimiento muchas veces, "
                "prueba el bloque Repeat. Coloca un bloque de movimiento dentro "
                "de Repeat y elige cuántas veces debe ejecutarse."
            )

        else:

            tutorial_feedback = (
                "Todavía no estás suficientemente cerca del cliente. "
                "Observa dónde terminó el paletero y modifica tu programa."
            )

   # Near customer: condition + serve required
    elif tutorial_step == 3:

        if not blockly_used_condition:
            tutorial_feedback = (
                "Pista: usa 'if customer nearby'. "
                "Coloca 'serve customer' dentro de la condición."
            )

        elif not blockly_used_serve:
            tutorial_feedback = (
                "Ya tienes la condición. Ahora coloca "
                "'serve customer' dentro de 'if customer nearby'."
            )

        else:
            tutorial_feedback = (
                "El cliente todavía no ha sido servido. "
                "Asegúrate de que el paletero esté suficientemente "
                "cerca cuando se ejecute la condición."
            )


    # Customer order is open: choose flavor
    elif tutorial_step == 4:

        tutorial_feedback = (
            "Lee el pedido en la ventana del cliente. "
            "Usa 'choose paleta flavor' y selecciona el sabor indicado."
        )


    # Money exists but has not been collected
    elif tutorial_step == 5:

        tutorial_feedback = (
            "El dinero está en el suelo. "
            "Usa 'collect money' cuando el paletero esté cerca."
        )

    tutorial_feedback_timer = pygame.time.get_ticks()
# game side support 

# blockly
def execute_serve_command(): 
    global prep_open
    global prep_customer
    global prep_step 
    global prep_message
    global paleta_customer
    global paleta_message 
    global paleta_order_open

    print("Serve command received")

    for customer in customers:

        distance = customer.distance_to(
            player 
        ) 
        print(
            "Customer distance:", 
            distance
        )
        if(
            not customer.sold
            and customer.distance_to(player) <= 50 

        ): 
            snack = customer.wanted_snack 
            print(
                "Serving:", 
                snack
            )
            #prep_type = SNACK_DATA[snack]["prep_type"]

            if player.inventory[snack] <= 0: 
                print("Out of", snack)
                return 
            prep_type = (
                SNACK_DATA[snack]["prep_type"]
            )
            if prep_type == "paleta_flavor": 
                # customer's order is already open. 
                # do not stop blockly again 
                # allow choose paleta flavor command to execute

                if paleta_customer is customer: 
                    print(
                        "Paleta order already pending: ", customer.flavor
                    )
                    return "order_already_open"
                # first time serving customer 
                paleta_customer = customer
                paleta_order_open = True

                paleta_message = (
                    f"El cliente quiere una paleta de {customer.flavor}."
                )
                

                print("================================")
                print("PALETA POPUP OPEN")
                print("paleta_order_open:", paleta_order_open)
                print("paleta_customer:", paleta_customer)
                print("flavor:", customer.flavor)
                print("================================")

                return "waiting_for_flavor"
            elif prep_type == "sequence": 
                prep_open = True 
                prep_customer = customer 
                prep_step = 0
                prep_message = ""
                return 
            elif prep_type == "flavor": 
                prep_open = True 
                prep_customer = customer 
                prep_step = 0 
                prep_message = ""
                return 
# blockly      
def execute_collect_command(): 
    global blockly_debug_message
    blockly_debug_message = (
        f"Money drops available: {len(money_drops)}"
    )

    for money in money_drops[:]: 
        distance = money.distance_to(player)
        blockly_debug_message = (
            f"Money drops: {len(money_drops)} | "
            f"Distance: {round(distance, 1)}"
        )

        if distance <= 50: 

            player.profit += money.amount 
            print(
                "Blockly collected:", 
                money.amount 
            )
            money.delete()
            money_drops.remove(
                money
            )
            return True 
    print(
        "Collect failed:"
        "no money nearby"
    )
    return False
# choose paleta flavor blockly-python integration 
def execute_paleta_flavor_command(flavor):
    global paleta_customer
    global paleta_message
    global paleta_order_open

    if paleta_customer is None:
        paleta_message = (
            "No hay un pedido de paleta esperando una selección."
        )
        return False

    if flavor == paleta_customer.flavor:
        paleta_message = (
            f"¡Correcto! Paleta de {flavor}."
        )

        complete_sale(paleta_customer)

        paleta_customer = None
        paleta_order_open = False 
        return True

    paleta_message = (
        f"Flavor incorrecto. "
        f"El cliente pidió {paleta_customer.flavor}."
    )

    return False
# reset blockly button function 
def reset_current_level(): 
    global blockly_running 
    global blockly_command_index
    global blockly_last_command_time 
    global tutorial_step
    global tutorial_message
    global prep_open
    global prep_customer 
    global prep_step 
    global prep_message

    global paleta_order_open 
    global paleta_customer
    global paleta_message 

    global inventory_open
    global library_open

    global day_over 
    global day_start_time

    global tutorial_feedback
    global tutorial_run_count 
    global tutorial_feedback_timer 

    print("Resetting level...")

    # stop Blockly program 
    blockly_running = False
    blockly_command_index = 0
    blockly_last_command_time = 0 

    # reset player 
    player.x, player.y = PLAYER_START
    player.profit = 0
    player.inventory = {
        "paleta": 3, 
        "esquite": 3, 
        "raspado": 3
    }

    # remove money but keep during tutorial 
    for money in money_drops[:]:
        money.delete()

    money_drops.clear()
    # # remove customers
    # for customer in customers[:]: 
    #     customer.delete()
    # customers.clear()

    # # respawn correct number
    # for i in range(
    #     level_data["customer_count"]
    # ):
    #     spawn_customer()

    # close windows 
    prep_open = False
    prep_customer = None 
    prep_step = 0
    prep_message = ""

    # close paleta customer order
    paleta_order_open = False
    paleta_customer = None 
    paleta_message = ""

    # reset day 

    day_over = False 
    if level_data["timed"]: 
        day_start_time = (
            pygame.time.get_ticks()
        )
    else: 
        day_start_time = None 

    if current_day == 0:

        tutorial_step = 1

        tutorial_message = (
            "Bienvenido! Construye un programa usando los bloques "
            "de Movimiento. Cada bloque representa una instrucción "
            "que el paletero seguirá. Agrega un bloque de movimiento "
            "y presiona Run."
        )

        tutorial_feedback = ""
def clear_old_blockly_program(): 
    if platform.system() != "Emscripten": 
        return 
    try: 
        window = platform.window 
        window.localStorage.removeItem(
            "streetVendorProgram"
        )
        print(
            "Cleared old Blockly program"
        )
    except Exception as error: 
        print(
            "Could not clear old Blockly program:", 
            error
        )

def find_paleta_flavor_command(commands):

    for command in commands:

        if isinstance(command, dict):

            if command.get("type") == "choose_paleta_flavor":
                return command

            if command.get("type") == "if_customer_nearby":

                nested = command.get(
                    "commands",
                    []
                )

                found = find_paleta_flavor_command(
                    nested
                )

                if found is not None:
                    return found

    return None

def find_collect_command(commands):

    for command in commands:

        if command == "collect":
            return "collect"

        if isinstance(command, dict):

            nested = command.get(
                "commands",
                []
            )

            found = find_collect_command(
                nested
            )

            if found is not None:
                return found

    return None
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
    global paleta_order_open 
    global paleta_customer 
    global paleta_message 

    global blockly_running
    global blockly_command_index
    global blockly_last_command_time
    global last_blockly_program

    global tutorial_step
    global tutorial_message
    global tutorial_feedback

    pygame.init()
    clear_old_blockly_program()

    running = True
    while running: 
        if not level_data["timed"]: 
            # tutorial has no countdown
            time_left = None 
        elif day_start_time is None: 
            
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

                                # elif prep_type == "instant": 
                                #     complete_sale(customer) 
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
            and not level_intro_open
        ):
            player.update(obstacles)

        if load_blockly_commands(): 
            blockly_command_index = 0
            blockly_running = True 
            blockly_last_command_time = 0

        # blockly executor 
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

                    command = blockly_commands[
                        blockly_command_index
                    ]

                    print(
                        "Executing Blockly command:",
                        command
                    )

                    if command == "reset": 
                        reset_current_level()

                    else: 

                        if isinstance(command, dict):

                            if (
                                command.get("type")
                                == "if_customer_nearby"
                            ): 
                                print(
                                    "Checking if customer is nearby..."
                                )

                                customer_nearby = False

                                for customer in customers: 

                                    distance = customer.distance_to(
                                        player
                                    )

                                    print(
                                        "Customer distance:",
                                        distance
                                    )

                                    if(
                                        not customer.sold
                                        and distance <= 50
                                    ): 
                                        customer_nearby = True 
                                        break 

                                print(
                                    "Customer nearby:",
                                    customer_nearby
                                )

                                if customer_nearby: 

                                    nested_commands = command.get(
                                        "commands",
                                        []
                                    )

                                    print(
                                        "Nested commands:",
                                        nested_commands
                                    )

                                    blockly_commands[
                                        blockly_command_index + 1:
                                        blockly_command_index + 1
                                    ] = nested_commands

                            elif (
                                command.get("type")
                                == "choose_paleta_flavor"
                            ):

                                flavor = command.get(
                                    "flavor"
                                )

                                execute_paleta_flavor_command(
                                    flavor
                                )

                        else: 

                            if command == "serve": 
                                execute_serve_command()

                            elif command == "collect": 
                                execute_collect_command()

                            else: 
                                player.execute_command(
                                    command,
                                    obstacles
                                )

                    blockly_command_index += 1

                    blockly_last_command_time = (
                        current_blockly_time
                    )

                    if (
                        blockly_command_index
                        >= len(blockly_commands)
                    ): 
                        blockly_running = False

                        if (
                            current_day == 0
                            and not day_over
                        ): 
                            give_tutorial_feedback()

                else: 
                    blockly_running = False

        # draw code 
        update_tutorial()
        game_surface.fill(clear_color)
        map.draw(game_surface)

        # # show collision boxes 
        # for obstacle in obstacles: 
        #     pygame.draw.rect(
        #         game_surface, 
        #         (255, 0, 0), 
        #         obstacle, 
        #         2
        #     )
        # pygame.draw.rect(
        #     game_surface, 
        #     (0, 0, 255), 
        #     player.get_rect(), 
        #     2
        # )
        for s in sprites: 
            s.draw(game_surface)
        for customer in customers: 
            customer.draw_request(game_surface, snack_icons)
        # add HUD to show profit and inventory on screen 
        profit_text = font.render(
            f"Profit: ${player.profit}", 
            True, 
            PANEL_TEXT
        )
        if level_data["timed"]: 

            timer_text = font.render(
                f"Time: {time_left}", 
                True, 
                PANEL_TEXT
            )
        else: 
            timer_text = font.render(
                "Tutorial", 
                True, 
                PANEL_TEXT
            )
        paleta_text = font.render(
            f"Paletas: {player.inventory['paleta']}", 
            True, 
            PANEL_TEXT
        )

        esquite_text = font.render(
                f"Esquites: {player.inventory['esquite']}", 
                True, 
                PANEL_TEXT
        )

        raspado_text = font.render(
                f"Raspados: {player.inventory['raspado']}", 
                True, 
                PANEL_TEXT
        )
        if current_day == 0: 
            day_label = "Tutorial"
        else: 
            day_label = f"Day {current_day}"
        day_text = font.render(
            day_label, 
            True, 
            PANEL_TEXT
        )
        goal_text = font.render(
            f"Goal: ${PROFIT_GOAL}", 
            True, 
            PANEL_TEXT
        )
        money_nearby = False
        for money in money_drops: 
            if money.distance_to(player) <= 40: 
                money_nearby = True
                collect_text = font.render(
                    f"Press E to collect ${money.amount}", 
                    True, 
                    LIBRARY_TEXT
                )
                collect_rect = pygame.Rect(
                    0, 
                    0, 
                    collect_text.get_width() + 36, 
                    collect_text.get_height() + 20, 
                )

                collect_rect.center = (
                    GAME_WIDTH // 2, 
                    GAME_HEIGHT - 105
                )

                draw_pixel_panel(
                    game_surface, 
                    collect_rect, 
                    background = LIBRARY_BG, 
                    border = LIBRARY_BORDER, 
                    highlight=LIBRARY_HIGHLIGHT, 
                    shadow=LIBRARY_SHADOW
                )

                text_rect = collect_text.get_rect(
                    center=collect_rect.center
                )
                game_surface.blit(
                    collect_text, 
                    text_rect
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
                            message = f"Press E - Prepare {customer.wanted_snack.capitalize()}"
                    else: 
                        message = f"Out of {customer.wanted_snack} - Press I to restock"
                    interact_text = font.render(
                        message, 
                        True, 
                        LIBRARY_TEXT
                    )
                    padding_x = 18
                    padding_y = 10 
                    interact_rect = pygame.Rect(
                        0, 
                        0, 
                        interact_text.get_width() + padding_x * 2, 
                        interact_text.get_height() + padding_y + 2
                    )
                    interact_rect.center = (
                        GAME_WIDTH // 2, 
                        GAME_HEIGHT - 105 
                    )

                    draw_pixel_panel(
                        game_surface, 
                        interact_rect, 
                        background = LIBRARY_BG, 
                        border=LIBRARY_BORDER, 
                        highlight=LIBRARY_HIGHLIGHT, 
                        shadow=LIBRARY_SHADOW
                    )
                    text_rect = interact_text.get_rect(
                        center=interact_rect.center 
                    )
                    game_surface.blit(interact_text, text_rect)
                    break
                
        # show results screen 
        if day_over:

            # Darken the game slightly
            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 110))

            game_surface.blit(
                overlay,
                (0, 0)
            )


            # Main result panel
            result_panel = pygame.Rect(
                170,
                110,
                500,
                260
            )

            draw_pixel_panel(
                game_surface,
                result_panel,
                background=LIBRARY_BG,
                border=LIBRARY_BORDER,
                highlight=LIBRARY_HIGHLIGHT,
                shadow=LIBRARY_SHADOW
            )


            # Result message
            if player.profit >= PROFIT_GOAL:

                if current_day == 0:
                    result_message = "Tutorial Complete!"
                else:
                    result_message = (
                        f"Level {current_day} Complete!"
                    )

            else:
                result_message = (
                    f"Level {current_day} Over!"
                )


            result_text = title_font.render(
                result_message,
                True,
                LIBRARY_TEXT
            )

            result_rect = result_text.get_rect(
                center=(
                    result_panel.centerx,
                    result_panel.top + 55
                )
            )

            game_surface.blit(
                result_text,
                result_rect
            )


            # Final profit
            profit_result = font.render(
                f"Final Profit: ${player.profit}",
                True,
                LIBRARY_TEXT
            )

            profit_rect = profit_result.get_rect(
                center=(
                    result_panel.centerx,
                    result_panel.top + 110
                )
            )

            game_surface.blit(
                profit_result,
                profit_rect
            )


            # Next / retry instruction
            if player.profit >= PROFIT_GOAL:

                if current_day == 0:
                    next_message = (
                        "Press N to start Level 1"
                    )

                elif current_day < max(LEVEL_DATA):
                    next_message = (
                        "Press N for next level"
                    )

                else:
                    next_message = (
                        "All levels complete!"
                    )

            else:
                if player.profit < PROFIT_GOAL: 
                    restart_text = small_font.render(
                        "Press R to retry", 
                        True, 
                        LIBRARY_TEXT
                    )
                restart_rect = restart_text.get_rect(
                    center=(
                        result_panel.centerx,
                        result_panel.bottom - 35 
                    )
                )
                game_surface.blit(
                    result_text, 
                    restart_rect
                )
                next_message = (
                    "Press R to retry"
                )


            next_text = font.render(
                next_message,
                True,
                LIBRARY_TEXT
            )

            next_rect = next_text.get_rect(
                center=(
                    result_panel.centerx,
                    result_panel.top + 165
                )
            )

            game_surface.blit(
                next_text,
                next_rect
            )


            # Restart instruction
            restart_text = small_font.render(
                "Press R to restart",
                True,
                LIBRARY_TEXT
            )

            restart_rect = restart_text.get_rect(
                center=(
                    result_panel.centerx,
                    result_panel.bottom - 35
                )
            )

            game_surface.blit(
                restart_text,
                restart_rect
            )

        # inventory overlay
        if inventory_open:

            # dark transparent background over entire game
            dark_overlay = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )

            dark_overlay.fill((0, 0, 0, 150))

            game_surface.blit(dark_overlay, (0, 0))


            # main inventory window
            unlocked_snacks = level_data["snacks"]
            panel_height = 95 + (len(unlocked_snacks) * 62)
            panel = pygame.Rect(
                70,
                25,
                460,
                panel_height
            )

            draw_pixel_panel(
                game_surface,  
                panel
            )


            # title
            title = title_font.render(
                "Inventory",
                True,
                (45, 35, 25)
            )

            game_surface.blit(
                title,
                (95, 40)
            )


            # money
            money_text = font.render(
                f"Money: ${player.profit}",
                True,
                (45, 35, 25)
            )

            game_surface.blit(
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
                PANEL_TEXT
            )

            game_surface.blit(
                close_text,
                (10, 275)
            )

            if inventory_msg != "":
                message_text = small_font.render(
                    inventory_msg, 
                    True, 
                    PANEL_TEXT
                )
                game_surface.blit(
                    message_text, 
                    (350, 275)
                )
        

        # left hud background 
        hud_background = pygame.Surface((170, 30), pygame.SRCALPHA)
        hud_background.fill((0,0,0,160))
        game_surface.blit(hud_background, (150,5))

        # left hud text
        profit_panel = pygame.Rect(
            150, 
            5, 
            170, 
            32
        )
        draw_pixel_panel(
            game_surface, 
            profit_panel, 
            background = PANEL_YELLOW, 
            border = PANEL_BORDER, 
            highlight = PANEL_HIGHLIGHT, 
            shadow = PANEL_SHADOW 
        )
        game_surface.blit(profit_text, (175, 11))

        # right HUD panel
        right_panel = pygame.Rect(
            GAME_WIDTH - 150,
            5,
            140,
            82
        )

        draw_pixel_panel(
            game_surface,
            right_panel,
            background=PANEL_YELLOW, 
            border = PANEL_BORDER, 
            highlight = PANEL_HIGHLIGHT, 
            shadow = PANEL_SHADOW
        )

        # right HUD text
        hud_x = GAME_WIDTH - 140

        game_surface.blit(timer_text, (hud_x, 10))
        game_surface.blit(day_text, (hud_x, 35))
        game_surface.blit(goal_text, (hud_x, 60))

        # snack prep window
        if prep_open and prep_customer is not None:

            snack = prep_customer.wanted_snack
            prep_type = SNACK_DATA[snack]["prep_type"]

            # darken game behind prep window
            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT), 
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 120))
            game_surface.blit(overlay, (0, 0))

            # main prep panel
            panel = pygame.Rect(
                170,
                70,
                500,
                330
            )

            draw_pixel_panel(
                game_surface, 
                panel, 
                background=LIBRARY_BG, 
                border=LIBRARY_BORDER, 
                highlight=LIBRARY_HIGHLIGHT, 
                shadow=LIBRARY_SHADOW
            )

            # title
            title = title_font.render(
                f"Prepare {snack.capitalize()}",
                True,
                LIBRARY_TEXT
            )
            title_rect = title.get_rect(
                center=(
                    panel.centerx, 
                    panel.top + 40 
                )
            )
            game_surface.blit(title, title_rect)


            # =====================================
            # ESQUITE
            # =====================================
            if prep_type == "sequence":

                steps = SNACK_DATA[snack]["steps"]
                current_step = steps[prep_step]

                instruction = font.render(
                    f"Next step: {current_step['text']}", 
                    True, 
                    LIBRARY_TEXT
                )
                game_surface.blit(
                    instruction, 
                    (
                        panel.left + 40, 
                        panel.top + 85 
                    )
                )

                ingredient_labels = [
                    "1 - Agregar elote", 
                    "2 - Agregar mayonesa", 
                    "3 - Agregar queso", 
                    "4 - Agregar tajin", 
                    "5 - Agregar limon"
                ]

                y = panel.top + 125 

                for index, label in enumerate(
                    ingredient_labels
                ): 
                    if index < prep_step: 
                        text_color = (
                            80, 
                            120, 
                            70 
                        )
                    elif index == prep_step: 
                        text_color = LIBRARY_TEXT 
                    else: 
                        text_color = (
                            100, 
                            90, 
                            75
                        )
                    step_text = font.render(
                        label, 
                        True, 
                        text_color 
                    )
                    game_surface.blit(
                        step_text, 
                        (
                            panel.left + 60, 
                            y
                        )
                    )
                    y += 34


                progress_text = small_font.render(
                    f"Step {prep_step + 1} / {len(steps)}",
                    True,
                    LIBRARY_TEXT
                )

                game_surface.blit(
                    progress_text, 
                    (
                        panel.left + 40, 
                        panel.bottom - 45
                    )
                )

                if prep_message != "": 
                    error_text = font.render(
                        prep_message, 
                        True, 
                        (150, 40, 35)
                    )
                    game_surface.blit(error_text, 
                        (
                            panel.right - error_text.get_width() - 40, 
                            panel.bottom - 50
                        )
                    )
                #game_surface.blit(instruction_text, (100, 195))


            # =====================================
            # RASPADO
            # =====================================
            elif prep_type == "flavor":

                request_text = font.render(
                    f"Customer wants: {prep_customer.flavor}",
                    True,
                    LIBRARY_TEXT
                )

                request_rect = request_text.get_rect(
                    center=(
                        panel.centerx, 
                        panel.top + 95 
                    )
                )

                game_surface.blit(
                    request_text, 
                    request_rect 
                )

                flavors = [
                    "1 - Vainilla", 
                    "2 - Fresa", 
                    "3 - Limon", 
                    "4 - Chicle Azul"
                ]

                y = panel.top + 145 

                for flavor in flavors: 
                    flavor_text = font.render(
                        flavor, 
                        True, 
                        LIBRARY_TEXT
                    )

                    flavor_rect = flavor_text.get_rect(
                        center=(
                            panel.centerx, 
                            y 
                        )
                    )
                    game_surface.blit(
                        flavor_text, 
                        flavor_rect 
                    )

                    y += 38

                if prep_message != "":
                    error_text = font.render(
                        prep_message,
                        True,
                        (150, 40, 35)
                    )

                    error_rect = error_text.get_rect(
                        center=(
                            panel.centerx, 
                            panel.bottom - 35
                        )
                    )

                    game_surface.blit(error_text, error_rect)
        # draw snack library 
        if library_open:

            # Darken background
            dark_overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT),
                pygame.SRCALPHA
            )

            dark_overlay.fill((0, 0, 0, 120))

            game_surface.blit(
                dark_overlay,
                (0, 0)
            )


            # ==============================
            # MAIN LIBRARY PANEL
            # ==============================

            library_margin = 30

            panel = pygame.Rect(
                library_margin,
                20,
                GAME_WIDTH - (library_margin * 2),
                GAME_HEIGHT - 40
            )

            draw_pixel_panel(
                game_surface,
                panel,
                background = LIBRARY_BG, 
                border = LIBRARY_BORDER, 
                highlight= LIBRARY_HIGHLIGHT, 
                shadow = LIBRARY_SHADOW
            )


            # Title
            title = title_font.render(
                "Snacks Library",
                True,
                PANEL_TEXT
            )

            game_surface.blit(
                title,
                (50, 40)
            )


            # ==============================
            # SNACK CARDS
            # ==============================

            snack_names = [
                "paleta",
                "esquite",
                "raspado"
            ]

            card_x = 50
            card_y = 85
            card_width = GAME_WIDTH - 100

            for snack in snack_names:

                data = SNACK_DATA[snack]

                unlocked = (
                    snack in level_data["snacks"]
                )

                description_lines = wrap_text(
                    data["description"],
                    small_font,
                    card_width - 120
                )

                card_height = (
                    72
                    + len(description_lines) * 16
                )

                card_rect = pygame.Rect(
                    card_x,
                    card_y,
                    card_width,
                    card_height
                )


                # Different background for locked snacks
                if unlocked:
                    card_background = LIBRARY_CARD
                else: 
                    card_background = LIBRARY_LOCKED


                draw_pixel_panel(
                    game_surface,
                    card_rect,
                    background=card_background, 
                    border=LIBRARY_BORDER, 
                    highlight=LIBRARY_HIGHLIGHT, 
                    shadow = LIBRARY_SHADOW
                )


                # Snack icon
                icon = snack_icons[snack].copy()

                if not unlocked:

                    icon.fill(
                        (100, 100, 100, 255),
                        special_flags=pygame.BLEND_RGBA_MULT
                    )

                game_surface.blit(
                    icon,
                    (
                        card_x + 15,
                        card_y + 15
                    )
                )


                # Snack name
                name_text = font.render(
                    snack.capitalize(),
                    True,
                    LIBRARY_TEXT
                )

                game_surface.blit(
                    name_text,
                    (
                        card_x + 55,
                        card_y + 12
                    )
                )


                # Locked / unlocked
                if unlocked:
                    status = "Unlocked"

                else:
                    status = (
                        f"Unlocks Level "
                        f"{data['unlock_level']}"
                    )

                status_text = small_font.render(
                    status,
                    True,
                    LIBRARY_TEXT
                )

                game_surface.blit(
                    status_text,
                    (
                        card_rect.right
                        - status_text.get_width()
                        - 15,
                        card_y + 15
                    )
                )


                # Sale price
                price_text = small_font.render(
                    f"Sale price: ${data['sale_price']}",
                    True,
                    LIBRARY_TEXT
                )

                game_surface.blit(
                    price_text,
                    (
                        card_x + 55,
                        card_y + 38
                    )
                )


                # Description
                description_y = card_y + 60

                for line in description_lines:

                    description_text = (
                        small_font.render(
                            line,
                            True,
                            LIBRARY_TEXT
                        )
                    )

                    game_surface.blit(
                        description_text,
                        (
                            card_x + 55,
                            description_y
                        )
                    )

                    description_y += 16


                # Next card
                card_y += card_height + 8


            # Close instruction
            close_text = small_font.render(
                "Press L to close",
                True,
                PANEL_TEXT
            )

            game_surface.blit(
                close_text,
                (
                    panel.right
                    - close_text.get_width()
                    - 15,
                    panel.bottom - 22
                )
            )
        if level_intro_open:

            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT), 
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 120))
            game_surface.blit(overlay, (0, 0))

            panel_width = 520
            panel_height = 320

            panel_x = (GAME_WIDTH - panel_width) // 2
            panel_y = (GAME_HEIGHT - panel_height) // 2

            panel = pygame.Rect(
                panel_x,
                panel_y,
                panel_width,
                panel_height
            )

            draw_pixel_panel(
                game_surface, 
                panel 
            )

            # level number
            if current_day == 0: 
                level_heading = "Tutorial"
            else: 
                level_heading = f"Day {current_day}"
            level_text = title_font.render(
                level_heading, 
                True,
                (45, 35, 25)
            )

            game_surface.blit(
                level_text,
                (panel_x + 30, panel_y + 25)
            )

            # level title
            intro_title = font.render(
                level_data["title"],
                True,
                (45, 35, 25)
            )

            game_surface.blit(
                intro_title,
                (panel_x + 30, panel_y + 70)
            )

            # goal
            goal_text = font.render(
                f"Goal: ${PROFIT_GOAL}",
                True,
                (45, 35, 25)
            )

            game_surface.blit(
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

            game_surface.blit(
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

                game_surface.blit(
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

            game_surface.blit(start_text, start_rect)

        if paleta_order_open and paleta_customer is not None:

            # darken the background slightly
            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 100)
            )

            game_surface.blit(
                overlay,
                (0, 0)
            )

            # main customer order panel
            order_panel = pygame.Rect(
                180,
                70,
                480,
                300
            )

            draw_pixel_panel(
                game_surface,
                order_panel,
                background=LIBRARY_BG,
                border=LIBRARY_BORDER,
                highlight=LIBRARY_HIGHLIGHT,
                shadow=LIBRARY_SHADOW
            )

            # title
            order_title = title_font.render(
                "CLIENTE",
                True,
                LIBRARY_TEXT
            )

            order_title_rect = order_title.get_rect(
                center=(
                    order_panel.centerx,
                    order_panel.top + 35
                )
            )

            game_surface.blit(
                order_title,
                order_title_rect
            )

            # customer portrait area
            portrait_rect = pygame.Rect(
                order_panel.left + 30,
                order_panel.top + 75,
                160,
                140
            )

            draw_pixel_panel(
                game_surface,
                portrait_rect,
                background=LIBRARY_CARD,
                border=LIBRARY_BORDER,
                highlight=LIBRARY_HIGHLIGHT,
                shadow=LIBRARY_SHADOW
            )

            portrait_image = pygame.transform.scale(
                customer_portrait_image,
                (120, 120)
            )

            portrait_image_rect = portrait_image.get_rect(
                center=portrait_rect.center
            )

            game_surface.blit(
                portrait_image,
                portrait_image_rect
            )
            # order text
            request_label = font.render(
                "PIDE:",
                True,
                LIBRARY_TEXT
            )

            game_surface.blit(
                request_label,
                (
                    order_panel.left + 230,
                    order_panel.top + 90
                )
            )

            snack_text = font.render(
                "Paleta",
                True,
                LIBRARY_TEXT
            )

            game_surface.blit(
                snack_text,
                (
                    order_panel.left + 230,
                    order_panel.top + 130
                )
            )

            flavor_text = title_font.render(
                paleta_customer.flavor.capitalize(),
                True,
                (150, 60, 60)
            )

            game_surface.blit(
                flavor_text,
                (
                    order_panel.left + 230,
                    order_panel.top + 165
                )
            )

            # instruction / feedback
            message_lines = wrap_text(
                paleta_message,
                small_font,
                order_panel.width - 60
            )

            message_y = order_panel.bottom - 65

            for line in message_lines:

                message_text = small_font.render(
                    line,
                    True,
                    LIBRARY_TEXT
                )

                game_surface.blit(
                    message_text,
                    (
                        order_panel.left + 30,
                        message_y
                    )
                )

                message_y += 18

        if current_day == 0 and not level_intro_open and not day_over:

            tutorial_panel = pygame.Rect(
                120,
                325, 
                600, 
                150
            )

            draw_pixel_panel(
                game_surface,
                tutorial_panel, 
                background = PANEL_YELLOW, 
                border = PANEL_BORDER, 
                highlight=PANEL_HIGHLIGHT, 
                shadow = PANEL_SHADOW
            )

            tutorial_lines = wrap_text(
                tutorial_message, 
                small_font, 
                tutorial_panel.width - 40
            )

            line_y = tutorial_panel.top + 20 

            for line in tutorial_lines: 
                tutorial_text = small_font.render(
                    line, 
                    True, 
                    PANEL_TEXT
                )
                game_surface.blit(
                    tutorial_text, 
                    (
                        tutorial_panel.left + 20, 
                        line_y
                    )
                )
                line_y += 20
            if tutorial_feedback:

                feedback_lines = wrap_text(
                    tutorial_feedback,
                    small_font,
                    tutorial_panel.width - 40
                )

                line_y += 8

                for line in feedback_lines:

                    feedback_text = small_font.render(
                        line,
                        True,
                        (120, 60, 20)
                    )

                    game_surface.blit(
                        feedback_text,
                        (
                            tutorial_panel.left + 20,
                            line_y
                        )
                    )

                    line_y += 20

        scaled_game = pygame.transform.scale(
            game_surface, 
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        screen.blit(
            scaled_game, 
            (0, 0)
        )

        if blockly_debug_message: 
            debug_text = small_font.render(
                blockly_debug_message, 
                True, 
                (255, 255, 255)
            )
            game_surface.blit(
                debug_text, 
                (10, GAME_HEIGHT - 25)
            )
        pygame.display.flip()
        #pygame.time.delay(17)

        await asyncio.sleep(0) #yield control back to browser event loop every frame
    pygame.quit()

asyncio.run(main()) # run async main function 