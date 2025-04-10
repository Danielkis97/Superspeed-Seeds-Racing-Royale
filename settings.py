# --- START OF FILE settings.py ---


import os
import pygame

# --- SCREEN & TRACK SETTINGS ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

TRACK_LEFT = 50
TRACK_TOP = 50
TRACK_RIGHT = SCREEN_WIDTH - 50
TRACK_BOTTOM = SCREEN_HEIGHT - 50

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
DARK_GRAY = (50, 50, 50) # Added for vault button fallback bg
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
FOG_COLOR = (220, 220, 220) # Kept definition, but unused
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50) # Added for achievement tier coloring
CYAN = (0, 255, 255) # Added for Freeze timer
TURQUOISE = (64, 224, 208)

# Player Trail Colors
TRAIL_COLOR_DEFAULT = (200, 200, 255) # Base slightly blueish-white
TRAIL_COLOR_SEEDGUY = (180, 180, 255) # More blue tint (Pod 1)
TRAIL_COLOR_JOAO = (255, 180, 100) # Orangey tint (Pod 2)
TRAIL_COLOR_MESKY = (255, 150, 150) # Reddish tint (Pod 3)
TRAIL_COLOR_CHOSEN = (255, 235, 150) # Golden tint (Pod 4)

PLAYER_TRAIL_COLORS = {
    1: TRAIL_COLOR_SEEDGUY,
    2: TRAIL_COLOR_JOAO,
    3: TRAIL_COLOR_MESKY,
    4: TRAIL_COLOR_CHOSEN,
}

# --- ASSET FILE PATHS ---
# Sprites are loaded from the ASSETS_DIR ("Assets")
# Sounds and videos are loaded from the MEDIA_DIR ("media")
ASSETS_DIR = "Assets"
MEDIA_DIR = "media"

# Ensure the ASSETS_DIR exists relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, ASSETS_DIR)
MEDIA_DIR = os.path.join(BASE_DIR, MEDIA_DIR)

# --- Core Game Assets ---
PLAYER_IMAGE = os.path.join(ASSETS_DIR, "seed_pod1.png") # Default, overwritten by character selection
DEBT_IMAGE = os.path.join(ASSETS_DIR, "debt.png")
SEED_IMAGE = os.path.join(ASSETS_DIR, "seed.png")
MAINNET_IMAGE = os.path.join(ASSETS_DIR, "mainnet.png") # Goal/Finish Line
BUTTON_IMAGE = os.path.join(ASSETS_DIR, "button.png") # General purpose button bg
VAULT_BUTTON_IMAGE = os.path.join(ASSETS_DIR, "vaultbutton.png") # Vault shop button bg
BACKGROUND_MENU = os.path.join(ASSETS_DIR, "backgroundmenu.png")
DAVID_IMAGE = os.path.join(ASSETS_DIR, "david.png") # David enemy
SHOOTER_IMAGE = os.path.join(ASSETS_DIR, "shooter.png") # Shooter enemy
MAGNET_IMAGE = os.path.join(ASSETS_DIR, "magnet.png") # Magnet powerup
MERCHANT_IMAGE = os.path.join(ASSETS_DIR, "merchant.png") # Shop merchant (used in overlay now?)
SHOP_BACKGROUND = os.path.join(ASSETS_DIR, "merchant_shop_bg.png") # Background for fullscreen shop
GAMEOVER_IMAGE = os.path.join(ASSETS_DIR, "gameover.png") # Game over screen graphic
# --- NEW: End screen image ---
ENDSCREEN_IMAGE = os.path.join(ASSETS_DIR, "endscreen.png")
# --- END NEW ---
COIN_IMAGE = os.path.join(ASSETS_DIR, "coin.png") # Old Coin icon # --- KEPT IN CASE NEEDED, BUT SUPR IS USED ---
SUPR_TOKEN_IMAGE = os.path.join(ASSETS_DIR, "supr_token.png") # <<< NEW: SUPR Token icon
LOCK_ICON_PATH = os.path.join(ASSETS_DIR, "lock_icon.png") # <<< NEW: Path for lock icon
UNLOCKED_ICON_PATH = os.path.join(ASSETS_DIR, "unlocked.png") # <<< NEW: Path for unlocked icon
FREEZE_IMAGE = os.path.join(ASSETS_DIR, "freeze.png") # Freeze powerup
SPARKLE_IMAGE = os.path.join(ASSETS_DIR, "sparkle.png") # Particle effect base
TUTORIAL_IMAGE = os.path.join(ASSETS_DIR, "tutorial.png") # Tutorial image 1
TUTORIAL2_IMAGE = os.path.join(ASSETS_DIR, "tutorial2.png") # Tutorial image 2
STORY_VIDEO = os.path.join(MEDIA_DIR, "story.mp4") # Story video
# --- FIX: Restore SLOW_AURA_IMAGE definition ---
SLOW_AURA_IMAGE = os.path.join(ASSETS_DIR, "slowaura.png") # <<< RESTORED
# --- END FIX ---


