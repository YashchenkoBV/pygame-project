import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


pygame.init()
FPS = 60
size = WIDTH, HEIGHT = 550, 500
clock = pygame.time.Clock()
tile_width = tile_height = 50
STEP = 4
tileset = load_image('morning_adventures_tileset_16x16.png')
bush = pygame.Surface.subsurface(tileset, (112, 64, 16, 16))
ground_island = pygame.Surface.subsurface(tileset, (50, 48, 12, 16))
ground_row = pygame.Surface.subsurface(tileset, (0, 48, 48, 16))
tile_images = {
    'bush': pygame.transform.scale(bush, (50, 50)),
    'ground_island': pygame.transform.scale(ground_island, (50, 50)),
    'ground_block': pygame.transform.scale(ground_island, (150, 50))
}
player_image = load_image('mar.png')

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def start_screen():
    intro_text = ["Это временно"]

    fon = pygame.transform.scale(load_image('test_fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 370
    string_rendered = font.render(intro_text[0], True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


'''def strip_from_sheet(sheet, start, size, columns, rows):
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0]+size[0]*i, start[1]+size[1]*j)
            frames.append(sheet.sur)
    return frames'''


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                continue
            elif level[y][x] == '#':
                Tile('bush', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == '_':
                Tile('ground_island', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


screen = pygame.display.set_mode(size)
start_screen()
player, level_x, level_y = generate_level(load_level('lvl1.txt'))


def terminate():
    pygame.quit()
    sys.exit()


running = True
while running:
    for event in pygame.event.get():
        all_sprites.update()
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.rect.y -= STEP
            if event.key == pygame.K_DOWN:
                player.rect.y += STEP

    '''camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)'''

    clock.tick(FPS)
    pygame.display.flip()
    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)

terminate()