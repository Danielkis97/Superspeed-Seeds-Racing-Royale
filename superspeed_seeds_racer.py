import pygame, os, math, time, random

"""
Superspeed Seeds: Racing Royale – Ultimate Prototype with Enhanced Transitions, Checkpoints, Dynamic Weather,
Shooter Enemies, and Extended Worlds

Features:
 • Window size: 1200x800.
 • Controlled via Arrow keys or WASD.
 • Main Menu with “Start the Seed” and “Seederboard” (Ranking) buttons plus credits.
 • In-game displays "Level X out of 100 reached" and a scene description (world name) at the top.
 • Worlds:
      Levels 1–9:  Earth World
      Levels 10–20: Frost World
      Levels 21–30: Water World
      Levels 31–40: Frost Snow World
      Levels 41–50: Fire World
      Levels 51–60: Desert World
      Levels 61–70: Jungle World
      Levels 71–80: Space World
      Levels 81–90: Cyber World
      Levels 91–94: Mystic World (Inverse Controls)
      Levels 95–100: Flashing World
   The scene description is shown at the top center.
 • MAINNET goal spawns at a random x‑position along the bottom.
 • Enemies ("Fudders") spawn at least 150 pixels away from the player's start; their hitboxes are slightly shrunk.
 • Collectible Seeds appear (weighted 2–8, with a 1% chance for 8).
 • Dynamic Weather (starting at level 5):
      - Clear: No effect.
      - Rain: Speed reduction by 20%
      - Fog: Fog overlay.
      - Wind: +40% horizontal drift.
      - Snow: Speed reduction by 50%
   Weather info is displayed in a dedicated line below the scene description.
 • Shop (top‑right) offers:
      1. Speed Upgrade: +5% player acceleration/max speed per upgrade; enemy speed +2% per upgrade.
      2. Seed/Enemy Upgrade: +1 extra enemy/seed per upgrade (max 10).
      3. Shield: Grants 1-second invincibility (when triggered, a pulsating yellow aura appears).
      4. Enemy Slow Upgrade: Slows enemy speed by 25% per upgrade; cost scales (25 seeds if level <50, 35 if 50–89, 40 if 90–100).
 • Checkpoint button (left of Shop) shows “Checkpoints 3/3”. Clicking it sets the current level as a checkpoint and shows “Checkpoint saved!” for 1 second.
 • After level 90, a 5‑second warning screen announces that levels 91–94 (Mystic World) will have inverse controls.
 • In Mystic World (levels 91–94), controls are inverted.
 • Every 10 levels (levels 10,20,…,90): a shooter enemy spawns on the left border and fires a yellow laser every second.
 • Pause menu: Press P to pause/resume. A “Press P to Pause” reminder is shown on-screen.
 • Tutorial screen includes a toggle button for detailed help (displayed in its own bordered window).
 • Ranking displays the top 10 scores with average time per level on a widened UI.
 • Background music loops if available.

"""

############################
#       GLOBAL SETTINGS    #
############################

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

TRACK_LEFT = 50
TRACK_TOP = 50
TRACK_RIGHT = SCREEN_WIDTH - 50
TRACK_BOTTOM = SCREEN_HEIGHT - 50

WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
RED     = (220, 20, 60)
GREEN   = (34, 139, 34)
BLUE    = (0, 0, 255)
GRAY    = (200, 200, 200)
FOG_COLOR = (220, 220, 220)
GOLD    = (255, 215, 0)
SILVER  = (192, 192, 192)

SEED_POD_IMAGE = "seed_pod.png"
MAINNET_IMAGE  = "mainnet.png"
FUDDER_IMAGE   = "fudder.png"
SEED_IMAGE     = "seed.png"
BG_MUSIC       = "bg_music.mp3"

BASE_PLAYER_MAX_SPEED = 9
BASE_PLAYER_ACCEL     = 0.3
PLAYER_FRICTION       = 0.98
PLAYER_ROT_SPEED      = 4

SCORES_FILE = "scores.txt"
MAX_SCORES_TO_KEEP = 10

MAX_LEVEL = 100

############################
#   INITIALIZE PYGAME      #
############################

import pygame, os, math, time, random

pygame.init()
pygame.font.init()
FONT_LG = pygame.font.SysFont(None, 64)
FONT_MD = pygame.font.SysFont(None, 48)
FONT_SM = pygame.font.SysFont(None, 32)
CP_FONT = pygame.font.SysFont(None, 24)
# Additional smaller font for simplified weather text
FONT_WEATHER = pygame.font.SysFont(None, 24)

if os.path.exists(BG_MUSIC):
    pygame.mixer.music.load(BG_MUSIC)
    pygame.mixer.music.play(-1)

############################
# GLOBAL SHOP & CHECKPOINT DATA
############################

shop_upgrades = {"speed": 0, "seed_enemy": 0, "enemy_slow": 0}
player_upgrades = {"shield": 0}
checkpoint_count = 3
active_checkpoint = None
checkpoint_feedback_time = 0

# We'll track if the intro was shown to avoid double press
intro_shown = False

############################
#       SCOREBOARD         #
############################

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    scores = []
    with open(SCORES_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split(',')
                if len(parts) == 3:
                    name = parts[0]
                    level = int(float(parts[1]))
                    total_time = float(parts[2])
                    scores.append((name, level, total_time))
                elif len(parts) == 2:
                    name = parts[0]
                    level = int(float(parts[1]))
                    total_time = 0.0
                    scores.append((name, level, total_time))
            except:
                continue
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def save_score(player_name, score, total_time):
    scores = load_scores()
    scores.append((player_name, score, total_time))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:MAX_SCORES_TO_KEEP]
    with open(SCORES_FILE, 'w') as f:
        for name, sc, t in scores:
            f.write(f"{name},{sc},{t}\n")