# --- NEW: Powerup Images ---
SHIELD_POWERUP_IMAGE = os.path.join(ASSETS_DIR, "shieldpowerup.png")
DOUBLE_SEED_POWERUP_IMAGE = os.path.join(ASSETS_DIR, "doubleseedpowerup.png")

# --- NEW: Ability Animation Images ---
DASH_ANIMATION_IMAGE = os.path.join(ASSETS_DIR, "dashanimation.png")
SPEED_ANIMATION_IMAGE = os.path.join(ASSETS_DIR, "speedanimation.png")
SLOW_ANIMATION_IMAGE = os.path.join(ASSETS_DIR, "slowanimation.png")
INVINC_ANIMATION_IMAGE = os.path.join(ASSETS_DIR, "invincanimation.png")

# --- Backgrounds for specific screens ---
REPAYMENT_VAULT_BACKGROUND = os.path.join(ASSETS_DIR, "repaymentvaultbackground.png") # Name for vault bg
HALL_OF_SEEDS_BACKGROUND = os.path.join(ASSETS_DIR, "hallofseedsbackground.png") # Name for hall bg
CHARACTER_SELECT_BACKGROUND = os.path.join(ASSETS_DIR, "characterselectbackground.png") # Name for char select bg
SEEDERBOARD_BACKGROUND = os.path.join(ASSETS_DIR, "seederboard_bg.png") # Background for seederboard
CHOOSE_DIFFICULTY_BACKGROUND = os.path.join(ASSETS_DIR, "choosedifficultyscreen.png") # Background for difficulty select
MANWHA_BG_IMAGE = os.path.join(ASSETS_DIR, "manwhabg.png") # <<< NEW: Background for Manwha viewer

# --- Manwha Images ---
MANWHA_IMAGES = [os.path.join(ASSETS_DIR, f"manwha{i}.png") for i in range(1, 11)] # Assumes manwha1.png to manwha10.png

# Minigame Backgrounds
MINIGAME1_BACKGROUND = os.path.join(ASSETS_DIR, "minigame1_bg.png") # Background for Seed Harvest
DAVID_MINIGAME_BACKGROUND = os.path.join(ASSETS_DIR, "bgdavidmini.png") # Background for David minigame
MINIGAME3_BACKGROUND = os.path.join(ASSETS_DIR, "minigame3_bg.png") # Background for Inverse Gauntlet

# --- Enemy Images (World-specific) ---
FIRE_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "fire_enemy.png")
WATER_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "water_enemy.png")
FROST_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "frost_enemy.png")
UNDERWORLD_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "underworld_enemy.png")
DESERT_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "desert_enemy.png")
JUNGLE_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "jungle_enemy.png")
SPACE_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "space_enemy.png")
CYBER_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "cyber_enemy.png")
MYSTIC_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "mystic_enemy.png")
SUPERSEED_ENEMY_IMAGE = os.path.join(ASSETS_DIR, "superseed_enemy.png") # Renamed (assuming filename change)
EARTH_ENEMY_IMAGE = DEBT_IMAGE # Earth world uses the default 'debt' image

# --- Character Display Images (for selection screen) ---
SEEDGUY_DISPLAY_IMAGE = os.path.join(ASSETS_DIR, "seedguy.png")
JOAO_DISPLAY_IMAGE = os.path.join(ASSETS_DIR, "joao.png")
MESKY_DISPLAY_IMAGE = os.path.join(ASSETS_DIR, "mesky.png")
CHOSEN_DISPLAY_IMAGE = os.path.join(ASSETS_DIR, "chosen.png")

# --- Player Pod Images (actual in-game sprites) ---
PLAYER_POD1_IMAGE = os.path.join(ASSETS_DIR, "seed_pod1.png") # SeedGuy
PLAYER_POD2_IMAGE = os.path.join(ASSETS_DIR, "seed_pod2.png") # Joao
PLAYER_POD3_IMAGE = os.path.join(ASSETS_DIR, "seed_pod3.png") # Mesky
PLAYER_POD4_IMAGE = os.path.join(ASSETS_DIR, "seed_pod4.png") # Chosen

