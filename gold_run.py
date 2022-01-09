import pygame
import sys
import os
from PIL import Image


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


pygame.init()
FPS = 60
size = WIDTH, HEIGHT = 700, 800
clock = pygame.time.Clock()
tile_width = tile_height = 50
STEP = 5
ALIVE = True
WIN = False
ground_y = set()

tileset_1 = load_image('morning_adventures_tileset_16x16.png')
bush = pygame.Surface.subsurface(tileset_1, (112, 64, 16, 16))
ground_island = pygame.Surface.subsurface(tileset_1, (50, 48, 12, 16))
ground_row = pygame.Surface.subsurface(tileset_1, (0, 48, 48, 16))
spikes = pygame.Surface.subsurface(tileset_1, (80, 80, 16, 16))

tile_images = {
    'bush': pygame.transform.scale(bush, (50, 50)),
    'ground_island': pygame.transform.scale(ground_island, (50, 50)),
    'ground_block': pygame.transform.scale(ground_row, (150, 50)),
    'spikes': pygame.transform.scale(spikes, (50, 50))
}
player_width, player_height = Image.open('data/run2.png').size
print(player_height)
spike_image = pygame.transform.scale(spikes, (50, 50))

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
finish_group = pygame.sprite.Group()


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


class Spike(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(spikes_group, all_sprites)
        self.image = spike_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, y_add=0):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * x, tile_height * y - y_add)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(background_group)
        self.image = pygame.transform.scale(load_image('sky_background.png'), (700, 800))
        self.rect = self.image.get_rect().move(0, 0)


class Finish(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(finish_group, all_sprites)
        self.image = pygame.transform.scale(load_image('finish.png'), (1000, 800))
        self.rect = self.image.get_rect().move(2500, 0)
        self.mask = pygame.mask.from_surface(self.image)


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
    BackGround()
    finish = Finish()
    spikes_lst = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                continue
            elif level[y][x] == '#':
                Spike(x, y)
                spikes_lst.append(Spike(x, y))
            elif level[y][x] == '@':
                new_player = AnimatedSprite(load_image('run2.png'), 8, 1, x, y, 9)
            elif level[y][x] == '_':
                a = Tile('ground_island', x, y)
                global ground_y
                ground_y.add(a.rect.y - player_height)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y, spikes_lst, finish


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * -obj.rect.width
        obj.rect.x -= 200

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)


screen = pygame.display.set_mode(size)
start_screen()
player, level_x, level_y, sp_lst, finish = generate_level(load_level('lvl1.txt'))


def terminate():
    pygame.quit()
    sys.exit()


def jump():
    v = 280
    y_pos = player.rect.y
    jump_h = ground - 120
    global down_f
    if y_pos > jump_h and not down_f:
        y_pos -= v * clock.tick() // 1000  # v * t в секундах
    if y_pos <= jump_h:
        down_f = True
        y_pos += v * clock.tick() // 1000  # v * t в секундах
    if down_f:
        y_pos += v * clock.tick() // 1000  # v * t в секундах
    if y_pos >= ground:
        global jump_f
        jump_f = False
        y_pos = ground
    player.rect.y = y_pos
    player.rect.x += 8


def message_window_win():
    col = pygame.Color('#640933')
    pygame.draw.rect(screen, col, (150, 250, 400, 250), 0)
    text = ['Поздравляем!', 'Вы прошли уровень!']
    text_coord = 250
    font = pygame.font.Font(None, 30)
    for line in text:
        string_rendered = font.render(line, True, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 155
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    button = pygame.Rect(160, 390, 380, 100)
    pygame.draw.rect(screen, pygame.Color('#ff7029'), button, 0)
    button_text = 'Вернуться в меню'


camera = Camera((level_x, level_y))
running = True
jump_f = False
count = 0
print(ground_y)
print(player.rect.y)
while running:
    count += 1
    if not jump_f:
        player.rect.x += STEP
    if count == 4 and ALIVE:
        player.update()
        count = 0
    screen.blit(player.image, (player.rect.x, player.rect.y))
    if pygame.sprite.collide_mask(player, finish):
        STEP = 0
        ALIVE = False
        WIN = True
        message_window_win()
    for event in pygame.event.get():
        all_sprites.update()
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and ALIVE:
            if event.key == pygame.K_UP and player.rect.y > sorted(list(ground_y))[0] and not jump_f:
                player.rect.y -= sorted(list(ground_y))[1] - sorted(list(ground_y))[0]
                print(player.rect.y)
            if event.key == pygame.K_DOWN and player.rect.y < sorted(list(ground_y))[2] and not jump_f:
                player.rect.y += sorted(list(ground_y))[1] - sorted(list(ground_y))[0]
                print(player.rect.y)
            if event.key == pygame.K_SPACE:
                if player.rect.y in ground_y:
                    ground = player.rect.y
                    down_f = False
                    jump_f = True
    if jump_f and ALIVE:
        jump()
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    clock.tick(FPS)
    pygame.display.flip()
    screen.fill((0, 0, 0))
    background_group.draw(screen)
    tiles_group.draw(screen)
    spikes_group.draw(screen)
    finish_group.draw(screen)
    player_group.draw(screen)
terminate()