############################
#         CLASSES          #
############################

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = self.load_seed_pod_image()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.angle = 0
        self.speed = 0
        self.invincible_until = 0

    def load_seed_pod_image(self):
        if os.path.exists(SEED_POD_IMAGE):
            img = pygame.image.load(SEED_POD_IMAGE).convert_alpha()
            return pygame.transform.scale(img, (50, 50))
        else:
            surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.polygon(surface, RED, [(25, 0), (50, 50), (0, 50)])
            return surface

    def update(self, keys, current_time, weather, inverse=False, mouse_pos=None, mouse_pressed=False):
        effective_accel = BASE_PLAYER_ACCEL * (1 + 0.05 * shop_upgrades["speed"])

        # If 'snow', reduce speed to 50%
        if weather == "rain":
            effective_accel *= 0.8
        elif weather == "snow":
            # -50% speed
            effective_accel *= 0.5

        # Inverse or normal
        if inverse:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle -= PLAYER_ROT_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle += PLAYER_ROT_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.speed -= effective_accel
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.speed += effective_accel
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle += PLAYER_ROT_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle -= PLAYER_ROT_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.speed += effective_accel
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.speed -= effective_accel

        # If windy, shift x
        if weather == "wind":
            self.pos_x += 0.4

        self.speed *= PLAYER_FRICTION
        max_speed = BASE_PLAYER_MAX_SPEED * (1 + 0.05 * shop_upgrades["speed"])
        if self.speed > max_speed:
            self.speed = max_speed
        if self.speed < -max_speed:
            self.speed = -max_speed

        rad = math.radians(self.angle)
        self.pos_x += -self.speed * math.sin(rad)
        self.pos_y += -self.speed * math.cos(rad)

        self.pos_x = max(TRACK_LEFT, min(self.pos_x, TRACK_RIGHT))
        self.pos_y = max(TRACK_TOP, min(self.pos_y, TRACK_BOTTOM))

        self.rect.center = (self.pos_x, self.pos_y)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, base_speed):
        super().__init__()
        self.image = self.load_fudder_image()
        self.rect = self.image.get_rect(center=(x, y))
        slow_factor = 1 - 0.25 * shop_upgrades.get("enemy_slow", 0)
        self.speed = base_speed * (1 + 0.02 * shop_upgrades["speed"]) * slow_factor
        angle = random.uniform(0, 2 * math.pi)
        self.vel_x = self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

    def load_fudder_image(self):
        if os.path.exists(FUDDER_IMAGE):
            img = pygame.image.load(FUDDER_IMAGE).convert_alpha()
            return pygame.transform.scale(img, (40, 40))
        else:
            surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0), (20, 20), 20)
            pygame.draw.line(surface, BLACK, (10, 10), (15, 15), 3)
            pygame.draw.line(surface, BLACK, (25, 10), (20, 15), 3)
            return surface

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.left < TRACK_LEFT:
            self.rect.left = TRACK_LEFT
            self.vel_x = abs(self.vel_x)
        if self.rect.right > TRACK_RIGHT:
            self.rect.right = TRACK_RIGHT
            self.vel_x = -abs(self.vel_x)
        if self.rect.top < TRACK_TOP:
            self.rect.top = TRACK_TOP
            self.vel_y = abs(self.vel_y)
        if self.rect.bottom > TRACK_BOTTOM:
            self.rect.bottom = TRACK_BOTTOM
            self.vel_y = -abs(self.vel_y)

class ShooterEnemy(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        # 50% smaller (20x20)
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(TRACK_LEFT, y))
        self.last_shot_time = 0

    def update(self, current_time, projectiles, player):
        if current_time - self.last_shot_time >= 1:
            self.last_shot_time = current_time
            projectile = Projectile(self.rect.centerx, self.rect.centery, player)
            projectiles.add(projectile)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.color = (255, 255, 0)
        self.thickness = 4
        self.speed = 8
        dx = player.pos_x - x
        dy = player.pos_y - y
        angle = math.atan2(dy, dx)
        self.vel_x = self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)
        self.rect = pygame.Rect(x, y, 10, 10)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, screen):
        end_x = self.rect.x + self.vel_x * 3
        end_y = self.rect.y + self.vel_y * 3
        pygame.draw.line(screen, self.color, (self.rect.x, self.rect.y),
                         (end_x, end_y), self.thickness)

class FinishLine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self.load_mainnet_image()
        self.rect = self.image.get_rect(center=(x, y))
    def load_mainnet_image(self):
        if os.path.exists(MAINNET_IMAGE):
            img = pygame.image.load(MAINNET_IMAGE).convert_alpha()
            return pygame.transform.scale(img, (80, 40))
        else:
            surface = pygame.Surface((80, 40), pygame.SRCALPHA)
            pygame.draw.rect(surface, BLUE, (0, 0, 80, 40))
            text = FONT_SM.render("MAINNET", True, WHITE)
            surface.blit(text, (5, 5))
            return surface
    def update(self):
        pass