# --- Ability Icons (for UI display) ---
SEEDGUY_ABILITY_ICON = os.path.join(ASSETS_DIR, "ability_dash.png")
JOAO_ABILITY_ICON = os.path.join(ASSETS_DIR, "ability_speed.png")
MESKY_ABILITY_ICON = os.path.join(ASSETS_DIR, "ability_slow.png")
CHOSEN_ABILITY_ICON = os.path.join(ASSETS_DIR, "ability_immunity.png")

# Dictionary to map character index to icon path
ABILITY_ICONS = {
    1: SEEDGUY_ABILITY_ICON,
    2: JOAO_ABILITY_ICON, # Joao uses speed icon
    3: MESKY_ABILITY_ICON, # Mesky uses slow icon
    4: CHOSEN_ABILITY_ICON, # Chosen uses immunity icon
}

# --- WORLD BACKGROUNDS ---
WORLD_BACKGROUNDS = {
    "Earth World": os.path.join(ASSETS_DIR, "earth.png"),
    "Water World": os.path.join(ASSETS_DIR, "water.png"),
    "Frost World": os.path.join(ASSETS_DIR, "frost.png"),
    "Fire World": os.path.join(ASSETS_DIR, "fire.png"),
    "Underworld": os.path.join(ASSETS_DIR, "underworld.png"),
    "Desert World": os.path.join(ASSETS_DIR, "desert.png"),
    "Jungle World": os.path.join(ASSETS_DIR, "jungle.png"),
    "Space World": os.path.join(ASSETS_DIR, "space.png"),
    "Cyber World": os.path.join(ASSETS_DIR, "cyber.png"),
    "Mystic World (Inverse Controls)": os.path.join(ASSETS_DIR, "mystic.png"),
    "Superseed World": os.path.join(ASSETS_DIR, "superseedworld.png"), # Renamed key and assumed file name change
}

# --- SOUND FILE PATHS ---
BG_MUSIC = os.path.join(MEDIA_DIR, "bg_music.mp3") # Main menu music
INGAME_MUSIC = os.path.join(MEDIA_DIR, "ingamemusic.mp3") # In-game music
DEAD_SOUND = os.path.join(MEDIA_DIR, "dead.mp3")
COLLECT_SOUND = os.path.join(MEDIA_DIR, "collect.mp3")
START_SOUND = os.path.join(MEDIA_DIR, "start.mp3")
CLICK_SOUND = os.path.join(MEDIA_DIR, "click.mp3")
MAGNET_SOUND = os.path.join(MEDIA_DIR, "magnet_activate.mp3")
FREEZE_SOUND = os.path.join(MEDIA_DIR, "freeze.mp3")
BREAK_SHIELD_SOUND = os.path.join(MEDIA_DIR, "breakshield.mp3") # <<< NEW
SHOOTER_CHARGE_SOUND = os.path.join(MEDIA_DIR, "shooter_charge.mp3") # <<< NEW
DAVID_DASH_SOUND = os.path.join(MEDIA_DIR, "david_dash.mp3") # <<< NEW
POWERUP_SHIELD_SOUND = os.path.join(MEDIA_DIR, "powerup_shield.mp3") # <<< NEW
POWERUP_DOUBLE_SOUND = os.path.join(MEDIA_DIR, "powerup_double.mp3") # <<< NEW

# Character ability sounds
XDASH_SOUND = os.path.join(MEDIA_DIR, "xdash.mp3")
XSPEED_SOUND = os.path.join(MEDIA_DIR, "xspeed.mp3")
XSLOW_SOUND = os.path.join(MEDIA_DIR, "xslow.mp3")
XIMMUNITY_SOUND = os.path.join(MEDIA_DIR, "ximmunity.mp3")
# Character selection sounds
SEEDGUY_SELECT_SOUND = os.path.join(MEDIA_DIR, "seedguy.mp3")
JOAO_SELECT_SOUND = os.path.join(MEDIA_DIR, "joao.mp3")
MESKY_SELECT_SOUND = os.path.join(MEDIA_DIR, "mesky.mp3")
CHOSEN_SELECT_SOUND = os.path.join(MEDIA_DIR, "chosen.mp3")

# --- GAME SETTINGS ---
# --- NEW: Screen Shake ---
SCREEN_SHAKE_DURATION = 0.2 # seconds
SCREEN_SHAKE_MAGNITUDE = 5 # pixels max offset
# --- END NEW ---

