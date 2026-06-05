import pygame
import sys
import json

# Start the Pygame engine engine
pygame.init()

# Setup screen measurements
TILE_SIZE = 40  # Each game block is 40x40 pixels
SCREEN_WIDTH = 640   # 16 columns of tiles
SCREEN_HEIGHT = 480  # 12 rows of tiles

# Open the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Chrono Chronicles")
clock = pygame.time.Clock()

# Define colors using RGB values (Red, Green, Blue)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GREY = (100, 100, 100)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
BLUE = (30, 144, 255)
DARK_GREEN = (0, 100, 0)
AQUA = (0, 255, 255)  # NPC color
RED = (255, 0, 0)     # Enemy color
PINK = (255, 105, 180)   # Pendant color
ORANGE = (255, 140, 0)   # Sword color
WHITE = (255, 255, 255) # Text color

# Initialize Pygame's Font Module
pygame.font.init()
# Create a font object (None uses the default system font, 24 is the pixel size)
game_font = pygame.font.Font(None, 24)

controls = {
    "MOVE_UP":    pygame.K_UP,     # Alternative: pygame.K_w
    "MOVE_DOWN":  pygame.K_DOWN,   # Alternative: pygame.K_s
    "MOVE_LEFT":  pygame.K_LEFT,   # Alternative: pygame.K_a
    "MOVE_RIGHT": pygame.K_RIGHT   # Alternative: pygame.K_d
}

