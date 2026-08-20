import pygame

class TileKind: 
    def __init__(self, name, image, is_solid): 
        self.name = name
        self.image = pygame.image.load(image)
        self.is_solid = is_solid

class Map: 
    def __init__(self, map_file, tile_kinds, tile_size): 
        self.tile_kinds = tile_kinds

        # load the file 
        file = open(map_file, "r")
        data = file.read()
        file.close()

        # set up tiles from loaded data
        self.tiles = []
        for line in data.split("\n"):
            row = []
            for tile_number in line:
                row.append(int(tile_number))

            self.tiles.append(row)

        # set size
        self.tile_size = tile_size

    def draw(self, screen):

        # If the map is just one tile,
        # scale that image to fill the whole game surface.
        if len(self.tiles) == 1 and len(self.tiles[0]) == 1:

            tile = self.tiles[0][0]

            image = self.tile_kinds[tile].image

            scaled_image = pygame.transform.scale(
                image,
                screen.get_size()
            )

            screen.blit(
                scaled_image,
                (0, 0)
            )

            return

        # Normal tile-map drawing
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):

                location = (
                    x * self.tile_size,
                    y * self.tile_size
                )

                image = self.tile_kinds[tile].image

                screen.blit(
                    image,
                    location
                )