# Player Movement Physics Adjustments
BASE_PLAYER_MAX_SPEED = 3.6 * 60 # Base speed (pixels/sec)
BASE_PLAYER_ACCEL = 2.0 * 60 * 60 # Acceleration
# --- Optional Physics Tuning: Lower friction slightly ---
PLAYER_FRICTION = 0.955 # Friction <<< REDUCED FURTHER SLIGHTLY (was 0.96)
# --- END Tuning ---
PLAYER_ROT_SPEED = 270 # Rotation speed

# Player Bounce Animation
PLAYER_BOUNCE_ENABLED = True # <<< NEW: Toggle for bounce animation
PLAYER_BOUNCE_AMOUNT = 2 # Pixels to move up/down
PLAYER_BOUNCE_SPEED = 6.0 # How fast the bounce cycles

# --- RESTORED: Weather Particle Counts ---
RAIN_DROP_COUNT = 100
RAIN_SPEED_MIN = 8
RAIN_SPEED_MAX = 14
RAIN_LENGTH_MIN = 2
RAIN_LENGTH_MAX = 4
RAIN_COLOR = (173, 216, 230) # Light blue

SNOW_FLAKE_COUNT = 70
SNOW_SPEED_MIN = 1
SNOW_SPEED_MAX = 3
SNOW_RADIUS_MIN = 2
SNOW_RADIUS_MAX = 4
SNOW_COLOR = (240, 248, 255) # Alice Blue / very light grey

WIND_STREAK_COUNT = 15
WIND_STREAK_LENGTH = 20
WIND_COLOR = (200, 200, 200)
# --- END RESTORED ---


ENEMY_SPEED_MULTIPLIER = 0.92 # Base multiplier for non-David enemies
# --- FIX: Revert ENEMY_BOUNCE_FACTOR ---
ENEMY_BOUNCE_FACTOR = 0.95 # <<< How much speed is retained on wall bounce (Reverted from 0.76)
# --- END FIX ---

SCORES_FILE = "scores.txt"
MAX_SCORES_TO_KEEP = 15 # Max scores saved in file
MAX_SCORES_DISPLAY = 20 # Max scores to display on screen before scrolling needed
MAX_LEVEL = 100

INITIAL_CHECKPOINT_COUNT = 3 # Default starting checkpoints (free to use)
MIN_ENEMY_SPAWN_DIST_FROM_PLAYER = 450 # Minimum distance enemies should spawn from player start (Increased from 120)

# --- SHOOTER ENEMY SETTINGS ---
SHOOTER_SHOT_INTERVAL = 1000  # milliseconds
PROJECTILE_SPEED = 5.2 * 60 # Pixels per second
PROJECTILE_LEAD_TIME = 0.5 # How far ahead to aim (seconds)
# --- NEW: Shooter Charging ---
SHOOTER_CHARGE_TIME = 0.3 # seconds before firing after interval
# --- END NEW ---

# --- FONT SETTINGS ---
pygame.font.init()
# Define font objects once using Impact
try:
    FONT_IMPACT_LG = pygame.font.SysFont("impact", 64)
    FONT_IMPACT_MD = pygame.font.SysFont("impact", 48)
    FONT_IMPACT_SM = pygame.font.SysFont("impact", 32)
    FONT_IMPACT_XSM = pygame.font.SysFont("impact", 24)
    FONT_IMPACT_XXSM = pygame.font.SysFont("impact", 20)
    FONT_IMPACT_XXXSM = pygame.font.SysFont("impact", 18) # <<< Added one smaller size
    FONT_IMPACT_TINY = pygame.font.SysFont("impact", 16)
    # --- Define fonts using Impact for leaderboard and hall ---
    FONT_LEADERBOARD_HEADER = pygame.font.SysFont("impact", 32) # Impact SM for header
    FONT_LEADERBOARD_SCORE = pygame.font.SysFont("impact", 48)  # Impact MD for scores
    FONT_HALL_SUPR_COUNT = pygame.font.SysFont("impact", 42) # Impact 42pt for Hall SUPR count
except Exception as e:
    print(f"Error loading system fonts: {e}. Using default pygame font.")
    # Fallback to default font if system fonts fail
    FONT_IMPACT_LG = pygame.font.Font(None, 64)
    FONT_IMPACT_MD = pygame.font.Font(None, 48)
    FONT_IMPACT_SM = pygame.font.Font(None, 32)
    FONT_IMPACT_XSM = pygame.font.Font(None, 24)
    FONT_IMPACT_XXSM = pygame.font.Font(None, 20)
    FONT_IMPACT_XXXSM = pygame.font.Font(None, 18) # <<< Added fallback
    FONT_IMPACT_TINY = pygame.font.Font(None, 16)
    # Fallback fonts for leaderboard and hall
    FONT_LEADERBOARD_HEADER = pygame.font.Font(None, 32)
    FONT_LEADERBOARD_SCORE = pygame.font.Font(None, 48)
    FONT_HALL_SUPR_COUNT = pygame.font.Font(None, 42) # Fallback for Hall SUPR font

