import pygame, sys

def ld_map(path):
    f = open(path, 'r')
    data = f.read()
    data = data.split("\n")
    map_ = []
    for row in data:
        map_.append(list(row))
    return map_

def collision_with_tiles(rect, tiles):
    hit_list_ = []
    for tile_ in tiles:
      if rect.colliderect(tile_):
         hit_list_.append(tile_)
    return hit_list_

def move(rect, movement, tiles):
    collision_types = {"top":False, "bottom":False, "right":False, "left":False}
    rect.x += movement[0]
    hit_list = collision_with_tiles(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True
        if movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True

    rect.y += movement[1]
    hit_list = collision_with_tiles(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True

    return rect, collision_types

global animation_frames
animation_frames = {}

def load_animations(path, frame_durations):
    global animation_frames
    animation_name = path.split("/")[-1]
    animation_frame_database = []
    n = 0
    for frame in frame_durations:
        saitama_frame_id = animation_name+str(n)
        saitama_frame = path + "/" + saitama_frame_id + ".png"
        image = pygame.image.load(saitama_frame)
        animation_frames[saitama_frame_id] = image
        for i in range(frame):
            animation_frame_database.append(saitama_frame_id)
        n += 1
    return animation_frame_database

def change_action(action_var, player_frame, new_action):
    if action_var != new_action:
        action_var = new_action
        player_frame = 0
    return action_var, player_frame

player_action = "idle"
player_frame = 0
player_flip = False

kick_duration = 0
punch_duration = 0

saitama_database = {}
saitama_database["idle"] = load_animations("player actions/idle", [20,20,20,20,20,20,20,20,20,20,20,20,20,20])
saitama_database["kick"] = load_animations("player actions/kick", [8,8,8,8,8,8,16])
saitama_database["punch"] = load_animations("player actions/punch", [8,8,8,8,8,8,8])
saitama_database["walk"] = load_animations("player actions/walk", [8,8,8,8,8,8,8,8,8,8,8])
saitama_database["boring"] = load_animations("player actions/boring", [10, 10, 10, 10])

boring_meter = 0

saitama_database["jump"] = load_animations("player actions/jump", [2, 10, 11, 12, 14, 15, 14, 13, 10, 6])
saitama_database["kick"] = load_animations("player actions/kick", [8,8,8,8,8,8,16])
saitama_database["punch"] = load_animations("player actions/punch", [8,8,8,8,8,8,8])

pygame.init()

clock = pygame.time.Clock()

WINDOW_SIZE = (600, 400)

pygame.display.set_caption("opm")

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

player_image = pygame.image.load("player actions/idle/idle0.png")

player_rect = pygame.Rect(50, 50, 24, 65)

tile_image = pygame.image.load("map/country-platform-preview.png")

gravity_pull = 0

moving_right = False
moving_left = False

game_map = ld_map("map/game_map.txt")

collisions = {"top":False, "bottom":True, "left":False, "right":False}

scroll = [0, 0]

continue_walking = False
cw = 0

background_layers = []
layer_speeds = [[0.1, 0], [0.2, 0.2], [0.3, 0.3], [0.4, 0.4], [0.5, 0.5]]

for i in range(5):
    frame_path = "map/city back/" + str(i) + ".png"
    image = pygame.image.load(frame_path)
    image_copy = pygame.transform.scale(image, (600, 400))
    background_layers.append([image_copy, layer_speeds[i]])

world_width = len(game_map[0])*383

left_boundary_rect = pygame.Rect(-50, 0, 50, 600)

right_boundary_rect = pygame.Rect(world_width, 0, 50, 600)

while True:

    scroll[0] += int((player_rect.x - scroll[0] - 270)/20)
    scroll[1] += int((player_rect.y - scroll[1] - 290)/20)

    # Scroll only when player is near screen edges
    # scroll_area_width = 150  # px from each side
    # if player_rect.centerx - scroll[0] < scroll_area_width:
    #     scroll[0] -= int(scroll_area_width - (player_rect.centerx - scroll[0]))
    # elif player_rect.centerx - scroll[0] > WINDOW_SIZE[0] - scroll_area_width:
    #     scroll[0] += int((player_rect.centerx - scroll[0]) - (WINDOW_SIZE[0] - scroll_area_width))

    scroll[0] = max(0, min(scroll[0], world_width - 600))

    off_set_y = 0

    screen.fill((146, 244, 255))

    no_of_blocks = int(world_width/600)
    #index_y is constant = 0
    # index_y = 0
    # for back_layer in background_layers:
    #    screen.blit(back_layer[0], (0-scroll[0]*back_layer[1][0], index_y-scroll[1]*back_layer[1][1]))

    for back_layer in background_layers:

        index_x = 0

        start_block = max(0, int(scroll[0] * back_layer[1][0] // 600) - 1)
        end_block = min(no_of_blocks, start_block + (WINDOW_SIZE[0] // 600) + 3)

        for i in range(start_block, end_block):
            x_pos = i * 600 - scroll[0] * back_layer[1][0]
            y_pos = -scroll[1] * back_layer[1][1]
            screen.blit(back_layer[0], (x_pos, y_pos))

    tiles_rect = []
    tiles_rect.append(left_boundary_rect)
    tiles_rect.append(right_boundary_rect)
    y = 0
    for row in game_map:
      x = 0
      for tile in row:
        if tile == "1":
            screen.blit(tile_image, (x*383-scroll[0], y*36-scroll[1]))
            if player_action == "walk":
              tiles_rect.append(pygame.Rect(x*383, y*36, 383, 36))
            else:
              tiles_rect.append(pygame.Rect(x*383, y*36, 383, 36))
        x += 1
      y += 1

    player_movement = [0, 0]

    if gravity_pull <= 5 and gravity_pull >= -9:
      gravity_pull += 0.2
    player_movement[1] += gravity_pull

    if moving_right:
        player_movement[0] = 2
        player_flip = False
        if player_frame == 87:
            player_frame = 73
        if player_frame in range(73, 87):
            player_movement[0] = 6

    if moving_left:
        player_movement[0] = -2
        player_flip = True
        if player_frame == 87:
            player_frame = 73
        if player_frame in range(73, 87):
            player_movement[0] = -6

    if (kick_duration > 0 or punch_duration) > 0 and collisions["bottom"]:
        player_movement[0] = 0

    player_rect, collisions = move(player_rect, player_movement, tiles_rect)

    if boring_meter > 200:
        player_action, player_frame = change_action(player_action, player_frame, "boring")
    elif kick_duration > 0:
        if player_action != "kick":
            player_action, player_frame = change_action(player_action, player_frame, "kick")
        kick_duration -= 1
    elif punch_duration > 0:
        if player_action != "punch":
            player_action, player_frame = change_action(player_action, player_frame, "punch")
        punch_duration -= 1
        if player_frame in range(15, 32):
            off_set_y = 10
        if player_frame in range(32, 55):
            off_set_y = 5
    elif player_movement[0] == 0 and player_action != "boring" and collisions["bottom"]:
        player_action, player_frame = change_action(player_action, player_frame, "idle")
        if cw == 0:
         continue_walking = False
        cw = 0
    elif player_action == "jump" and collisions["bottom"]:
        player_action, player_frame = change_action(player_action, player_frame, "idle")
        if cw == 0:
         continue_walking = False
        cw = 0
    elif collisions["bottom"] and player_action != "jump" and player_movement[0] != 0:
        player_action, player_frame = change_action(player_action, player_frame, "walk")
        if continue_walking:
            player_frame = 73
            continue_walking = False

    # if player_movement[0] == 0 and player_action != "boring" and collisions["bottom"]:
    #     player_action, player_frame = change_action(player_action, player_frame, "idle")
    # if player_action == "jump" and collisions["bottom"]:
    #     player_action, player_frame = change_action(player_action, player_frame, "idle")

    if player_movement[0] == 0 and collisions["bottom"]:
        boring_meter += 1
    else:
        boring_meter = 0

    # if boring_meter == 500:
    #     player_action, player_frame = change_action(player_action, player_frame, "boring")

    if player_action == "boring":
        if player_frame >= 10:
            off_set_y = 7
        if player_frame >= 20:
            off_set_y = 23
        if player_frame >= 30:
            off_set_y = 20
        if player_frame >= 39:
            player_frame = 30

    player_frame += 1
    if player_frame >= len(saitama_database[player_action]):
        player_frame = 0

    player_image = animation_frames[saitama_database[player_action][player_frame]]

    screen.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x-scroll[0], player_rect.y-scroll[1] + off_set_y + 8))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_d:
            moving_right = True
          if event.key == pygame.K_a:
            moving_left = True
          if event.key == pygame.K_k:
            kick_duration = 64
            punch_duration = 0
          if event.key == pygame.K_m:
            punch_duration = 56
            kick_duration = 0
          if event.key == pygame.K_w and collisions["bottom"]:
            if player_action == "walk" and player_frame in range(73, 88):
                continue_walking = True
            cw = 1
            gravity_pull = -9
            player_action, player_frame = change_action(player_action, player_frame, "jump")
            player_frame = 0

        if event.type == pygame.KEYUP:
          if event.key == pygame.K_d:
            moving_right = False
          if event.key == pygame.K_a:
            moving_left = False

    pygame.display.update()
    clock.tick(60)