class CollectibleSeed(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self.load_seed_image()
        self.rect = self.image.get_rect(center=(x, y))
    def load_seed_image(self):
        if os.path.exists(SEED_IMAGE):
            img = pygame.image.load(SEED_IMAGE).convert_alpha()
            return pygame.transform.scale(img, (20, 20))
        else:
            surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(surface, GREEN, (10, 10), 10)
            return surface

############################
#   STATIC SHIELD INDICATOR
############################

def draw_static_shield(screen, player):
    if player_upgrades["shield"] > 0:
        pygame.draw.circle(screen, (0, 255, 255),
                           (int(player.pos_x), int(player.pos_y)), 30, 3)

############################
#   DYNAMIC WEATHER SYSTEM
############################

def choose_weather():
    # The weighting remains the same; we'll just interpret 'snow' as -50% in Player
    return random.choices(["clear", "rain", "fog", "wind", "snow"],
                          weights=[40,20,15,15,10], k=1)[0]

def update_rain(raindrops):
    for drop in raindrops:
        drop[1] += drop[2]
        if drop[1] > TRACK_BOTTOM:
            drop[1] = TRACK_TOP
            drop[0] = random.randint(TRACK_LEFT, TRACK_RIGHT)
    return raindrops

def draw_rain(screen, raindrops):
    for drop in raindrops:
        pygame.draw.line(screen, WHITE, (drop[0], drop[1]),
                         (drop[0], drop[1]+5), 1)

def update_snow(snowflakes):
    for flake in snowflakes:
        flake[1] += flake[2]
        if flake[1] > TRACK_BOTTOM:
            flake[1] = TRACK_TOP
            flake[0] = random.randint(TRACK_LEFT, TRACK_RIGHT)
    return snowflakes

def draw_snow(screen, snowflakes):
    for flake in snowflakes:
        pygame.draw.circle(screen, WHITE, (flake[0],flake[1]),2)

def draw_weather_info(screen, weather):
    # We'll keep the dictionary but interpret 'snow' as -50% now
    effects = {
        "clear": "No effect.",
        "rain": "Speed reduction by 20%",
        "fog": "Fog is influencing your senses.",
        "wind": "Horizontal Drift + 40%.",
        # changed the text to reflect -50%
        "snow": "Speed reduction by 50%"
    }
    info = FONT_SM.render(f"Effect: {effects.get(weather, 'No effect.')}", True, WHITE)
    screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 40))

############################
#   BACKGROUND & SCENE
############################

def get_scene_color(level):
    if level < 10:
        return (50, 150, 50)
    elif level < 21:
        return (180, 220, 250)
    elif level < 31:
        return (0, 0, 80)
    elif level < 41:
        return (200, 230, 255)
    elif level < 51:
        return (255, 69, 0)
    elif level < 61:
        return (237, 201, 175)
    elif level < 71:
        return (0, 100, 0)
    elif level < 81:
        return (10, 10, 30)
    elif level < 91:
        return (0, 255, 255)
    elif level < 95:
        return (75, 0, 130)
    else:
        return (random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255))

def get_scene_description(level):
    if level < 10:
        return "Earth World"
    elif level < 21:
        return "Frost World"
    elif level < 31:
        return "Water World"
    elif level < 41:
        return "Frost Snow World"
    elif level < 51:
        return "Fire World"
    elif level < 61:
        return "Desert World"
    elif level < 71:
        return "Jungle World"
    elif level < 81:
        return "Space World"
    elif level < 91:
        return "Cyber World"
    elif level < 95:
        return "Mystic World (Inverse Controls)"
    else:
        return "Flashing World"

def draw_scene(screen, level):
    bg_color = get_scene_color(level)
    screen.fill(bg_color)
    if 31 <= level < 41:
        for _ in range(100):
            x = random.randint(TRACK_LEFT, TRACK_RIGHT)
            y = random.randint(TRACK_TOP, TRACK_BOTTOM)
            pygame.draw.circle(screen, WHITE, (x,y), 2)
    pygame.draw.rect(screen, GRAY, (TRACK_LEFT, TRACK_TOP,
                     TRACK_RIGHT-TRACK_LEFT, TRACK_BOTTOM-TRACK_TOP), 5)
    desc = get_scene_description(level)
    desc_text = FONT_SM.render(desc, True, WHITE)
    screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 10))
    if level >= 5:
        draw_weather_info(screen, weather)

############################
#   CHECKPOINT SYSTEM
############################

CHECKPOINT_RECT = pygame.Rect(SCREEN_WIDTH - 320, 10, 150, 50)