# UI Font Aliases (mapping to consistent names for clarity in ui.py)
ATTR_FONT = FONT_IMPACT_TINY
STORY_FONT = FONT_IMPACT_XXXSM
BUTTON_FONT = FONT_IMPACT_XSM # Default button font
MENU_BUTTON_FONT = FONT_IMPACT_XSM # Font for main menu and back buttons
VAULT_SHOP_BUTTON_FONT = FONT_IMPACT_XXXSM # <<< CHANGED FONT ALIAS
VAULT_COST_FONT = FONT_IMPACT_XXXSM      # Vault Cost Text Font
VAULT_CLOSE_BUTTON_FONT = FONT_IMPACT_XXSM # Font for vault close
LEVEL_TEXT_FONT = FONT_IMPACT_SM
TITLE_FONT = FONT_IMPACT_MD
FONT_WEATHER = FONT_IMPACT_XXSM
CP_FONT = FONT_IMPACT_XSM # Checkpoint button font
FONT_LG = FONT_IMPACT_LG # Large Font Alias
FONT_MD = FONT_IMPACT_MD # Medium Font Alias
FONT_SM = FONT_IMPACT_SM # Small Font Alias
FONT_TINY = FONT_IMPACT_TINY # Tiny Font Alias

# Cumulative size increase factors (applied in game_objects.py)
PLAYER_CUMULATIVE_SIZE_INCREASE = 2.673 # <<< INCREASED SIZE (was 1.98, now +35%)
# --- FIX: Adjust enemy size factors ---
ENEMY_CUMULATIVE_SIZE_INCREASE = 1.6 # Reduced from 2.0 (20% smaller)
DAVID_SIZE_MULTIPLIER = 1.6 # Match new enemy size
SHOOTER_SIZE_MULTIPLIER = 1.6 # Match new enemy size
# --- END FIX ---
POWERUP_CUMULATIVE_SIZE_INCREASE = 1.94 # REDUCED SIZE (was 2.5875, reduced by ~25%)
SEED_SIZE_MULTIPLIER = 1.68 # Seed size further reduced: 2.4 * (1 - 0.3) = 1.68 (another 30% reduction)


# --- Character Ability Constants ---
SEEDGUY_COOLDOWN = 6
JOAO_COOLDOWN = 30
MESKY_COOLDOWN = 30
CHOSEN_SEED_COOLDOWN = 45 # <<< FIX: Reduced from 60

# --- CHANGE: Updated Mesky Duration ---
JOAO_DURATION = 5
MESKY_DURATION = 5 # Duration of Mesky's slow field
CHOSEN_SEED_DURATION = 5
# --- END CHANGE ---

# --- NEW: Ability Visual Effect Size ---
# --- FIX: Increase Chosen Seed ability animation size factor ---
ABILITY_ANIMATION_SIZE_FACTOR = 1.0 # Default size factor
ABILITY_ANIMATION_SIZE_FACTOR_CHOSEN = 1.1 # <<< 10% larger for Chosen Seed
# --- END FIX ---
# --- FIX: Ability effect duration ---
ABILITY_EFFECT_DURATION = 0.5 # seconds for the visual effect
# --- END FIX ---

# --- NEW: David Dash Behavior ---
DAVID_DASH_INTERVAL_MIN = 3.0 # seconds
DAVID_DASH_INTERVAL_MAX = 6.0 # seconds
DAVID_DASH_RANGE_SQ = (300**2) # Distance within which David might dash
DAVID_DASH_PREP_TIME = 0.4 # seconds to stop and flash
DAVID_DASH_DURATION = 0.5 # seconds of high speed dash
DAVID_DASH_SPEED_MULTIPLIER = 3.0 # Speed multiplier during dash
# --- END NEW ---

# --- Powerup Durations ---
FREEZE_DURATION = 2.0 # Seconds
MAGNET_DURATION = 3.0 # Seconds
MAGNET_PICKUP_RADIUS_MULTIPLIER = 1.35 # Increase pickup radius by 35% when magnet active
# --- NEW: Powerup Durations ---
SHIELD_POWERUP_DURATION = 10.0 # Seconds for temporary shield
DOUBLE_SEED_DURATION = 6.0 # Seconds for double seeds
# --- END NEW ---