# loading in the date from the JSON files
# Change your function to accept a filename parameter
def load_data(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: {filename} is missing!")
        return {}

# Now you can load both super cleanly!
world_zones = load_data("maps.json")
enemy_data = load_data("enemies.json")
tile_images = {
    0: pygame.image.load("grass.png").convert_alpha(),
    1: pygame.image.load("wall.png").convert_alpha(),
    2: pygame.image.load("door.png").convert_alpha(),       # NEW!
    3: pygame.image.load("key.png").convert_alpha(),        # NEW!
    4: pygame.image.load("water.png").convert_alpha(),
    5: pygame.image.load("tall_grass.png").convert_alpha(),
    6: pygame.image.load("pendant.png").convert_alpha(),    # NEW!
    7: pygame.image.load("sword_pickup.png").convert_alpha() # NEW!
}
npc_image = pygame.image.load("npc.png").convert_alpha()
# Load UI Images
heart_img = pygame.image.load("heart.png").convert_alpha()
ui_key_img = pygame.image.load("ui_key.png").convert_alpha()
ui_sword_img = pygame.image.load("ui_sword.png").convert_alpha()
ui_pendant_img = pygame.image.load("ui_pendant.png").convert_alpha()
class Player: # Capitalized!
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.has_key = False
        self.has_weapon = False
        self.has_pendant = False
        self.facing = (0, 1) # Default facing down
        self.current_zone = "Zone_A"
        self.is_invincible = False
        self.invincible_timer = 0
        # --- ANIMATION LOGIC ---
        # Load both frames into a list
        self.move_cooldown = 0
        self.walk_frames = [
            pygame.image.load("player_walk1.png").convert_alpha(),
            pygame.image.load("player_walk2.png").convert_alpha()
        ]
        self.current_frame = 0 # Index for the list (0 or 1)
        self.image = self.walk_frames[self.current_frame] # The active image
        self.animation_timer = 0

        self.attack_timer = 0  # Counts down the swing
        self.base_slash = pygame.image.load("slash.png").convert_alpha() # The un-rotated slash
        self.slash_image = self.base_slash # This will hold the rotated version

    def check_wall(self, next_x, next_y, current_zone_map):
        # Dynamically check the map size!
        map_width = len(current_zone_map[0])
        map_height = len(current_zone_map)
        
        if next_x < 0 or next_x >= map_width or next_y < 0 or next_y >= map_height: 
            return False
        
        tile = current_zone_map[next_y][next_x]
        if tile in [0, 5]: return True 
        return False 

    def take_damage(self, enemy_attack):
        if not self.is_invincible:
            self.hp -= enemy_attack
            print(f"Ouch! HP is now {self.hp}")
            
            if self.hp <= 0:
                print("Game Over! You have been defeated.")
                self.hp = 0 
            else:
                # SURVIVED! Give i-frames and knockback
                self.is_invincible = True
                self.invincible_timer = 60
                
                knockback_x = self.x + (self.facing[0] * 2)
                knockback_y = self.y + (self.facing[1] * 2)
                
                self.x = max(0, min(15, knockback_x))
                self.y = max(0, min(11, knockback_y))
                
    def update(self):
        if self.is_invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False
                
        # --- ANIMATION LOGIC ---
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            self.animation_timer += 1
            if self.animation_timer >= 8:
                self.animation_timer = 0
                if self.current_frame == 0: self.current_frame = 1
                else: self.current_frame = 0
        else:
            self.current_frame = 0
            self.animation_timer = 0
            
        self.image = self.walk_frames[self.current_frame]

        # --- ATTACK LOGIC ---
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
            # Rotate the slash based on facing direction!
            if self.facing == (0, 1):   angle = -90
            elif self.facing == (0, -1): angle = 90
            elif self.facing == (-1, 0): angle = 180
            else:                        angle = 0 # Right

            self.slash_image = pygame.transform.rotate(self.base_slash, angle)
            
            # FADE OUT EFFECT: As timer goes down, alpha (transparency) goes down!
            # Timer is 15 to 0. Alpha is 255 to 0.
            alpha = int((self.attack_timer / 15) * 255)
            self.slash_image.set_alpha(alpha)

class Enemy:
    def __init__(self, name, x, y, zone, hp, attack, speed, patrol_direction, aggro_range):
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.patrol_direction = patrol_direction
        self.aggro_range = aggro_range
        self.image = pygame.image.load("guard.png").convert_alpha() # Load the guard sprite
        
        self.dir = 1 # 1 or -1, used for patrolling back and forth
        self.timer = 0
        self.is_alive = True

    def update(self, player, current_zone_map):
        self.timer += 1
        if self.timer < self.speed:
            return 
        
        self.timer = 0 

        if player.current_zone == self.zone:
            # Calculate distance and maybe chase.
            dist_x = abs(player.x - self.x)
            dist_y = abs(player.y - self.y)
            total_distance = dist_x + dist_y

            if total_distance <= self.aggro_range: self.chase_player(player, current_zone_map)
            else: self.patrol(current_zone_map)
        else: self.patrol(current_zone_map) # No! Player is in a different zone. Just patrol normally.

    def check_wall(self, next_x, next_y, current_zone_map):
        # Dynamically check the map size!
        map_width = len(current_zone_map[0])
        map_height = len(current_zone_map)
        
        if next_x < 0 or next_x >= map_width or next_y < 0 or next_y >= map_height: 
            return False
        
        tile = current_zone_map[next_y][next_x]
        if tile in [0, 5]: return True 
        return False 

    def chase_player(self, player, current_zone_map):
        dx = player.x - self.x # Positive = player is right, Negative = player is left
        dy = player.y - self.y # Positive = player is down, Negative = player is up
        
        next_x = self.x
        next_y = self.y

        # Move on the axis that has the biggest gap first
        # This makes the enemy take a diagonal-looking path towards you
        if abs(dx) > abs(dy):
            if dx > 0: next_x += 1 # Step right
            else: next_x -= 1      # Step left
        else:
            if dy > 0: next_y += 1 # Step down
            else: next_y -= 1      # Step up
        
        # Only actually move if we didn't hit a wall!
        if self.check_wall(next_x, next_y, current_zone_map):
            self.x = next_x
            self.y = next_y

    def patrol(self, current_zone_map):
        next_x = self.x
        next_y = self.y

        # Move based on what the JSON told us this enemy does
        if self.patrol_direction == "vertical":
            next_y += self.dir # Move up or down
        else: # horizontal
            next_x += self.dir # Move left or right

        # Check if we hit a wall
        if self.check_wall(next_x, next_y, current_zone_map):
            self.x = next_x
            self.y = next_y
        else:
            # We hit a wall! Turn around!
            self.dir *= -1 # If dir was 1, it becomes -1. If -1, becomes 1.
# The Master Dictionary! Holds ALL enemies in the game.
global_enemies = {} 
# The list of enemies currently in the room with the player
active_enemies = [] 
def load_all_enemies():
    global global_enemies
    global_enemies = {} # Clear the master list completely
    
    # Loop through every zone in the JSON
    for zone_name, enemy_list in enemy_data.items():
        # Create an empty list for this zone in our dictionary
        global_enemies[zone_name] = []
        
        # Loop through enemies in this zone and create them
        for enemy_info in enemy_list:
            new_enemy = Enemy(
                name=enemy_info["name"],
                x=enemy_info["x"],
                y=enemy_info["y"],
                zone=zone_name,
                hp=enemy_info["hp"],
                attack=enemy_info["attack"],
                speed=enemy_info["speed"],
                patrol_direction=enemy_info["patrol_direction"],
                aggro_range=enemy_info["aggro_range"]
            )
            # Add them to the master dictionary under their room name
            global_enemies[zone_name].append(new_enemy)
def load_room(zone_name):
    global active_enemies
    # Grab the list of enemies for this zone from the master dictionary
    # If the zone has no enemies, default to an empty list []
    active_enemies = global_enemies.get(zone_name, [])
npc_x, npc_y = 3, 8
npc_zone = "Zone_A"
npc_message = ""  # Holds the live dialog box text on screen

def draw_text(message, color, x, y):
    # True enables anti-aliasing (smooths out the pixel edges)
    text_surface = game_font.render(message, True, color)
    screen.blit(text_surface, (x, y))


def try_move(dx, dy):
    
    # Always track the last direction the player moved!
    player.facing = (dx, dy)
    
    next_x = player.x + dx
    next_y = player.y + dy
    
    
    # ZONE_A -> ENTER ZONE_B (Going Right)
    if player.current_zone == "Zone_A" and next_x > 15:
        # Return: (new_zone, target_x, target_y, transition_direction, previous_zone)
        return ("Zone_B", 0, player.y, (1, 0), "Zone_A")

    # ZONE_B HUB NAVIGATIONS
    elif player.current_zone == "Zone_B":
        if next_x < 0:      # Walked Left -> Zone_A
            return ("Zone_A", 15, player.y, (-1, 0), "Zone_B")
        elif next_x > 15:   # Walked Right -> Zone_E
            return ("Zone_E", 0, player.y, (1, 0), "Zone_B")
        elif next_y < 0:    # Walked Up -> Zone_C
            return ("Zone_C", next_x, 11, (0, -1), "Zone_B")
        elif next_y > 11:   # Walked Down -> Zone_D
            return ("Zone_D", next_x, 0, (0, 1), "Zone_B")

    # RETURNING TO THE CENTRAL HUB
    elif player.current_zone == "Zone_C" and next_y > 11: 
        return ("Zone_B", next_x, 0, (0, 1), "Zone_C")
        
    elif player.current_zone == "Zone_D" and next_y < 0:  
        return ("Zone_B", next_x, 11, (0, -1), "Zone_D")
        
    elif player.current_zone == "Zone_E" and next_x < 0:  
        return ("Zone_B", 15, player.y, (-1, 0), "Zone_E")
    
    target_tile = world_zones[player.current_zone][next_y][next_x]
    
    if target_tile in [0, 5]:
        if player.current_zone == "Zone_A" and next_x == npc_x and next_y == npc_y:
            print("Ouch! Bumped into the NPC.") 
            return None
            
        player.x = next_x
        player.y = next_y
    elif target_tile == 3: # Key
        player.has_key = True
        world_zones[player.current_zone][next_y][next_x] = 0
        player.x = next_x
        player.y = next_y
    elif target_tile == 2: # Door
        if player.has_key:
            world_zones[player.current_zone][next_y][next_x] = 0
            player.has_key = False
            player.x = next_x
            player.y = next_y
    elif target_tile == 6: # Pendant
        player.has_pendant = True
        world_zones[player.current_zone][next_y][next_x] = 0
        player.x = next_x
        player.y = next_y
    elif target_tile == 7: # Sword
        player.has_weapon = True
        world_zones[player.current_zone][next_y][next_x] = 0
        player.x = next_x
        player.y = next_y
        
    return None # No transition happened

player = Player(1, 1)
game_running = True
game_state = "MENU" # Start at the menu now!
# (Remove load_all_enemies and load_room from here, we will put them in a setup function)

def start_new_game():
    global global_enemies, active_enemies
    player.x = 1
    player.y = 1
    player.hp = 3
    player.has_key = False
    player.has_weapon = False
    player.has_pendant = False
    player.facing = (0, 1)
    player.current_zone = "Zone_A"
    player.is_invincible = False
    
    # Reset the map! (Reload it from JSON to restore picked up items)
    global world_zones
    world_zones = load_data("maps.json")
    
    # Spawn enemies fresh
    load_all_enemies()
    load_room(player.current_zone)

def save_game():
    print("Saving Game...")
    save_data = {
        "player": {
            "x": player.x, "y": player.y, "hp": player.hp,
            "has_key": player.has_key, "has_weapon": player.has_weapon,
            "has_pendant": player.has_pendant, 
            "facing": list(player.facing), # Tuples become lists in JSON!
            "current_zone": player.current_zone
        },
        "world_zones": world_zones # Saves which keys/doors you've picked up!
    }
    
    # Save Enemy Data (We have to extract it from the objects)
    enemy_save_data = {}
    for zone_name, enemies in global_enemies.items():
        enemy_save_data[zone_name] = []
        for e in enemies:
            enemy_save_data[zone_name].append({
                "name": e.name, "x": e.x, "y": e.y, "zone": e.zone,
                "hp": e.hp, "attack": e.attack, "speed": e.speed,
                "patrol_direction": e.patrol_direction, "aggro_range": e.aggro_range,
                "is_alive": e.is_alive, "dir": e.dir # CRITICAL: Remember if they are dead!
            })
            
    save_data["enemies"] = enemy_save_data
    
    with open("save.json", "w") as file:
        json.dump(save_data, file)
    print("Game Saved!")

def load_game():
    global global_enemies, active_enemies, world_zones
    print("Loading Game...")
    try:
        with open("save.json", "r") as file:
            save_data = json.load(file)
            
        # 1. Load Player
        p_data = save_data["player"]
        player.x = p_data["x"]
        player.y = p_data["y"]
        player.hp = p_data["hp"]
        player.has_key = p_data["has_key"]
        player.has_weapon = p_data["has_weapon"]
        player.has_pendant = p_data["has_pendant"]
        player.facing = tuple(p_data["facing"]) # Convert list back to tuple!
        player.current_zone = p_data["current_zone"]
        player.is_invincible = False
        
        # 2. Load Map State
        world_zones = save_data["world_zones"]
        
        # 3. Load Enemy State
        global_enemies = {}
        for zone_name, enemies_data in save_data["enemies"].items():
            global_enemies[zone_name] = []
            for e_data in enemies_data:
                # Re-create the enemy object from saved data
                loaded_enemy = Enemy(
                    name=e_data["name"], x=e_data["x"], y=e_data["y"], zone=e_data["zone"],
                    hp=e_data["hp"], attack=e_data["attack"], speed=e_data["speed"],
                    patrol_direction=e_data["patrol_direction"], aggro_range=e_data["aggro_range"]
                )
                loaded_enemy.is_alive = e_data["is_alive"]
                loaded_enemy.dir = e_data["dir"]
                global_enemies[zone_name].append(loaded_enemy)
                
        load_room(player.current_zone)
        return True
        
    except FileNotFoundError:
        print("No save file found!")
        return False

transition_offset = 0      # How far the screen has slid (0 to 640 or 480)
transition_speed = 40      # How fast it slides (pixels per frame). 40 is fast and snappy!
transition_dir = (0, 0)    # Which way is it sliding? (1,0) right, (-1,0) left, (0,1) down, (0,-1) up
previous_zone = ""         # The zone we are leaving
target_zone = ""           # The zone we are entering
target_x = 0               # Where the player will end up in the new zone
target_y = 0

while game_running:
    
    # --- 1. EVENT HANDLING (Always runs) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            game_running = False 
        
        if game_state == "MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # Enter key
                    start_new_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_l: # L key to load
                    if load_game():
                        game_state = "PLAYING"
            
        # Only allow movement/attacking if we are PLAYING
        elif game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                transition_info = None # Reset check
                
                if event.key == controls["MOVE_LEFT"]: 
                    transition_info = try_move(-1, 0)
                    if not transition_info: player.move_cooldown = 15
                elif event.key == controls["MOVE_RIGHT"]: 
                    transition_info = try_move(1, 0)
                    if not transition_info: player.move_cooldown = 15
                elif event.key == controls["MOVE_UP"]: 
                    transition_info = try_move(0, -1)
                    if not transition_info: player.move_cooldown = 15
                elif event.key == controls["MOVE_DOWN"]: 
                    transition_info = try_move(0, 1)
                    if not transition_info: player.move_cooldown = 15
                elif event.key == pygame.K_q: save_game() # Quick Save with F5!
                elif event.key == pygame.K_ESCAPE: # BACK TO MENU (Auto-saves!)
                    save_game() 
                    game_state = "MENU"
                elif event.key == pygame.K_SPACE: 
                    # Only attack if we have a weapon AND we aren't already attacking!
                    if player.has_weapon and player.attack_timer == 0:
                        attack_x = player.x + player.facing[0]
                        attack_y = player.y + player.facing[1]
                        for enemy in active_enemies:
                            if enemy.is_alive and player.current_zone == enemy.zone and attack_x == enemy.x and attack_y == enemy.y:
                                enemy.is_alive = False
                                print(f"{enemy.name} eliminated!")
                        player.attack_timer = 15 # Increased to 15 frames
                
                # Did try_move tell us to start a transition?
                if transition_info:
                    target_zone, target_x, target_y, t_dir, prev_zone = transition_info
                    transition_dir = t_dir
                    previous_zone = prev_zone
                    transition_offset = 0
                    game_state = "TRANSITION"
        
        # Only allow Restarting if we are GAMEOVER
        elif game_state == "GAMEOVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    start_new_game()
                    game_state = "PLAYING"

    # --- 2. LOGIC UPDATES (Only if PLAYING) ---
    if game_state == "PLAYING":
        player.update()
        for enemy in active_enemies:
            if enemy.is_alive:
                enemy.update(player, world_zones[enemy.zone])

        for enemy in active_enemies:
            if enemy.is_alive and player.current_zone == enemy.zone and player.x == enemy.x and player.y == enemy.y:
                player.take_damage(enemy.attack)

        if player.hp <= 0:
            game_state = "GAMEOVER"

        if npc_x is not None and player.current_zone == npc_zone:
            dist_x = abs(player.x - npc_x)
            dist_y = abs(player.y - npc_y)
            if dist_x <= 1 and dist_y <= 1:
                if player.has_pendant:
                    npc_message = "NPC: 'Wow, the pendant! Go ahead, the path is open.'"
                    npc_x, npc_y = None, None
                    player.has_pendant = False
                else: npc_message = "NPC: 'Bring me my missing placeholder item...'"
            else: npc_message = ""
        else: npc_message = ""
    
    elif game_state == "TRANSITION":
        # Move the offset based on the direction
        if transition_dir[0] != 0: # Horizontal slide
            transition_offset += transition_speed
        elif transition_dir[1] != 0: # Vertical slide
            transition_offset += transition_speed

        # Check if the slide is finished (Offset reached screen width or height)
        if transition_offset >= SCREEN_WIDTH or transition_offset >= SCREEN_HEIGHT:
            player.current_zone = target_zone
            player.x = target_x
            player.y = target_y
            
            # Load the enemies for the new room from memory!
            load_room(player.current_zone)
            
            game_state = "PLAYING"

        # --- 3. RENDERING ---
    screen.fill(BLACK)
    if game_state == "MENU":
        # Draw Title
        draw_text("THE CHRONO CHRONICLES", GOLD, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 60)
        # Draw Instructions
        draw_text("Press ENTER to Start", WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
        draw_text("Press L to Load Game", AQUA, SCREEN_WIDTH // 2 - 102, SCREEN_HEIGHT // 2 + 40)
        draw_text("Press ESC to Return to Menu", AQUA, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 80)
        
    else:
        # Determine which zones to draw and their offsets
        zones_to_draw = []
        if game_state == "TRANSITION":
            # The old zone slides OUT
            out_x = -transition_offset * transition_dir[0]
            out_y = -transition_offset * transition_dir[1]
            zones_to_draw.append((previous_zone, out_x, out_y))
            
            # The new zone slides IN
            in_x = SCREEN_WIDTH * transition_dir[0] - transition_offset * transition_dir[0]
            in_y = SCREEN_HEIGHT * transition_dir[1] - transition_offset * transition_dir[1]
            zones_to_draw.append((target_zone, in_x, in_y))
        else:
            # Normal gameplay, just draw the current zone with no offset
            zones_to_draw.append((player.current_zone, 0, 0))

        # Draw Map (Now actually uses the offsets!)
        for zone_name, offset_x, offset_y in zones_to_draw:
            if zone_name not in world_zones: continue
            
            for row_index in range(len(world_zones[zone_name])):
                for col_index in range(len(world_zones[zone_name][row_index])):
                    x_pixel = (col_index * TILE_SIZE) + offset_x
                    y_pixel = (row_index * TILE_SIZE) + offset_y
                    
                    if -TILE_SIZE < x_pixel < SCREEN_WIDTH and -TILE_SIZE < y_pixel < SCREEN_HEIGHT:
                        tile_type = world_zones[zone_name][row_index][col_index]
                        
                        # ALWAYS draw the floor (Grass) under items so the background isn't black!
                        # 3 = Key, 6 = Pendant, 7 = Sword Pickup
                        if tile_type in [3, 6, 7]: 
                            screen.blit(tile_images[0], (x_pixel, y_pixel)) # 0 is Grass
                        
                        # Then draw the actual tile on top
                        if tile_type in tile_images:
                            screen.blit(tile_images[tile_type], (x_pixel, y_pixel))

        # Draw Player (Only if PLAYING)
        if game_state == "PLAYING":
            if not player.is_invincible or player.invincible_timer % 10 < 5: 
                player_draw_x = player.x * TILE_SIZE
                player_draw_y = player.y * TILE_SIZE
                screen.blit(player.image, (player_draw_x, player_draw_y))
                
                if player.attack_timer > 0 and player.has_weapon:
                    slash_x = (player.x + player.facing[0]) * TILE_SIZE
                    slash_y = (player.y + player.facing[1]) * TILE_SIZE
                    screen.blit(player.slash_image, (slash_x, slash_y))
            # Draw Entities (Only if PLAYING)
        if game_state == "PLAYING":
            if player.current_zone == npc_zone:
                if npc_x is not None: 
                    screen.blit(npc_image, (npc_x * TILE_SIZE, npc_y * TILE_SIZE))
                    
            # Draw ALL active enemies!
            for enemy in active_enemies:
                if enemy.is_alive: screen.blit(enemy.image, (enemy.x * TILE_SIZE, enemy.y * TILE_SIZE))
        
        # ---Draw UI---
        # 1. Draw Hearts
        for i in range(player.hp):
            screen.blit(heart_img, (20 + (i * 25), 15))

        # 2. Draw Inventory Icons
        inv_x_pos = 20
        inv_y_pos = 45
        if player.has_key: 
            screen.blit(ui_key_img, (inv_x_pos, inv_y_pos))
            inv_x_pos += 25
        if player.has_weapon: 
            screen.blit(ui_sword_img, (inv_x_pos, inv_y_pos))
            inv_x_pos += 25
        if player.has_pendant: 
            screen.blit(ui_pendant_img, (inv_x_pos, inv_y_pos))

        # 3. Draw NPC Dialog Box (RPG Style!)
        if npc_message != "":
            # Create a semi-transparent black box
            dialog_box = pygame.Surface((SCREEN_WIDTH - 40, 60), pygame.SRCALPHA)
            dialog_box.fill((0, 0, 0, 200)) # 200 is slightly see-through
            
            # Draw a border around the box
            pygame.draw.rect(dialog_box, AQUA, (0, 0, dialog_box.get_width(), dialog_box.get_height()), 3)
            
            # Blit the box to the screen
            screen.blit(dialog_box, (20, SCREEN_HEIGHT - 80))
            
            # Draw the text inside the box
            draw_text(npc_message, WHITE, 40, SCREEN_HEIGHT - 65)
        draw_text(f"{player.current_zone}", GOLD, SCREEN_WIDTH - 100, 15)
            # Save reminder
        draw_text("[Q] Save", GOLD, SCREEN_WIDTH - 200, 15)
        # --- STATE-SPECIFIC OVERLAYS ---
        if game_state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180) 
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            draw_text("GAME OVER", RED, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 40)
            draw_text("Press R to Restart", GOLD, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 10)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()