def draw_checkpoint_button(screen, checkpoint_count, active):
    text = CP_FONT.render(f"Checkpoints {checkpoint_count}/3", True, BLACK)
    color = GOLD if active else GRAY
    pygame.draw.rect(screen, color, CHECKPOINT_RECT)
    screen.blit(text, (CHECKPOINT_RECT.centerx - text.get_width()//2,
                       CHECKPOINT_RECT.centery - text.get_height()//2))
    if active:
        subtext = CP_FONT.render("Activated", True, BLACK)
        # Moved up a bit so it doesn't overlap
        screen.blit(subtext,(CHECKPOINT_RECT.centerx - subtext.get_width()//2,
                             CHECKPOINT_RECT.bottom - 18))
    global checkpoint_feedback_time
    if checkpoint_feedback_time and time.time() - checkpoint_feedback_time < 1:
        feedback = CP_FONT.render("Checkpoint saved!", True, GOLD)
        screen.blit(feedback, (CHECKPOINT_RECT.x, CHECKPOINT_RECT.bottom + 5))
    else:
        checkpoint_feedback_time = 0

############################
#   ATTRIBUTE DISPLAY
############################

def draw_attributes(screen):
    # Move 150 px to left, 60% alpha silver
    attr_width = 330
    attr_height=230
    # We'll place it top-right but minus 150 px
    # The shop is at x=SCREEN_WIDTH-160, so let's do x=SCREEN_WIDTH-160-attr_width
    overlay_x = SCREEN_WIDTH - 55 - attr_width
    overlay_y = SHOP_RECT.bottom + 10

    overlay_surf = pygame.Surface((attr_width, attr_height))
    overlay_surf.set_alpha(50)  # ~60% alpha
    overlay_surf.fill(SILVER)

    # We'll place text inside
    base_y = 10
    base_x = 10

    speed_text = FONT_SM.render(f"Speed Upgrade: Lvl {shop_upgrades['speed']}",True,BLACK)
    seed_text  = FONT_SM.render(f"Seed/Enemy Upgrade: Lvl {shop_upgrades['seed_enemy']}/10", True, BLACK)
    shield_status = "Yes" if player_upgrades["shield"]>0 else "No"
    shield_text   = FONT_SM.render(f"Shield: {shield_status}", True, BLACK)
    slow_text     = FONT_SM.render(f"Enemy Slow: Lvl {shop_upgrades.get('enemy_slow',0)}",True,BLACK)

    overlay_surf.blit(speed_text,(base_x, base_y))
    overlay_surf.blit(seed_text, (base_x, base_y+30))
    overlay_surf.blit(shield_text,(base_x, base_y+60))
    overlay_surf.blit(slow_text,  (base_x, base_y+90))

    eff1 = FONT_SM.render(f"Player Accel Bonus: {shop_upgrades['speed']*5}%", True, BLACK)
    eff2 = FONT_SM.render(f"Enemy Speed Bonus: {shop_upgrades['speed']*2}%", True, BLACK)
    eff3 = FONT_SM.render(f"Extra Seeds/Enemies: +{shop_upgrades['seed_enemy']}", True, BLACK)

    overlay_surf.blit(eff1,(base_x, base_y+130))
    overlay_surf.blit(eff2,(base_x, base_y+160))
    overlay_surf.blit(eff3,(base_x, base_y+190))

    screen.blit(overlay_surf,(overlay_x,overlay_y))

def draw_shield_aura(screen, player, current_time):
    if current_time < player.invincible_until:
        pulse = 5 * math.sin(current_time*6) + 25
        pygame.draw.circle(screen, (255,255,0),
                           (int(player.pos_x), int(player.pos_y)),
                           int(pulse), 3)

############################
#   STATIC SHIELD INDICATOR
############################

def draw_static_shield(screen, player):
    if player_upgrades["shield"]>0:
        pygame.draw.circle(screen, (0,255,255),
                           (int(player.pos_x), int(player.pos_y)),30,3)

############################
#       SHOP SYSTEM
############################

SHOP_RECT = pygame.Rect(SCREEN_WIDTH - 160, 10, 150, 50)

def draw_shop_icon(screen, seed_count):
    pygame.draw.rect(screen, BLACK, SHOP_RECT)
    shop_text = FONT_SM.render("Shop", True, WHITE)
    screen.blit(shop_text,(SHOP_RECT.centerx - shop_text.get_width()//2,
                           SHOP_RECT.centery - shop_text.get_height()//2))
    counter_text = FONT_SM.render(f"Seeds: {seed_count}", True, WHITE)
    screen.blit(counter_text,(SHOP_RECT.left - counter_text.get_width() -10, 20))

def show_shop(screen, seed_count, current_level):
    # We'll add buying checkpoints here if <3 for 40 seeds
    global shop_upgrades, player_upgrades, checkpoint_count
    option1_button=pygame.Rect(SCREEN_WIDTH//2-250,150,500,50)
    option2_button=pygame.Rect(SCREEN_WIDTH//2-250,220,500,50)
    option3_button=pygame.Rect(SCREEN_WIDTH//2-250,290,500,50)
    option4_button=pygame.Rect(SCREEN_WIDTH//2-250,360,500,50)
    # new button for buying checkpoint
    option5_button=pygame.Rect(SCREEN_WIDTH//2-250,430,500,50)

    close_button=pygame.Rect(SCREEN_WIDTH//2-100,500,200,50)

    cost1=(shop_upgrades["speed"]+1)*5
    cost2=((shop_upgrades["seed_enemy"]+1)*10
           if shop_upgrades["seed_enemy"]<10 else None)
    cost3=20 if current_level<50 else 40
    if current_level<50:
        cost4=25
    elif current_level<90:
        cost4=35
    else:
        cost4=40

    cost_checkpoint=40  # cost to buy 1 checkpoint

    running=True
    while running:
        screen.fill(BLACK)

        title=FONT_LG.render("SHOP", True, WHITE)
        screen.blit(title,(SCREEN_WIDTH//2 - title.get_width()//2,50))

        mouse_pos=pygame.mouse.get_pos()

        c1=GRAY if option1_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen,c1,option1_button)
        opt1_text=FONT_SM.render(f"Speed Upgrade: Lvl {shop_upgrades['speed']}  Cost: {cost1} seeds",True,WHITE)
        screen.blit(opt1_text,(option1_button.centerx - opt1_text.get_width()//2,
                               option1_button.centery - opt1_text.get_height()//2))

        c2=GRAY if option2_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen,c2,option2_button)
        if cost2 is not None:
            opt2_text=FONT_SM.render(f"Seed/Enemy Upgrade: Lvl {shop_upgrades['seed_enemy']}  Cost: {cost2} seeds", True,WHITE)
        else:
            opt2_text=FONT_SM.render(f"Seed/Enemy Upgrade: Lvl {shop_upgrades['seed_enemy']}  (MAX)", True,WHITE)
        screen.blit(opt2_text,(option2_button.centerx - opt2_text.get_width()//2,
                               option2_button.centery - opt2_text.get_height()//2))

        c3=GRAY if option3_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen,c3,option3_button)
        opt3_text=FONT_SM.render(f"Shield: {('Yes' if player_upgrades['shield']>0 else 'No')}  Cost: {cost3} seeds",True,WHITE)
        screen.blit(opt3_text,(option3_button.centerx - opt3_text.get_width()//2,
                               option3_button.centery - opt3_text.get_height()//2))

        c4=GRAY if option4_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen,c4,option4_button)
        opt4_text=FONT_SM.render(f"Enemy Slow: Lvl {shop_upgrades.get('enemy_slow',0)}  Cost: {cost4} seeds", True, WHITE)
        screen.blit(opt4_text,(option4_button.centerx - opt4_text.get_width()//2,
                               option4_button.centery - opt4_text.get_height()//2))

        c5=GRAY if option5_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen,c5,option5_button)
        if checkpoint_count<3:
            opt5_text=FONT_SM.render(f"Buy +1 Checkpoint (Currently {checkpoint_count}/3)  Cost: {cost_checkpoint} seeds",True,WHITE)
        else:
            opt5_text=FONT_SM.render(f"Buy +1 Checkpoint (MAX)",True,WHITE)
        screen.blit(opt5_text,(option5_button.centerx - opt5_text.get_width()//2,
                               option5_button.centery - opt5_text.get_height()//2))

        close_color=GRAY if close_button.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(screen, close_color, close_button)
        close_txt=FONT_SM.render("Close Shop", True, WHITE)
        screen.blit(close_txt,(close_button.centerx - close_txt.get_width()//2,
                               close_button.centery - close_txt.get_height()//2))

        current_disp=FONT_SM.render(f"Your Seeds: {seed_count}", True, WHITE)
        screen.blit(current_disp,(SCREEN_WIDTH//2 - current_disp.get_width()//2,
                                  close_button.bottom+20))

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); exit()
            elif ev.type==pygame.MOUSEBUTTONDOWN:
                if option1_button.collidepoint(ev.pos):
                    if seed_count>=cost1:
                        seed_count-=cost1
                        shop_upgrades["speed"]+=1
                        cost1=(shop_upgrades["speed"]+1)*5
                elif option2_button.collidepoint(ev.pos):
                    if shop_upgrades["seed_enemy"]<10:
                        cost_2=(shop_upgrades["seed_enemy"]+1)*10
                        if seed_count>=cost_2:
                            seed_count-=cost_2
                            shop_upgrades["seed_enemy"]+=1
                elif option3_button.collidepoint(ev.pos):
                    if seed_count>=cost3:
                        seed_count-=cost3
                        player_upgrades["shield"]=1
                elif option4_button.collidepoint(ev.pos):
                    if seed_count>=cost4:
                        seed_count-=cost4
                        shop_upgrades["enemy_slow"]= shop_upgrades.get("enemy_slow",0)+1
                        if current_level<50:
                            cost4=25
                        elif current_level<90:
                            cost4=35
                        else:
                            cost4=40
                elif option5_button.collidepoint(ev.pos):
                    # Buy an extra checkpoint if <3
                    if checkpoint_count<3:
                        if seed_count>=40:
                            seed_count-=40
                            checkpoint_count+=1
                elif close_button.collidepoint(ev.pos):
                    running=False
        pygame.time.wait(50)
    return seed_count

############################
#   TUTORIAL & INTRO SCREEN
############################

def show_introduction(screen):
    # single key press
    global intro_shown
    if intro_shown:
        return
    intro_shown = True
    screen.fill(BLACK)
    intro_text = [
        "Your seed lost its powers due to the withering curse of the Dark Winds.",
        "The ancient Tower of Seeds has crumbled and your superseed status is gone.",
        "You must climb back the Tower of Seeds, reclaim your power,",
        "and awaken your true potential to reach Mainnet."
    ]
    y = SCREEN_HEIGHT//2 - 80
    for line in intro_text:
        line_surf = FONT_SM.render(line, True, WHITE)
        screen.blit(line_surf,(SCREEN_WIDTH//2 - line_surf.get_width()//2, y))
        y+=40

    prompt=FONT_SM.render("Press any key to continue...", True, WHITE)
    screen.blit(prompt,(SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT-100))
    pygame.display.flip()

    waiting=True
    while waiting:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); exit()
            elif ev.type==pygame.KEYDOWN:
                waiting=False


def show_tutorial(screen):
    show_introduction(screen)  # If you still want the intro before the tutorial

    # Combine everything into one neatly formatted list of lines:
    lines = [
        "Movement & Goals:",
        "  •  Use Arrow Keys or WASD to steer your Seed Pod and accelerate.",
        "  •  Reach the MAINNET at the bottom of the screen to advance levels.",
        "  •  Avoid Fudders – colliding with them ends your run unless you have a Shield.",
        "  •  Collect Seeds on each level to spend in the Shop.",
        "  •  Click the Shop icon (top-right) to purchase upgrades.",
        "  •  Click the Checkpoint button (left of Shop) if you have available checkpoints.",
        "",
        "Upgrades:",
        "  •  Speed Upgrade: Increases your acceleration & max speed by 5% per level, but also boosts enemy speed by 2%.",
        "  •  Seed/Enemy Upgrade: Adds +1 enemy and +1 seed to each level (max 10).",
        "  •  Shield: Grants one collision protection and 1 second of invincibility.",
        "  •  Enemy Slow: Slows enemies by 25% per level; cost scales with your current level.",
        "",
        "Additional Mechanics:",
        "  •  Shooter Enemies: Appear every 10 levels (10, 20, 30, etc.), firing projectiles from the left.",
        "  •  Press P to pause the game (a light overlay keeps the board visible).",
        "  •  Checkpoints: You can set up to 3 per run and overwrite older ones if needed."
    ]

    # We’ll keep displaying these lines until the user presses a key
    while True:
        screen.fill(BLACK)

        # Title at the top
        title = FONT_LG.render("Superspeed Seeds: Racing Royale", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # Render the combined lines
        y = SCREEN_HEIGHT // 2.5 - 200  # Adjust to place them higher or lower
        for line in lines:
            line_surf = FONT_SM.render(line, True, WHITE)
            screen.blit(line_surf, (SCREEN_WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 30  # spacing between lines

        pygame.display.flip()

        # End tutorial on keypress
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                return


def show_level_clear(screen, level, level_time):
    # single pass fade: alpha=0->255->0
    msg = FONT_MD.render(f"Level {level} cleared in {level_time:.2f}s", True, WHITE)
    steps=20  # ~2 seconds total => each step ~33ms
    for i in range(steps + 1):
        if i<=steps:
            alpha=int((i/steps)*255)
        else:
            alpha=int(((2*steps-i)/steps)*255)
        fade=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        fade.fill(BLACK)
        fade.set_alpha(alpha)
        screen.fill(BLACK)
        screen.blit(msg,(SCREEN_WIDTH//2 - msg.get_width()//2,
                         SCREEN_HEIGHT//2))
        screen.blit(fade,(0,0))
        pygame.display.flip()
        pygame.time.delay(33)

def show_inverse_warning(screen):
    warning = FONT_MD.render("Mystic World Incoming!", True, WHITE)
    sub = FONT_SM.render("Levels 91-94: Inverse Controls Active", True, WHITE)
    screen.fill(BLACK)
    screen.blit(warning,(SCREEN_WIDTH//2 - warning.get_width()//2,
                         SCREEN_HEIGHT//2 - 40))
    screen.blit(sub,(SCREEN_WIDTH//2 - sub.get_width()//2,
                     SCREEN_HEIGHT//2 + 10))
    pygame.display.flip()
    pygame.time.wait(5000)

############################
#       PAUSE MENU         #
############################

def pause_menu(screen):
    paused = True
    pause_text = FONT_MD.render("Paused", True, WHITE)
    instruct_text = FONT_SM.render("Press P to resume", True, WHITE)
    while paused:
        overlay = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        # We'll keep alpha=200 to see partial
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay,(0,0))
        screen.blit(pause_text,(SCREEN_WIDTH//2 - pause_text.get_width()//2,
                                SCREEN_HEIGHT//2 - 50))
        screen.blit(instruct_text,(SCREEN_WIDTH//2 - instruct_text.get_width()//2,
                                   SCREEN_HEIGHT//2 + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_p:
                    paused=False
            if event.type==pygame.QUIT:
                pygame.quit(); exit()

############################
#       MAIN MENU          #
############################

def main_menu(screen):
    menu_bg = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    menu_bg.fill((34,139,34))
    start_button=pygame.Rect(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-100,300,60)
    board_button=pygame.Rect(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2,300,60)
    running=True
    while running:
        screen.blit(menu_bg,(0,0))
        title=FONT_LG.render("Superspeed Seeds: Racing Royale",True,WHITE)
        screen.blit(title,(SCREEN_WIDTH//2 - title.get_width()//2,80))

        pygame.draw.rect(screen, GRAY, start_button)
        stxt=FONT_MD.render("Start the Seed",True,BLACK)
        screen.blit(stxt,(start_button.centerx - stxt.get_width()//2,
                          start_button.centery - stxt.get_height()//2))

        pygame.draw.rect(screen, GRAY, board_button)
        btxt=FONT_MD.render("Seederboard",True,BLACK)
        screen.blit(btxt,(board_button.centerx - btxt.get_width()//2,
                          board_button.centery - btxt.get_height()//2))

        cred=FONT_SM.render("Made by FarmingLegendX on March 19, 2025 for the SuperSeed Tesla Contest",True,WHITE)
        screen.blit(cred,(10,SCREEN_HEIGHT - cred.get_height() -10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                if start_button.collidepoint((mx,my)):
                    return "start"
                elif board_button.collidepoint((mx,my)):
                    return "seederboard"

############################
#     DISPLAY LEADERBOARD
############################

def display_leaderboard(screen):
    scores=load_scores()
    running=True
    while running:
        screen.fill(BLACK)
        header=FONT_MD.render("Seederboard Ranking ",True,WHITE)
        screen.blit(header,(SCREEN_WIDTH//2 - header.get_width()//2,50))
        y_offset=120
        for i,(name,sc,t) in enumerate(scores, start=1):
            avg=t/sc if sc!=0 else 0
            entry_rect=pygame.Rect(SCREEN_WIDTH//2-300,y_offset-5,600,35)
            pygame.draw.rect(screen,GRAY,entry_rect,border_radius=5)
            line=FONT_SM.render(f"{i}. {name} - Level {sc} | Time: {t:.2f}s | Avg: {avg:.2f}s/level",True,WHITE)
            screen.blit(line,(SCREEN_WIDTH//2 - line.get_width()//2,y_offset))
            y_offset+=45

        info=FONT_SM.render("Press any key or click to return to the main menu",True,WHITE)
        screen.blit(info,(SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT-100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN or event.type==pygame.MOUSEBUTTONDOWN:
                running=False

############################
#      GAME LEVEL
############################

def run_level(screen, level, seed_count):
    global active_checkpoint, checkpoint_count, checkpoint_feedback_time, weather
    player = Player(SCREEN_WIDTH // 2, TRACK_TOP + 30)
    finish_x = random.randint(TRACK_LEFT, TRACK_RIGHT)
    finish_y = TRACK_BOTTOM - 20
    finish_goal = FinishLine(finish_x, finish_y)

    base_enemy_count = min(3 + level, 20) + shop_upgrades["seed_enemy"]
    enemies = pygame.sprite.Group()
    for _ in range(base_enemy_count):
        while True:
            ex = random.randint(TRACK_LEFT, TRACK_RIGHT)
            ey = random.randint(TRACK_TOP, TRACK_BOTTOM)
            if math.hypot(ex - SCREEN_WIDTH // 2, ey - (TRACK_TOP + 30)) >= 150:
                break
        base_enemy_speed = 1 + level * 0.1
        enemy = Enemy(ex, ey, base_enemy_speed)
        enemies.add(enemy)

    base_num_seeds = random.choices(range(2,9), weights=[40,25,15,10,5,4,1], k=1)[0]
    nseeds = base_num_seeds + shop_upgrades["seed_enemy"]
    seeds = pygame.sprite.Group()
    for _ in range(base_num_seeds):
        sx = random.randint(TRACK_LEFT, TRACK_RIGHT)
        sy = random.randint(TRACK_TOP, TRACK_BOTTOM)
        s = CollectibleSeed(sx, sy)
        seeds.add(s)

    if level < 5:
        weather = "clear"
    else:
        weather = choose_weather()

    raindrops = []
    snowflakes = []
    if weather == "rain":
        for _ in range(100):
            rx = random.randint(TRACK_LEFT, TRACK_RIGHT)
            ry = random.randint(TRACK_TOP, TRACK_BOTTOM)
            sp = random.randint(5,15)
            raindrops.append([rx, ry, sp])
    if weather == "snow":
        for _ in range(100):
            rx = random.randint(TRACK_LEFT, TRACK_RIGHT)
            ry = random.randint(TRACK_TOP, TRACK_BOTTOM)
            sp = random.randint(2,8)
            snowflakes.append([rx, ry, sp])

    shooter_group = pygame.sprite.Group()
    if level >= 10:
        num_shooters = level // 10
        spacing = (TRACK_BOTTOM - TRACK_TOP) // (num_shooters + 1)
        for i in range(num_shooters):
            shr = ShooterEnemy(TRACK_TOP + (i+1)*spacing)
            shooter_group.add(shr)

    projectiles = pygame.sprite.Group()

    clock = pygame.time.Clock()
    level_start_time = time.time()

    inverse = True if 91 <= level < 95 else False

    while True:
        dt = clock.tick(FPS)
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if SHOP_RECT.collidepoint(pygame.mouse.get_pos()):
                    seed_count = show_shop(screen, seed_count, level)

                # --- Overwrite checkpoint each time (always uses up a slot) ---
                if CHECKPOINT_RECT.collidepoint(event.pos):
                    if checkpoint_count > 0:
                        active_checkpoint = level
                        checkpoint_count -= 1
                        checkpoint_feedback_time = time.time()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_menu(screen)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()

        player.update(keys, current_time, weather, inverse)
        enemies.update()
        finish_goal.update()

        if weather == "rain":
            raindrops = update_rain(raindrops)
        if weather == "snow":
            snowflakes = update_snow(snowflakes)

        for shr in shooter_group:
            shr.update(current_time, projectiles, player)
        projectiles.update()

        if current_time >= player.invincible_until:
            def custom_collide(pl, en):
                return pl.rect.colliderect(en.rect.inflate(-10, -10))

            if any(custom_collide(player, e) for e in enemies):
                if player_upgrades["shield"] > 0:
                    player_upgrades["shield"] = 0
                    player.invincible_until = current_time + 1
                else:
                    level_time = time.time() - level_start_time
                    return (False, seed_count, level_time)

            for proj in projectiles:
                if player.rect.colliderect(proj.rect):
                    if player_upgrades["shield"] > 0:
                        player_upgrades["shield"] = 0
                        player.invincible_until = current_time + 1
                        proj.kill()
                    else:
                        level_time = time.time() - level_start_time
                        return (False, seed_count, level_time)

        collected = pygame.sprite.spritecollide(player, seeds, True)
        if collected:
            seed_count += len(collected)

        if player.rect.colliderect(finish_goal.rect):
            level_time = time.time() - level_start_time
            return (True, seed_count, level_time)

        draw_scene(screen, level)
        w_text = FONT_SM.render(f"Weather: {weather.capitalize()}", True, WHITE)
        screen.blit(w_text, (TRACK_LEFT + 10, TRACK_TOP - 70))
        draw_weather_info(screen, weather)

        level_text = FONT_SM.render(f"Level {level} out of {MAX_LEVEL} reached | Seeds: {seed_count}", True, WHITE)
        screen.blit(level_text, (TRACK_LEFT + 10, TRACK_TOP - 40))

        pause_info = FONT_SM.render("Press P to Pause", True, WHITE)
        screen.blit(pause_info, (SCREEN_WIDTH // 2 - pause_info.get_width() // 2, SCREEN_HEIGHT - 30))

        draw_shop_icon(screen, seed_count)
        draw_checkpoint_button(screen, checkpoint_count, active_checkpoint is not None)
        draw_attributes(screen)

        screen.blit(finish_goal.image, finish_goal.rect)
        for enemy in enemies:
            screen.blit(enemy.image, enemy.rect)
        for seed_obj in seeds:
            screen.blit(seed_obj.image, seed_obj.rect)
        for shooter in shooter_group:
            screen.blit(shooter.image, shooter.rect)
        for proj in projectiles:
            proj.draw(screen)

        if weather == "rain":
            draw_rain(screen, raindrops)
        if weather == "snow":
            draw_snow(screen, snowflakes)
        if weather == "fog":
            fog_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fog_overlay.set_alpha(100)
            fog_overlay.fill(FOG_COLOR)
            screen.blit(fog_overlay, (0, 0))

        screen.blit(player.image, player.rect)
        draw_shield_aura(screen, player, current_time)
        draw_static_shield(screen, player)

        pygame.display.flip()

def show_game_over(screen, level, total_time):
    overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    overlay.set_alpha(230)
    overlay.fill(BLACK)
    message=FONT_LG.render("Your Seed has been destroyed...",True,RED)
    level_msg=FONT_SM.render(f"You reached Level {level}.",True,WHITE)
    time_msg=FONT_SM.render(f"Total Time: {total_time:.2f}s",True,WHITE)
    prompt=FONT_SM.render("Enter your name and press 'S' to save your score.",True,WHITE)
    input_name=""
    while True:
        screen.blit(overlay,(0,0))
        screen.blit(message,(SCREEN_WIDTH//2 - message.get_width()//2,
                             SCREEN_HEIGHT//2-170))
        screen.blit(level_msg,(SCREEN_WIDTH//2 - level_msg.get_width()//2,
                               SCREEN_HEIGHT//2-120))
        screen.blit(time_msg,(SCREEN_WIDTH//2 - time_msg.get_width()//2,
                              SCREEN_HEIGHT//2-80))
        screen.blit(prompt,(SCREEN_WIDTH//2 - prompt.get_width()//2,
                            SCREEN_HEIGHT//2-20))
        name_surf=FONT_SM.render("Name: "+input_name,True,WHITE)
        screen.blit(name_surf,(SCREEN_WIDTH//2 - name_surf.get_width()//2,
                               SCREEN_HEIGHT//2+30))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); exit()
            elif ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_BACKSPACE:
                    input_name=input_name[:-1]
                elif ev.key==pygame.K_s:
                    if not input_name.strip():
                        input_name="Player"
                    save_score(input_name, level, total_time)
                    return
                else:
                    input_name+=ev.unicode

############################
#          MAIN
############################

def main():
    global shop_upgrades, player_upgrades, checkpoint_count, active_checkpoint, checkpoint_feedback_time, weather

    while True:
        shop_upgrades = {"speed": 0, "seed_enemy": 0, "enemy_slow": 0}
        player_upgrades = {"shield": 0}
        checkpoint_count = 3
        active_checkpoint = None
        checkpoint_feedback_time = 0

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Superspeed Seeds: Racing Royale")

        seed_count=0
        total_time=0.0

        option=main_menu(screen)
        if option=="start":
            show_introduction(screen)
            screen.fill(BLACK)
            pygame.display.flip()
            show_tutorial(screen)
            current_level=1
            total_time=0.0
            while current_level<=MAX_LEVEL:
                if current_level==91:
                    show_inverse_warning(screen)

                completed, seed_count, lvl_time= run_level(screen, current_level, seed_count)
                total_time += lvl_time
                if not completed:
                    if active_checkpoint is not None:
                        current_level=active_checkpoint
                        active_checkpoint=None
                        continue
                    else:
                        show_game_over(screen, current_level, total_time)
                        seed_count=0
                        break

                show_level_clear(screen, current_level, lvl_time)
                current_level+=1

            if current_level>MAX_LEVEL:
                screen.fill(BLACK)
                congrats=FONT_MD.render("Congratulations! You beat 100 levels! You have evolved to a SuperSeed! You may now enter the Mainnet!",True,WHITE)
                total_msg=FONT_SM.render(f"Total Time: {total_time:.2f}s",True,WHITE)
                screen.blit(congrats,(SCREEN_WIDTH//2 - congrats.get_width()//2,
                                      SCREEN_HEIGHT//2 -40))
                screen.blit(total_msg,(SCREEN_WIDTH//2 - total_msg.get_width()//2,
                                       SCREEN_HEIGHT//2 +20))
                pygame.display.flip()
                pygame.time.wait(3000)
        elif option=="seederboard":
            display_leaderboard(screen)

if __name__ == "__main__":
    main()