# --- Achievement Tiers ---
ACHIEVEMENT_TIERS = {
    "Bronze": BRONZE,
    "Silver": SILVER,
    "Gold": GOLD
}
ACHIEVEMENT_SUPR_REWARDS = {
    "Bronze": 1,
    "Silver": 2,
    "Gold": 3
}
ACHIEVEMENT_BANNER_DURATION = 3.0 # <<< INCREASED DURATION (was 2.0)

# --- Achievement Constants (Renamed/Added) ---
# Bronze
ACH_SPROUTED = "Sprouted" # Replaces Superseed
ACH_ATTRACTOR_NODE = "Attractor Node" # Replaces Magnetic Seed
ACH_WARP_SPEED_ENGAGED = "Warp Speed Engaged" # Replaces Speed Demon
ACH_NAVIGATING_THE_NOISE = "Navigating the Noise" # Replaces Master of Inversion
ACH_EARTH_SEEDED = "Earth Seeded" # Replaces Earth Planet
ACH_FIRE_SEEDED = "Fire Seeded"
ACH_WATER_SEEDED = "Water Seeded"
ACH_FROST_SEEDED = "Frost Seeded"
ACH_UNDERWORLD_SEEDED = "Underworld Seeded"
ACH_DESERT_SEEDED = "Desert Seeded"
ACH_JUNGLE_SEEDED = "Jungle Seeded"
ACH_SPACE_SEEDED = "Space Seeded"
ACH_CYBER_SEEDED = "Cyber Seeded"
ACH_MYSTIC_SEEDED = "Mystic Seeded"
ACH_SUPERSEED_SEEDED = "Superseed Seeded"

# Silver
ACH_GRAVITY_WELL = "Gravity Well" # Replaces Magnetic Genius
ACH_BOUNTIFUL_HARVEST = "Bountiful Harvest" # Replaces Seed Collector
ACH_SEED_HARVEST_VICTOR = "Seed Harvest Victor" # Replaces Minigame 1 Complete
ACH_DAVID_REVENGE_VICTOR = "David's Revenge Victor" # Replaces Minigame 2 Complete
ACH_INVERSE_GAUNTLET_VICTOR = "Inverse Gauntlet Victor" # Replaces Minigame 3 Complete
ACH_DIAMOND_HANDS = "Diamond Hands" # New Silver: Hold 100+ seeds at level end
ACH_PACIFIST_RUN = "Pacifist Run" # New Silver: Beat a level >= 20 without using ability

# Gold
ACH_SEED_SINGULARITY = "Seed Singularity" # Replaces Magnetic Master Seed
ACH_MAINNET_MAGNET = "Mainnet Magnet" # Replaces Magnetic God of Seeds
ACH_SEED_BANK_BARON = "Seed Bank Baron" # Replaces Seed Hoarder
ACH_TGE_ACHIEVED = "TGE Achieved!" # Replaces WEN TGE?
ACH_WIN_SEEDGUY = "The One Who Did Not Give Up" # New Gold: Win with SeedGuy
ACH_WIN_JOAO = "David's Favorite Developer" # New Gold: Win with Joao
ACH_WIN_MESKY = "Market Turned Bullish" # New Gold: Win with Mesky
ACH_WIN_CHOSEN = "For the Community!" # New Gold: Win with Chosen
ACH_TRUE_SUPERSEED = "True Superseed" # New Gold: Unlock all other achievements

