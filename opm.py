import pygame, sys

pygame.init()

clock = pygame.time.Clock()

WINDOW_SIZE = (600, 400)

screen = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.set_caption("One Punch Man")

scroll = [0, 0]

def load_map(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    data = data.split("\n")
    map = []
    for row in data:
       map.append(list(row))
    return map

global saitama_frames
saitama_frames = {}

def animation(path, frames):
    global saitama_frames
    animation_name = path.split("/")[-1]
    saitama_frame_data = []
    n = 0
    for frame in frames:
        saitama_frame_id = animation_name+str(n)
        saitama_frame = path + "/"+saitama_frame_id+".png"
        image = pygame.image.load(saitama_frame)
        saitama_frames[saitama_frame_id] = image
        for i in range(frame):
            saitama_frame_data.append(saitama_frame_id)
        n += 1
    return saitama_frame_data

animation_database_opm = {}
animation_database_opm["idle"] = animation("player/entities/idle", [20,20,20,20,20,20,20,20,20,20,20,20,20,20])
animation_database_opm["walk"] = animation("player/entities/walk", [8,8,8,8,8,8,8,8,8,8,8])
animation_database_opm["punch"] = animation("player/entities/punch", [8,8,8,8,8,8,8])
animation_database_opm["kick"] = animation("player/entities/kick", [8,8,8,8,8,8,16])
action = "idle"
player_frames = 0
saitama_flip = False

punch_duration = 0

kick_duration = 0

background_scroll = 0.16

def change_actions(old_action, frames, new_action):
    if old_action != new_action:
        frames = 0
    return new_action, frames

game_map = load_map("map/game_map.txt")

player_image = pygame.image.load("player/player-removebg-preview.png").convert_alpha()
player_rect = pygame.Rect(100, 100, player_image.get_width(), player_image.get_height())

player_moving_right = False
player_moving_left = False

tile_image = pygame.image.load("map/country-platform-preview.png")

player_y_momentum = 0.2

player_image.set_colorkey((255, 255, 255))

def collision(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    rect.x += movement[0]
    collision_types = {"left":False, "right":False, "top":False, "bottom":False}
    collisions = collision(rect, tiles)
    for tile in collisions:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True
        if movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]
    collisions = collision(rect, tiles)
    for tile in collisions:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True
    return rect, collision_types

background_images = []

layer_speeds = [[0.1, 0], [0.2, 0.2], [0.3, 0.3], [0.4, 0.4], [0.5, 0.5], [0.6, 0.6],[0.7, 0.7]]

for i in range(6):
    frame_path = "map/city back/"+str(i)+".png"
    image = pygame.image.load(frame_path)
    image_copy = pygame.transform.scale(image, (600, 400))
    background_images.append([image_copy, layer_speeds[i]])

running = True

while running:


    # if background_scroll > 1:
    #     background_scroll = 0.16

    print(player_rect.x)

    scroll[0] += int((player_rect.x - scroll[0] - 270)/20)
    scroll[1] += int((player_rect.y - scroll[1] - 290)/20)

    tiles_rect = []

    screen.fill((135, 206, 235))

    for object in background_images:
        screen.blit(object[0], (0-scroll[0]*object[1][0], 0-scroll[1]*object[1][1]))
        background_scroll += 0.16

    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            if game_map[y][x] != '0':
                screen.blit(tile_image, (x*383-scroll[0], y*36-scroll[1]))
                tiles_rect.append(pygame.Rect(x*383, y*36, 383, 36))

    movement = [0, 0]

    if player_y_momentum > 10:
        player_y_momentum = 10
    movement[1] = player_y_momentum
    player_y_momentum += 0.4

    if player_moving_right:
        movement[0] = 2
        if action == "walk" and player_frames>=73:
            movement[0] += 2
    if player_moving_left:
        movement[0] = -2
        if action == "walk" and player_frames>=73:
            movement[0] -= 2
    player_rect, collisions = move(player_rect, movement, tiles_rect)

    if kick_duration > 0:
        action = "kick"
        kick_duration -= 1
        if collisions["bottom"] and movement[0] > 0:
           player_rect.x -= 1
    elif punch_duration > 0:
        action = "punch"
        punch_duration -= 1
    elif movement[0] == 0:
        action, player_frames = change_actions(action, player_frames, "idle")
    elif movement[0] > 0:
        saitama_flip = False
        action, player_frames = change_actions(action, player_frames, "walk")
    elif movement[0] < 0:
        saitama_flip = True
        action, player_frames = change_actions(action, player_frames, "walk")

    if player_frames >= len(animation_database_opm[action]):
        player_frames = 0

    if action == "walk" and player_frames == 87:
        player_frames = 73

    saitama_frame_id = animation_database_opm[action][player_frames]
    player_image = saitama_frames[saitama_frame_id]
    player_frames += 1

    bottom = player_rect.bottom
    player_rect = pygame.Rect(player_rect.x, 0, player_image.get_width(), player_image.get_height())
    player_rect.bottom = bottom

    screen.blit(pygame.transform.flip(player_image, saitama_flip, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player_y_momentum = -15
            if event.key == pygame.K_d:
                player_moving_right = True
            if event.key == pygame.K_a:
                player_moving_left = True
            if event.key == pygame.K_m:
                punch_duration = 56
            if event.key == pygame.K_k:
                kick_duration = 64
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player_moving_right = False
            if event.key == pygame.K_a:
                player_moving_left = False


    clock.tick(60)
    pygame.display.update()