# --- Master Achievement List (Updated) ---
MASTER_ACHIEVEMENT_LIST = [
    # Bronze
    ACH_SPROUTED, ACH_ATTRACTOR_NODE, ACH_WARP_SPEED_ENGAGED, ACH_NAVIGATING_THE_NOISE,
    ACH_EARTH_SEEDED, ACH_FIRE_SEEDED, ACH_WATER_SEEDED, ACH_FROST_SEEDED, ACH_UNDERWORLD_SEEDED,
    ACH_DESERT_SEEDED, ACH_JUNGLE_SEEDED, ACH_SPACE_SEEDED, ACH_CYBER_SEEDED, ACH_MYSTIC_SEEDED, ACH_SUPERSEED_SEEDED,
    # Silver
    ACH_GRAVITY_WELL, ACH_BOUNTIFUL_HARVEST, ACH_SEED_HARVEST_VICTOR, ACH_DAVID_REVENGE_VICTOR, ACH_INVERSE_GAUNTLET_VICTOR,
    ACH_DIAMOND_HANDS, ACH_PACIFIST_RUN,
    # Gold
    ACH_SEED_SINGULARITY, ACH_MAINNET_MAGNET, ACH_SEED_BANK_BARON, ACH_TGE_ACHIEVED,
    ACH_WIN_SEEDGUY, ACH_WIN_JOAO, ACH_WIN_MESKY, ACH_WIN_CHOSEN, ACH_TRUE_SUPERSEED
]
ACHIEVEMENT_INFO = {
    # Bronze
    ACH_SPROUTED: "Sprout your journey! (Play at least one game)",
    ACH_ATTRACTOR_NODE: "Activate the first node. (Collect 25 magnets)",
    ACH_WARP_SPEED_ENGAGED: "Clear a level in under 2 seconds.",
    ACH_NAVIGATING_THE_NOISE: "Survive the inverted controls of Mystic World.",
    ACH_EARTH_SEEDED: "Reach Earth World.",
    ACH_FIRE_SEEDED: "Reach Fire World.",
    ACH_WATER_SEEDED: "Reach Water World.",
    ACH_FROST_SEEDED: "Reach Frost World.",
    ACH_UNDERWORLD_SEEDED: "Reach the Underworld.",
    ACH_DESERT_SEEDED: "Reach Desert World.",
    ACH_JUNGLE_SEEDED: "Reach Jungle World.",
    ACH_SPACE_SEEDED: "Reach Space World.",
    ACH_CYBER_SEEDED: "Reach Cyber World.",
    ACH_MYSTIC_SEEDED: "Reach Mystic World.",
    ACH_SUPERSEED_SEEDED: "Reach the Superseed World.",
    # Silver
    ACH_GRAVITY_WELL: "Strengthen the pull. (Collect 50 magnets)",
    ACH_BOUNTIFUL_HARVEST: "Collect 100 seeds in a single race.",
    ACH_SEED_HARVEST_VICTOR: "Win the Seed Harvest Frenzy minigame.",
    ACH_DAVID_REVENGE_VICTOR: "Survive David’s Revenge minigame.",
    ACH_INVERSE_GAUNTLET_VICTOR: "Conquer the Inverse Gauntlet minigame.",
    ACH_DIAMOND_HANDS: "Finish a level holding 100 or more seeds.",
    ACH_PACIFIST_RUN: "Clear level 20 or higher without using your ability.",
    # Gold
    ACH_SEED_SINGULARITY: "Master the magnetic fields. (Collect 75 magnets)",
    ACH_MAINNET_MAGNET: "Become a magnet god. (Collect 100 magnets)",
    ACH_SEED_BANK_BARON: "Amass a fortune. (Collect 1000 total seeds)",
    # --- FIX: Updated TGE Achieved description ---
    ACH_TGE_ACHIEVED: "Reach the Mainnet! (Win level 100 in under 30 mins)",
    # --- END FIX ---
    ACH_WIN_SEEDGUY: "Win the game as SeedGuy.",
    ACH_WIN_JOAO: "Win the game as Joao.",
    ACH_WIN_MESKY: "Win the game as Mesky.",
    ACH_WIN_CHOSEN: "Win the game as The Chosen Seed.",
    ACH_TRUE_SUPERSEED: "Unlock all other achievements."
}
ACHIEVEMENT_TIER_MAP = {
    # Gold Tier
    ACH_SEED_SINGULARITY: "Gold", ACH_MAINNET_MAGNET: "Gold", ACH_SEED_BANK_BARON: "Gold",
    ACH_TGE_ACHIEVED: "Gold", ACH_WIN_SEEDGUY: "Gold", ACH_WIN_JOAO: "Gold",
    ACH_WIN_MESKY: "Gold", ACH_WIN_CHOSEN: "Gold", ACH_TRUE_SUPERSEED: "Gold",
    # Silver Tier
    ACH_GRAVITY_WELL: "Silver", ACH_BOUNTIFUL_HARVEST: "Silver", ACH_SEED_HARVEST_VICTOR: "Silver",
    ACH_DAVID_REVENGE_VICTOR: "Silver", ACH_INVERSE_GAUNTLET_VICTOR: "Silver",
    ACH_DIAMOND_HANDS: "Silver", ACH_PACIFIST_RUN: "Silver",
    # Bronze Tier (Default for the rest)
    ACH_SPROUTED: "Bronze", ACH_ATTRACTOR_NODE: "Bronze", ACH_WARP_SPEED_ENGAGED: "Bronze",
    ACH_NAVIGATING_THE_NOISE: "Bronze", ACH_EARTH_SEEDED: "Bronze", ACH_FIRE_SEEDED: "Bronze",
    ACH_WATER_SEEDED: "Bronze", ACH_FROST_SEEDED: "Bronze", ACH_UNDERWORLD_SEEDED: "Bronze",
    ACH_DESERT_SEEDED: "Bronze", ACH_JUNGLE_SEEDED: "Bronze", ACH_SPACE_SEEDED: "Bronze",
    ACH_CYBER_SEEDED: "Bronze", ACH_MYSTIC_SEEDED: "Bronze", ACH_SUPERSEED_SEEDED: "Bronze",
}


# --- MINIGAME CONSTANTS ---
MINIGAME1_DURATION = 10000 # ms (Seed Harvest Frenzy)
MINIGAME1_SEED_RANGE = (15, 30)

MINIGAME2_DURATION = 30000 # ms (David's Revenge)
MINIGAME2_SPAWN_RATE = 3000 # ms (Spawn every 3 seconds)
MINIGAME2_ENEMY_COUNT = 10 # Total enemies to spawn
MINIGAME2_MIN_SPAWN_DIST = 150 # pixels from player

MINIGAME3_SHOOTER_COUNT = 1 # Reduced from 2
MINIGAME3_ENEMY_COUNT = 9

# --- VAULT COSTS ---
VAULT_COST_NODE_SPEED = 3
VAULT_COST_EXTRA_LIFE = 4 # Increases MAX checkpoint capacity
VAULT_COST_MULTIPLIER = 10
VAULT_COST_RADIUS_BASE = 5 # <<< CHANGED FROM 15 to 5
VAULT_COST_RADIUS_INCREMENT = 0 # << CHANGED FROM 5 to 0 (Cost is now flat 5)
VAULT_COST_COOLDOWN = 5
VAULT_COST_SHIELD = 7
VAULT_COST_AURA = 4
VAULT_COST_BLESSING = 6

VAULT_MAX_LEVELS = {
    "node_speed_boost": 2,
    "extra_life": 2,
    "seed_multiplier": 1,
    "seed_radius": 5, # <<< CHANGED FROM 10 to 5
    "cooldown_reduction": 1,
    "starting_shield": 1,
    "enemy_slow_aura": 2,
    "blessing_superseed": 1
}

# --- SHOP COSTS ---
SHOP_SPEED_COST_FACTOR = 5
SHOP_SEED_ENEMY_COST_FACTOR = 8 # Lowered from 10
SHOP_SEED_ENEMY_MAX_LEVEL = 10
SHOP_SHIELD_COST_LOW = 20
SHOP_SHIELD_COST_HIGH = 40
SHOP_SHIELD_LEVEL_THRESHOLD = 50
SHOP_SLOW_COST_LOW = 25
SHOP_SLOW_COST_MID = 35
SHOP_SLOW_COST_HIGH = 40
SHOP_SLOW_LEVEL_THRESH1 = 50
SHOP_SLOW_LEVEL_THRESH2 = 90
SHOP_CHECKPOINT_COST = 40 # Cost to *purchase* one checkpoint charge
SHOP_SPEED_ENEMY_BOOST_FACTOR = 0.02 # Each player speed level increases enemy speed by 2%

# --- POWERUP CHANCES ---
POWERUP_CHANCE_BASE = 0.15 # <<< INCREASED (was 0.07)
POWERUP_CHANCE_BLESSING = 0.25 # Base chance + 10% (15% + 10% = 25%)
# --- NEW: Powerup Weights ---
# More likely to get Magnet/Freeze, less likely Shield/Double
POWERUP_WEIGHTS = {
    "freeze": 30,
    "magnet": 30,
    "shield": 20,
    "double": 20,
}
# --- END NEW ---

# --- PLAYER TRAIL ---
TRAIL_LENGTH = 30

# --- SIZES ---
ORIGINAL_PLAYER_BASE_WIDTH = 50
ORIGINAL_PLAYER_BASE_HEIGHT = 35
ORIGINAL_ENEMY_BASE_SIZE = 35
ORIGINAL_SEED_BASE_SIZE = 25
ORIGINAL_POWERUP_BASE_SIZE = 45 # Base size for Magnet/Freeze/Shield/Double
ORIGINAL_SHOOTER_BASE_WIDTH = 40
ORIGINAL_SHOOTER_BASE_HEIGHT = 40
# --- END OF FILE settings.py ---