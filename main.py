# --- START OF FILE main.py ---


import pygame, os, time, random, math, json, sys, traceback

# --- Library Import with Detailed Checks ---
MOVIEPY_AVAILABLE = False
NUMPY_AVAILABLE = False
np = None
VideoFileClip = None # Initialize as None

print("--- Checking Required Libraries ---")
try:
    # Attempt NumPy import first
    try:
        import numpy as np
        NUMPY_AVAILABLE = True
        print("[Import Check] NumPy library FOUND.")
    except ImportError as e_np:
        print(f"[Import Check] NumPy Import Warning: {e_np}")
        print("[Import Check] NumPy is required for video playback.")
        np = None # Ensure np is None if import failed
    except Exception as e_np_other:
        print(f"[Import Check] An unexpected error occurred during NumPy import: {e_np_other}")
        traceback.print_exc()
        np = None # Ensure np is None on other errors

    # Attempt MoviePy import only if NumPy succeeded
    if NUMPY_AVAILABLE:
        try:
            # Using the direct import style for VideoFileClip
            from moviepy.video.io.VideoFileClip import VideoFileClip # Import specific class
            MOVIEPY_AVAILABLE = True
            print("[Import Check] MoviePy library FOUND.")
        except ImportError as e_mvpy:
            print(f"[Import Check] MoviePy Import Warning (using 'from moviepy.video.io.VideoFileClip import VideoFileClip'): {e_mvpy}")
            print("[Import Check] MoviePy is required for video playback.")
            VideoFileClip = None # Ensure VideoFileClip is None
        except Exception as e_mvpy_other:
            print(f"[Import Check] An unexpected error occurred during MoviePy import: {e_mvpy_other}")
            traceback.print_exc()
            VideoFileClip = None # Ensure VideoFileClip is None
    else:
        print("[Import Check] Skipping MoviePy check because NumPy is missing.")
        VideoFileClip = None

    if not NUMPY_AVAILABLE or not MOVIEPY_AVAILABLE:
        print("-" * 30)
        print("!! Import Warning !!")
        if not NUMPY_AVAILABLE:
            print("- NumPy library not found or failed to import.")
        if not MOVIEPY_AVAILABLE:
            print("- MoviePy library not found or failed to import.")
        print("- Video playback functionality will be disabled.")
        print("- Please ensure both are installed: `pip install numpy moviepy`")
        print("-" * 30)

except Exception as e_outer:
    # Catch any other unexpected errors during the import block
    print(f"[Import Check] An critical error occurred during library import phase: {e_outer}")
    traceback.print_exc()
    # Ensure flags are False and variables are None
    MOVIEPY_AVAILABLE = False
    NUMPY_AVAILABLE = False
    np = None
    VideoFileClip = None
    print("[Import Check] Video playback disabled due to critical import error.")

print("--- Library Check Complete ---")
# --- End Library Import ---


from settings import *
# --- Import game objects including new powerups and effects ---
from game_objects import (Player, Enemy, CollectibleSeed, FinishLine, ShooterEnemy,
                          Projectile, Particle, MagnetPowerUp, FreezePowerUp,
                          ShieldPowerUp, DoubleSeedPowerUp, AbilityEffect,
                          create_shield_break_particles, David, EarthEnemy,
                          FireEnemy, WaterEnemy, FrostEnemy, UnderworldEnemy,
                          DesertEnemy, JungleEnemy, SpaceEnemy, CyberEnemy,
                          MysticEnemy, SuperseedEnemy) # Updated import list
# --- Import UI elements including new ones ---
from ui import (draw_game_border, draw_current_world_and_weather,
                show_level_clear, pause_menu, main_menu, display_leaderboard, hall_of_seeds,
                character_select, repayment_vault_shop, announce_mini_game, show_tutorial_image,
                LEVEL_TEXT_FONT, FONT_MD, FONT_SM, TITLE_FONT, BUTTON_FONT, FONT_TINY, FONT_IMPACT_XSM, FONT_IMPACT_XXXSM, # Added FONT_IMPACT_XXXSM
                draw_plain_button, play_click_sound, show_game_over, draw_shield_aura,
                draw_checkpoint_button, CHECKPOINT_RECT, draw_shop_button, SHOP_BUTTON_RECT,
                show_ingame_shop_overlay,
                draw_attributes, draw_ability_icon, play_freeze_sound, show_manwha_reader,
                draw_help_button, HELP_BUTTON_RECT, show_controls_overlay,
                draw_seed_doubler_timer, draw_screen_flash, get_scene_color, show_world_transition, # <<< Added get_scene_color, show_world_transition
                CP_BUTTON_RIGHT_MARGIN, show_win_screen, CP_FONT) # <-- Import CP_BUTTON_RIGHT_MARGIN from ui, Import show_win_screen, Import CP_FONT
from minigame import minigame_1, minigame_2, minigame_3

save_data = {} # Global dictionary for save data
unlocked_achievements_this_session_main = set() # Track achievements across a full game run

# --- save_save_data function MUST be defined before load_save_data uses it internally ---
def save_save_data(data):
    """Saves the provided data dictionary to save_data.json."""
    try:
        with open("save_data.json", "w") as f:
            json.dump(data, f, indent=4)
        # print("Save data written to file.") # Optional confirmation
    except Exception as e:
        print(f"Error saving data: {e}")
# ---------------------------------------------------------------------------------------

def circle_collision(sprite1, sprite2):
    # Prioritize using pos_x/pos_y and radius if available
    px = getattr(sprite1, 'pos_x', None)
    py = getattr(sprite1, 'pos_y', None)
    ox = getattr(sprite2, 'pos_x', None)
    oy = getattr(sprite2, 'pos_y', None)
    pr = getattr(sprite1, 'radius', None)
    orad = getattr(sprite2, 'radius', None)

    # If circle properties are available for both, use circle collision
    if px is not None and py is not None and ox is not None and oy is not None and pr is not None and orad is not None:
        dx = px - ox
        dy = py - oy
        distance_sq = dx*dx + dy*dy
        radius_sum = pr + orad
        # Add a small tolerance to prevent collision when exactly touching
        return distance_sq < (radius_sum * radius_sum) * 0.98 # Check if distance is slightly less than sum of radii

    # --- Fallback to Rect Collision if circle properties are missing ---
    # Use rect centers as fallback positions if pos_x/y missing
    rect1 = getattr(sprite1, 'rect', None)
    rect2 = getattr(sprite2, 'rect', None)

    if rect1 is None or rect2 is None:
        print("Warning: Cannot perform collision check - sprites missing rect.")
        return False # Cannot collide if rects are missing

    # Use rect-based collision if circle properties were incomplete
    # print("Warning: Falling back to rect collision.") # Optional debug
    return pygame.sprite.collide_rect(sprite1, sprite2)

# --- CORRECTED: Definition moved back to main.py ---
def collide_circle_precise_seed(player_sprite, seed_sprite):
    """
    Custom collision function for player-seed interaction.
    Uses player's potentially augmented pickup radius.
    """
    # Player properties
    px = getattr(player_sprite, 'pos_x', player_sprite.rect.centerx)
    py = getattr(player_sprite, 'pos_y', player_sprite.rect.centery)
    # Calculate player's effective radius including vault bonus
    player_base_radius = getattr(player_sprite, 'radius', player_sprite.rect.width / 2 * 0.8) # Default scaling like Enemy
    player_vault_bonus = getattr(player_sprite, 'vault_pickup_radius_bonus', 0)
    player_effective_radius = player_base_radius + player_vault_bonus

    # Seed properties
    sx = getattr(seed_sprite, 'pos_x', seed_sprite.rect.centerx)
    sy = getattr(seed_sprite, 'pos_y', seed_sprite.rect.centery)
    # Seed radius might have its own scaling factor (using 1.1 from CollectibleSeed definition)
    seed_radius = getattr(seed_sprite, 'radius', seed_sprite.rect.width / 2 * 1.1)

    # Check for missing attributes (shouldn't happen with Player/Seed)
    if px is None or py is None or sx is None or sy is None:
        return False # Cannot perform circle collision

    # Distance check
    dx = px - sx
    dy = py - sy
    distance_sq = dx*dx + dy*dy
    radius_sum = player_effective_radius + seed_radius
    return distance_sq < (radius_sum * radius_sum)
# --- END CORRECTION ---

def load_scores():
    try:
        if not os.path.exists(SCORES_FILE):
            return [] # Return empty list if file doesn't exist
        scores = []
        with open(SCORES_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue # Skip empty lines
                try:
                    parts = line.split(',')
                    if len(parts) == 4:
                        name = parts[0]
                        level = int(parts[1])
                        total_time = float(parts[2])
                        total_seeds = int(parts[3])
                        scores.append((name, level, total_time, total_seeds))
                    else:
                        print(f"Skipping malformed score line: {line}")
                except ValueError as e:
                    print(f"Error parsing score line '{line}': {e}")
                    continue # Skip lines with parsing errors
        # Sort scores: primarily by level descending, secondarily by time ascending
        scores.sort(key=lambda x: (-x[1], x[2]))
        return scores
    except Exception as e:
        print(f"Error loading scores from {SCORES_FILE}: {e}")
        return [] # Return empty list on error


def save_score(player_name, level_reached, total_time, seeds_collected_run):
    if not player_name or not player_name.strip(): player_name = "Player" # Default name
    try:
        scores = load_scores() # Load existing scores
        scores.append((player_name, level_reached, total_time, seeds_collected_run)) # Add new score
        scores.sort(key=lambda x: (-x[1], x[2])) # Re-sort
        scores_to_save = scores[:MAX_SCORES_TO_KEEP] # Keep only the top scores
        with open(SCORES_FILE, "w") as f:
            for name, lvl, time_val, seeds in scores_to_save:
                f.write(f"{name},{lvl},{time_val:.4f},{seeds}\n") # Write formatted scores
    except Exception as e:
        print(f"Error saving score: {e}")


def get_scene_description(level):
    level = max(1, level) # Ensure level is at least 1
    if level < 10: return "Earth World"
    elif level < 21: return "Fire World"
    elif level < 31: return "Water World"
    elif level < 41: return "Frost World"
    elif level < 51: return "Underworld" # Updated world name
    elif level < 61: return "Desert World"
    elif level < 71: return "Jungle World"
    elif level < 81: return "Space World"
    elif level < 91: return "Cyber World"
    elif level < 95: return "Mystic World (Inverse Controls)"
    else: return "Superseed World" # Renamed

# Fallback removed as get_scene_color is now correctly imported from ui.py


def load_save_data():
    """Loads game save data from save_data.json, initializing defaults if needed."""
    global save_data # Use the global save_data dictionary
    default_data = {
        "tutorial_shown": False, # Track if tutorial images have been shown automatically
        "story_shown": False, # Track if story video has been shown automatically
        "selected_character": 1,
        "unlocked_characters": [1, 2, 3, 4], # Default unlocked characters
        "achievements": [],
        "character_images": { # Default character image filenames
            "1": os.path.basename(SEEDGUY_DISPLAY_IMAGE),
            "2": os.path.basename(JOAO_DISPLAY_IMAGE),
            "3": os.path.basename(MESKY_DISPLAY_IMAGE),
            "4": os.path.basename(CHOSEN_DISPLAY_IMAGE)
        },
        "supercollateral_coins": 0, # Internal key name remains the same
        "vault_upgrades": { # Default vault upgrade levels
            "node_speed_boost": 0, "extra_life": 0, "seed_multiplier": 0,
            "seed_radius": 0, "cooldown_reduction": 0, "starting_shield": 0,
            "enemy_slow_aura": 0, "blessing_superseed": 0
        },
        "total_seeds_accumulated": 0,
        "total_magnets_collected": 0,
        "total_runs_completed": 0, # New stat
        "highest_level_reached": 0, # New stat
        "total_time_played": 0.0, # New stat
    }
    save_file_path = "save_data.json"

    if os.path.exists(save_file_path):
        try:
            with open(save_file_path, "r") as f:
                data = json.load(f)
            needs_update = False # Flag to check if save file needs updating

            # Check and update missing top-level keys
            for key, default_value in default_data.items():
                if key not in data:
                    data[key] = default_value
                    needs_update = True
                # Special handling for nested dictionaries (vault_upgrades, character_images)
                elif key in ["vault_upgrades", "character_images"] and isinstance(default_value, dict):
                    # Ensure the loaded value is also a dictionary
                    if not isinstance(data.get(key), dict):
                        data[key] = {} # Reset to empty dict if it's not a dict
                        needs_update = True
                    # Check for missing keys within the nested dictionary
                    for sub_key, sub_default_value in default_value.items():
                        if sub_key not in data[key]:
                             data[key][sub_key] = sub_default_value
                             needs_update = True
                    # Clean up old/removed keys if necessary (example: 'speed_boost')
                    if key == "vault_upgrades" and 'speed_boost' in data[key]:
                        del data[key]['speed_boost']
                        needs_update = True

            save_data = data # Assign loaded/updated data to global variable
            if needs_update:
                print("Save data updated with new defaults...")
                save_save_data(save_data) # Save the updated data back to file
            else:
                print("Save data loaded.")
        except json.JSONDecodeError as e:
            print(f"Error decoding save_data.json: {e}. Creating new default file.")
            save_data = default_data.copy() # Use defaults
            save_save_data(save_data) # Create the file with defaults
        except Exception as e:
            print(f"Error loading/updating save_data.json: {e}. Using defaults.")
            save_data = default_data.copy() # Use defaults on other errors
            save_save_data(save_data) # Attempt to save defaults
    else:
        # If save file doesn't exist, create it with defaults
        print("save_data.json not found. Creating defaults.")
        save_data = default_data.copy()
        save_save_data(save_data)


def save_checkpoint(player, seed_count, shop_upgrades, level, checkpoint_count, difficulty, last_ability_time):
    """Creates a dictionary containing the checkpoint state."""
    return {
        "level": level,
        "position": (player.pos_x, player.pos_y), # Save precise float position
        "angle": player.angle,
        "seeds": seed_count,
        "shop_upgrades": shop_upgrades.copy(), # Save a copy of shop upgrades
        "remaining_checkpoints": checkpoint_count - 1, # Decrease remaining count
        "difficulty": difficulty,
        "last_ability_time": last_ability_time # Save last ability use time
    }

def load_from_checkpoint(checkpoint_data):
    """Extracts game state from a checkpoint dictionary."""
    if not checkpoint_data or not isinstance(checkpoint_data, dict):
        print("Error: Invalid checkpoint data provided.")
        return None # Return None if data is invalid

    try:
        level = checkpoint_data.get("level", 1)
        # --- FIX: Default checkpoint load position near TOP ---
        position = checkpoint_data.get("position", (SCREEN_WIDTH // 2, TRACK_TOP + 50)) # Load near top
        angle = checkpoint_data.get("angle", 270) # Default to facing down
        # --- END FIX ---
        seeds = checkpoint_data.get("seeds", 0)
        shop_upgrades = checkpoint_data.get("shop_upgrades", {})
        checkpoint_count = checkpoint_data.get("remaining_checkpoints", 0)
        difficulty = checkpoint_data.get("difficulty", "Normal")
        last_ability_time = checkpoint_data.get("last_ability_time", -1000.0) # Default if missing

        print(f"Loading from checkpoint: Lvl {level}, Seeds {seeds}, CP Left {checkpoint_count}")
        return level, position, angle, seeds, shop_upgrades, checkpoint_count, difficulty, last_ability_time
    except Exception as e:
        print(f"Error parsing checkpoint data: {e}")
        return None # Return None if parsing fails

def select_difficulty(screen):
    """Displays the difficulty selection screen and returns the chosen difficulty."""
    bg_difficulty = None
    if os.path.exists(CHOOSE_DIFFICULTY_BACKGROUND):
        try:
            bg_difficulty = pygame.image.load(CHOOSE_DIFFICULTY_BACKGROUND).convert()
            bg_difficulty = pygame.transform.scale(bg_difficulty, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading difficulty select background: {e}")

    button_width = 400 # Wider buttons
    button_height = 70
    normal_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - 120, button_width, button_height)
    hard_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 10, button_width, button_height)

    info_font = FONT_SM
    # --- CHANGE: Updated Hard difficulty text ---
    info_text_hard = "Enemies: +2 | Enemy Speed: +15%"
    info_surf_hard = info_font.render(info_text_hard, True, WHITE)
    info_rect_hard = info_surf_hard.get_rect(midtop=(hard_button.centerx, hard_button.bottom + 10)) # Position below button

    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos() # Get mouse pos for hover

        # Draw Background
        if bg_difficulty:
            screen.blit(bg_difficulty, (0, 0))
        else:
            screen.fill(BLACK) # Fallback background

        # Draw Buttons using Vault Button style and hover effect
        draw_plain_button(screen, normal_button, "Normal", BUTTON_FONT, button_image_path=VAULT_BUTTON_IMAGE, hover=normal_button.collidepoint(mouse_pos))
        draw_plain_button(screen, hard_button, "Hard", BUTTON_FONT, button_image_path=VAULT_BUTTON_IMAGE, hover=hard_button.collidepoint(mouse_pos))

        # Draw info text for Hard difficulty
        screen.blit(info_surf_hard, info_rect_hard)

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None # Allow quitting
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_click_sound()
                mx, my = pygame.mouse.get_pos()
                if normal_button.collidepoint((mx, my)): return "Normal"
                elif hard_button.collidepoint((mx, my)): return "Hard"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: play_click_sound(); return None # Allow escaping back
        clock.tick(FPS)


# --- run_level: Updated to REMOVE camera/shake and adjust drawing ---
def run_level(screen, level, current_seed_count, shop_upgrades, player_upgrades, checkpoint_count, last_ability_time,
              difficulty="Normal", start_pos=None, start_angle=None, character=1, add_achievement_func=None, current_run_total_time=0.0, current_run_total_seeds=0):
    """Runs a single level of the game."""
    global save_data
    clock = pygame.time.Clock()
    level_start_time = time.time()
    initial_seed_count_for_level = current_seed_count
    checkpoint_data = None
    # --- FIX: Define shield break invincibility time ---
    SHIELD_BREAK_INVINCIBILITY = 1.5  # Seconds of invincibility after shield breaks
    # --- END FIX ---
    # --- NEW: Flag to indicate if a shield break effect needs playing ---
    perform_shield_break_effect = False
    # --- END NEW ---


    # Player Spawn Position (Near Top)
    player_start_x = start_pos[0] if start_pos else SCREEN_WIDTH // 2
    player_start_y = start_pos[1] if start_pos else TRACK_TOP + 50
    default_angle = 270
    player_start_angle = start_angle if start_angle is not None else default_angle

    player = Player(player_start_x, player_start_y, character=character)
    # Player angle and rotation set correctly in Player.__init__ based on start_angle
    player.angle = player_start_angle # Set movement angle
    player.visual_angle = player_start_angle # Sync visual angle
    # --- FIX: Explicitly set last_ability_time loaded from checkpoint ---
    player.last_ability = last_ability_time
    # --- END FIX ---

    if "vault_upgrades" in save_data and isinstance(save_data["vault_upgrades"], dict):
        player.apply_vault_upgrades(save_data["vault_upgrades"])
        if player_upgrades.get('shield', 0) <= 0: player_upgrades['shield'] = save_data["vault_upgrades"].get("starting_shield", 0)
    else:
        print("Warning: Vault upgrades missing/invalid in run_level.")
        if "vault_upgrades" not in save_data: save_data["vault_upgrades"] = {}
        defaults = {"node_speed_boost": 0, "extra_life": 0, "seed_multiplier": 0, "seed_radius": 0, "cooldown_reduction": 0, "starting_shield": 0, "enemy_slow_aura": 0, "blessing_superseed": 0}
        for key, default_val in defaults.items(): save_data["vault_upgrades"].setdefault(key, default_val)
        player.apply_vault_upgrades(save_data["vault_upgrades"])
        if player_upgrades.get('shield', 0) <= 0: player_upgrades['shield'] = save_data["vault_upgrades"].get("starting_shield", 0)

    player.upgrades = player_upgrades.copy()
    # --- Ensure temp_shield_end_time is reset/initialized for the level ---
    player.temp_shield_end_time = 0.0
    player.invincible_until = 0.0 # Ensure invincibility is reset unless loaded from checkpoint (handled later?)
    # --- End initialization ---


    # Goal Position (Near Bottom)
    # --- FIX: Adjust Finish Line Y position to be ON the bottom border ---
    finish_line_height = 100 # Assuming FinishLine image is 100px tall
    finish_goal = FinishLine(random.randint(TRACK_LEFT + 50, TRACK_RIGHT - 50), TRACK_BOTTOM - finish_line_height // 2) # Center on bottom border
    # --- END FIX ---

    enemies = pygame.sprite.Group()
    shooter_group = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    seeds = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    ability_effects = pygame.sprite.Group()
    player.ability_effects = ability_effects
    player.particle_group_ref = particles

    # Enemy Spawning
    if level <= 15: base_count = 4 + (level - 1) * (6 / 14)
    elif level <= 80: base_count = 10 + (level - 15) * (7 / 65)
    else: base_count = 17 + (level - 80) * (3 / 19)
    base_count = min(base_count, 20)
    final_enemy_count = int(base_count) + shop_upgrades.get('seed_enemy', 0)
    if difficulty == "Hard": final_enemy_count += 2; print(f"Hard difficulty: +2 enemies (Total: {final_enemy_count})")

    world_name = get_scene_description(level)
    world_key = world_name.replace(" (Inverse Controls)","").replace(" World","").strip()
    enemy_class_name = world_key + "Enemy"
    enemy_class = globals().get(enemy_class_name, Enemy)

    world_enemy_image_map = {
        "Earth": EARTH_ENEMY_IMAGE, "Fire": FIRE_ENEMY_IMAGE, "Water": WATER_ENEMY_IMAGE, "Frost": FROST_ENEMY_IMAGE,
        "Underworld": UNDERWORLD_ENEMY_IMAGE, "Desert": DESERT_ENEMY_IMAGE, "Jungle": JUNGLE_ENEMY_IMAGE,
        "Space": SPACE_ENEMY_IMAGE, "Cyber": CYBER_ENEMY_IMAGE, "Mystic": MYSTIC_ENEMY_IMAGE, "Superseed": SUPERSEED_ENEMY_IMAGE
    }
    enemy_image_path = world_enemy_image_map.get(world_key, DEBT_IMAGE)

    enemy_positions = []
    current_shop_speed_level = shop_upgrades.get('speed', 0)
    for i in range(final_enemy_count):
        base_arbitrary_speed = (1.0 + level * 0.08)
        speed_difficulty_mult = 1.15 if difficulty == "Hard" else 1.0
        effective_arbitrary_speed = base_arbitrary_speed * speed_difficulty_mult
        if difficulty == "Hard": print(f"Hard difficulty: Enemy base speed unit: {effective_arbitrary_speed:.2f} (Multiplier: {speed_difficulty_mult})")

        attempts = 0
        while attempts < 100:
            enemy_radius_est = ORIGINAL_ENEMY_BASE_SIZE * ENEMY_CUMULATIVE_SIZE_INCREASE / 2
            ex = random.randint(int(TRACK_LEFT + enemy_radius_est + 10), int(TRACK_RIGHT - enemy_radius_est - 10))
            ey = random.randint(int(TRACK_TOP + enemy_radius_est + 10), int(TRACK_BOTTOM - enemy_radius_est - 10))
            valid = True
            if math.hypot(ex - player_start_x, ey - player_start_y) < MIN_ENEMY_SPAWN_DIST_FROM_PLAYER: valid = False
            if valid:
                for pos in enemy_positions:
                    if math.hypot(ex - pos[0], ey - pos[1]) < 40: valid = False; break
            if valid and math.hypot(ex - finish_goal.rect.centerx, ey - finish_goal.rect.centery) < finish_goal.radius + 50: valid = False
            if valid: enemy_positions.append((ex, ey)); break
            attempts += 1
        if attempts >= 100:
             enemy_radius_est = ORIGINAL_ENEMY_BASE_SIZE * ENEMY_CUMULATIVE_SIZE_INCREASE / 2
             ex = random.randint(int(TRACK_LEFT + enemy_radius_est + 10), int(TRACK_RIGHT - enemy_radius_est - 10))
             ey = random.randint(int(TRACK_TOP + enemy_radius_est + 10), int(TRACK_BOTTOM - enemy_radius_est - 10))
             print(f"Warning: Enemy spawn fallback Lvl {level}. Pos:({ex},{ey}).")
             enemy_positions.append((ex, ey))
        ex, ey = enemy_positions[-1]

        if level >= 20:
            if level < 70: david_chance = 0.1 + (level / 200)
            else: david_chance = min(0.1 + (70 / 200) + (level - 70) / 500, 0.50)
        else: david_chance = 0.0

        if random.random() < david_chance: enemy = David(ex, ey, effective_arbitrary_speed, image_path=DAVID_IMAGE, shop_speed_level=current_shop_speed_level)
        else: enemy = enemy_class(ex, ey, effective_arbitrary_speed, image_path=enemy_image_path, shop_speed_level=current_shop_speed_level)
        enemies.add(enemy)

    if level >= 15:
        enemy_list = [e for e in enemies if hasattr(e, 'homing') and not isinstance(e, David)]
        num_homing = min(len(enemy_list), 1 + level // 10)
        if num_homing > 0 and enemy_list:
            try: selected_homing = random.sample(enemy_list, num_homing); [setattr(e, 'homing', True) for e in selected_homing]
            except ValueError as e: print(f"Warning: Error selecting homing enemies: {e}")

    num_seeds = random.choices(range(2, 9), weights=[40, 25, 15, 10, 5, 4, 1], k=1)[0]
    num_seeds += shop_upgrades.get('seed_enemy', 0) * 2
    seed_radius_check = ORIGINAL_SEED_BASE_SIZE * SEED_SIZE_MULTIPLIER / 2
    seed_positions = []
    for _ in range(num_seeds):
        attempts = 0
        while attempts < 50:
             sx = random.randint(int(TRACK_LEFT + seed_radius_check + 5), int(TRACK_RIGHT - seed_radius_check - 5))
             sy = random.randint(int(TRACK_TOP + seed_radius_check + 5), int(TRACK_BOTTOM - seed_radius_check - 5))
             valid = True
             if math.hypot(sx - player_start_x, sy - player_start_y) < 100: valid = False
             if valid and math.hypot(sx - finish_goal.rect.centerx, sy - finish_goal.rect.centery) < finish_goal.radius + 30: valid = False
             if valid:
                 for pos in seed_positions:
                      if math.hypot(sx-pos[0], sy-pos[1]) < 30: valid=False; break
             if valid: seeds.add(CollectibleSeed(sx, sy)); seed_positions.append((sx, sy)); break
             attempts += 1

    weather = "clear"
    available_weather = ["clear", "rain", "wind", "snow"]
    weather_weights = [5, 2, 2, 1]
    if level >= 5: weather = random.choices(available_weather, weights=weather_weights, k=1)[0]

    # Weather particle initialization
    raindrops = []; snowflakes = []; wind_direction_persistent = None
    if weather == "rain":
        for _ in range(RAIN_DROP_COUNT): rx, ry = random.randint(TRACK_LEFT, TRACK_RIGHT), random.randint(TRACK_TOP, TRACK_BOTTOM); sp, length = random.randint(RAIN_SPEED_MIN * 60, RAIN_SPEED_MAX * 60), random.randint(RAIN_LENGTH_MIN, RAIN_LENGTH_MAX); raindrops.append([rx, ry, sp, length])
    if weather == "snow":
        for _ in range(SNOW_FLAKE_COUNT): sx, sy = random.randint(TRACK_LEFT, TRACK_RIGHT), random.randint(TRACK_TOP, TRACK_BOTTOM); sp, radius, drift = random.randint(SNOW_SPEED_MIN * 60, SNOW_SPEED_MAX * 60), random.randint(SNOW_RADIUS_MIN, SNOW_RADIUS_MAX), random.uniform(-0.5, 0.5) * 60; snowflakes.append([sx, sy, sp, radius, drift])
    if weather == "wind": wind_direction_persistent = random.choice([-1, 1])

    if level >= 10:
        num_shooters = max(1, level // 10)
        shooter_y_spacing = (TRACK_BOTTOM - TRACK_TOP - 200) / (num_shooters + 1) if num_shooters > 0 else 0
        shooter_positions = []
        for i in range(num_shooters):
             attempts = 0
             while attempts < 20:
                  shooter_radius_est = ORIGINAL_SHOOTER_BASE_WIDTH * SHOOTER_SIZE_MULTIPLIER / 2
                  sx = random.choice([TRACK_LEFT + shooter_radius_est + 10, TRACK_RIGHT - shooter_radius_est - 10]);
                  sy = TRACK_TOP + 100 + (i + 1) * shooter_y_spacing;
                  sy = max(TRACK_TOP + shooter_radius_est + 10, min(sy, TRACK_BOTTOM - shooter_radius_est - 10))
                  valid = True
                  for pos in shooter_positions:
                      if math.hypot(sx-pos[0], sy-pos[1]) < 50: valid=False; break
                  if valid: shooter_group.add(ShooterEnemy(sx, sy)); shooter_positions.append((sx,sy)); break
                  attempts += 1

    powerup_spawn_timer = 0.0
    powerup_interval = random.uniform(4.0, 8.0)

    bg_texture = None
    world_bg_path = WORLD_BACKGROUNDS.get(world_name)
    if world_bg_path and os.path.exists(world_bg_path):
        try: bg_texture = pygame.image.load(world_bg_path).convert(); bg_texture = pygame.transform.scale(bg_texture, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e: print(f"Error loading background {world_bg_path}: {e}")

    achievement_banners = []
    unlocked_achievements_this_session = set()
    checkpoint_saved_this_level = False
    checkpoint_feedback_time = 0.0
    freeze_end_time = 0.0
    magnet_active_until = 0.0
    double_seed_end_time = 0.0
    # temp_shield_end_time initialized in Player object
    level_screen_flash_timer = 0.0 # Renamed from screen_flash_timer
    level_screen_flash_color = WHITE # Renamed from screen_flash_color

    if add_achievement_func:
        planet_ach_name = world_key + " Seeded"
        add_achievement_func(planet_ach_name, achievement_banners, unlocked_achievements_this_session)

    if level == 91:
        warning = FONT_MD.render("Mystic World Incoming!", True, WHITE); sub = FONT_SM.render("Levels 91-94: Inverse Controls Active!", True, RED)
        screen.fill(BLACK); screen.blit(warning, warning.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))); screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))); pygame.display.flip(); pygame.time.wait(4000)

    # --- Main Level Loop ---
    running = True; paused = False; shop_is_open = False; help_is_open = False
    level_outcome = None; inverse_controls = (world_name == "Mystic World (Inverse Controls)")
    level_duration = 0.0; mixer_ok = pygame.mixer.get_init(); music_was_playing = False

    # --- Pre-calculate UI element dimensions ---
    attr_width = CHECKPOINT_RECT.width + SHOP_BUTTON_RECT.width + CP_BUTTON_RIGHT_MARGIN
    attr_height = 80 # <<< Increased height to accommodate vault info
    world_weather_max_height = 80
    timer_font = FONT_SM
    max_timer_text = "Double Seeds: 0.0s"
    timer_max_width = timer_font.size(max_timer_text)[0] + 20
    timer_max_height = timer_font.get_height() + 10

    while running:
        dt = clock.tick_busy_loop(FPS) / 1000.0
        dt = min(dt, 0.05)
        current_time_sec = time.time()
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        can_use_checkpoint_now = checkpoint_count > 0 and not checkpoint_saved_this_level

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: level_outcome = "exit"; running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if not shop_is_open and not help_is_open:
                        paused = not paused; play_click_sound()
                        if paused: music_was_playing = mixer_ok and pygame.mixer.music.get_busy(); (pygame.mixer.music.pause() if music_was_playing else None)
                        elif music_was_playing: (pygame.mixer.music.unpause() if mixer_ok else None)
                elif event.key == pygame.K_ESCAPE: level_outcome = "exit"; running = False
                elif event.key == pygame.K_c:
                    if can_use_checkpoint_now and not paused and not shop_is_open and not help_is_open:
                        play_click_sound(); checkpoint_data = save_checkpoint(player, current_seed_count, shop_upgrades, level, checkpoint_count, difficulty, player.last_ability)
                        checkpoint_count -= 1; checkpoint_feedback_time = time.time(); checkpoint_saved_this_level = True; print(f"Checkpoint saved Lvl {level} (via key). Uses left: {checkpoint_count}"); can_use_checkpoint_now = False
                elif event.key == pygame.K_k: # Key to open/close help overlay
                     if not paused and not shop_is_open:
                         play_click_sound(); help_is_open = not help_is_open
                         if help_is_open: music_was_playing = mixer_ok and pygame.mixer.music.get_busy(); (pygame.mixer.music.pause() if music_was_playing else None)
                         elif music_was_playing: (pygame.mixer.music.unpause() if mixer_ok else None)


            if not paused and not help_is_open and event.type == pygame.MOUSEBUTTONDOWN:
                 if SHOP_BUTTON_RECT.collidepoint(event.pos) and not shop_is_open:
                      play_click_sound(); shop_is_open = True; music_was_playing = mixer_ok and pygame.mixer.music.get_busy(); (pygame.mixer.music.pause() if music_was_playing else None)
                 elif CHECKPOINT_RECT.collidepoint(event.pos) and can_use_checkpoint_now and not shop_is_open:
                      play_click_sound(); checkpoint_data = save_checkpoint(player, current_seed_count, shop_upgrades, level, checkpoint_count, difficulty, player.last_ability)
                      checkpoint_count -= 1; checkpoint_feedback_time = time.time(); checkpoint_saved_this_level = True; print(f"Checkpoint saved Lvl {level} (via click). Uses left: {checkpoint_count}"); can_use_checkpoint_now = False
                 elif HELP_BUTTON_RECT.collidepoint(event.pos) and not shop_is_open:
                      play_click_sound(); help_is_open = True; music_was_playing = mixer_ok and pygame.mixer.music.get_busy(); (pygame.mixer.music.pause() if music_was_playing else None)


        # --- Pause State ---
        if paused:
            # --- FIX: Draw static scene during pause (No Offset) ---
            if bg_texture: screen.blit(bg_texture, (0, 0))
            else: screen.fill(get_scene_color(level)) # Use ui.get_scene_color
            # Draw world elements at absolute rect positions
            screen.blit(finish_goal.image, finish_goal.rect) # Draw finish line during pause
            for s in seeds: screen.blit(s.image, s.rect)
            for e in enemies: screen.blit(e.image, e.rect)
            for sh in shooter_group: screen.blit(sh.image, sh.rect)
            for p in projectiles: screen.blit(p.image, p.rect)
            for pw in powerups: screen.blit(pw.image, pw.rect)
            for ae in ability_effects: screen.blit(ae.image, ae.rect)
            player_draw_rect = player.get_draw_rect()
            screen.blit(player.image, player_draw_rect)
            # --- END FIX ---
            dim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 100)); screen.blit(dim_surface, (0, 0))
            pause_result = pause_menu(screen)
            if pause_result == "resume": paused = False; (pygame.mixer.music.unpause() if music_was_playing and mixer_ok else None)
            elif pause_result == "menu": level_outcome = "menu"; running = False
            continue

        # --- Help Overlay State ---
        if help_is_open:
            show_controls_overlay(screen); help_is_open = False # Function now handles its own loop
            (pygame.mixer.music.unpause() if music_was_playing and mixer_ok else None)
            pygame.event.clear(pygame.MOUSEBUTTONDOWN) # Clear clicks made while overlay was open
            continue

        # --- Shop State ---
        if shop_is_open:
            shop_status, current_seed_count, checkpoint_count, shop_upgrades, player_upgrades = show_ingame_shop_overlay(screen, current_seed_count, level, shop_upgrades, player_upgrades, checkpoint_count)
            player.upgrades = player_upgrades
            if shop_status == "close":
                shop_is_open = False; (pygame.mixer.music.unpause() if music_was_playing and mixer_ok else None)
                current_shop_speed_level = shop_upgrades.get('speed', 0)
                for enemy in enemies:
                    base_speed_boost = 1.0 + (current_shop_speed_level * SHOP_SPEED_ENEMY_BOOST_FACTOR)
                    enemy.speed_pps = enemy.base_speed_pps * ENEMY_SPEED_MULTIPLIER * base_speed_boost
                    current_vel_magnitude = math.hypot(enemy.vel_x, enemy.vel_y)
                    if current_vel_magnitude > 0.01:
                        scale_factor = enemy.speed_pps / current_vel_magnitude
                        enemy.vel_x *= scale_factor; enemy.vel_y *= scale_factor
                    else:
                         angle = random.uniform(0, 2 * math.pi)
                         enemy.vel_x = enemy.speed_pps * math.cos(angle); enemy.vel_y = enemy.speed_pps * math.sin(angle)
                print("Updated enemy speeds after shop close.")
            elif shop_status == "exit": level_outcome = "exit"; running = False
            pygame.display.flip(); continue

        # --- Game Updates ---
        player.update(keys, current_time_sec, weather, shop_upgrades, inverse_controls, wind_direction_persistent, player_ref=player, dt=dt)
        finish_goal.update(dt=dt)

        freeze_active = current_time_sec < freeze_end_time
        magnet_active = current_time_sec < magnet_active_until
        double_seed_active = current_time_sec < double_seed_end_time
        # temp_shield_active check moved to collision logic

        # --- FIX: Mesky slow logic ---
        effective_speed_modifier_for_updates = 1.0
        if freeze_active:
             effective_speed_modifier_for_updates = 0.0 # Freeze overrides Mesky
        elif player.character == 3 and player.ability_active:
             effective_speed_modifier_for_updates = 0.5 # Mesky ability is 50% slow
        # --- END FIX ---

        shop_slow_factor = 1.0 - (shop_upgrades.get('enemy_slow', 0) * 0.05)
        final_shop_mesky_modifier = effective_speed_modifier_for_updates * shop_slow_factor

        aura_level = save_data["vault_upgrades"].get("enemy_slow_aura", 0)
        aura_slow_factor = 1.0 - (0.07 * aura_level) if aura_level > 0 else 1.0
        aura_radius_sq = (40 + aura_level * 10) ** 2 if aura_level > 0 else -1

        all_enemies = enemies.sprites()
        for i, enemy in enumerate(all_enemies):
            final_modifier = final_shop_mesky_modifier
            if aura_radius_sq > 0 and hasattr(enemy, 'pos_x') and hasattr(enemy, 'pos_y'):
                 dx_aura, dy_aura = player.pos_x - enemy.pos_x, player.pos_y - enemy.pos_y
                 if dx_aura*dx_aura + dy_aura*dy_aura <= aura_radius_sq: final_modifier *= aura_slow_factor
            other_enemies_for_collision = all_enemies[i+1:]
            player_arg_for_update = player if isinstance(enemy, David) or getattr(enemy, 'homing', False) else None
            enemy.update(player_arg_for_update, speed_modifier=final_modifier, dt=dt, other_enemies=other_enemies_for_collision)

        shooter_player_arg = player if not freeze_active else None
        shooter_group.update(current_time_sec, projectiles, shooter_player_arg)
        projectiles.update(dt=dt, speed_modifier=(0.0 if freeze_active else 1.0))
        particles.update(dt=dt)
        powerups.update(dt=dt)
        ability_effects.update(dt, player) # Pass player ref to ability effect update

        player_base_pickup_radius = player.radius + player.vault_pickup_radius_bonus
        current_pickup_radius = player_base_pickup_radius
        if magnet_active:
            current_pickup_radius *= MAGNET_PICKUP_RADIUS_MULTIPLIER
            magnet_pull_speed = 250; magnet_radius_sq = current_pickup_radius**2
            for seed in seeds:
                dx = player.pos_x - seed.pos_x
                dy = player.pos_y - seed.pos_y
                dist_sq = dx*dx + dy*dy
                if dist_sq < magnet_radius_sq and dist_sq > (player.radius * 0.5)**2:
                    dist = math.sqrt(dist_sq)
                    pull_nx = dx / dist; pull_ny = dy / dist
                    pull_vx = pull_nx * magnet_pull_speed * dt
                    pull_vy = pull_ny * magnet_pull_speed * dt
                    seed.pos_x += pull_vx; seed.pos_y += pull_vy
        seeds.update() # Sync rect with pos

        powerup_spawn_timer += dt
        if powerup_spawn_timer >= powerup_interval:
            powerup_spawn_timer -= powerup_interval
            powerup_chance = POWERUP_CHANCE_BLESSING if save_data["vault_upgrades"].get("blessing_superseed", 0) >= 1 else POWERUP_CHANCE_BASE
            if random.random() < powerup_chance:
                 attempts = 0
                 while attempts < 20:
                      pu_radius_est = ORIGINAL_POWERUP_BASE_SIZE * POWERUP_CUMULATIVE_SIZE_INCREASE / 2
                      fx = random.randint(int(TRACK_LEFT+pu_radius_est+10), int(TRACK_RIGHT-pu_radius_est-10));
                      fy = random.randint(int(TRACK_TOP+pu_radius_est+10), int(TRACK_BOTTOM-pu_radius_est-10));
                      if math.hypot(fx - player.pos_x, fy - player.pos_y) > 100:
                           pu_types = list(POWERUP_WEIGHTS.keys()); pu_weights = list(POWERUP_WEIGHTS.values())
                           pu_type = random.choices(pu_types, weights=pu_weights, k=1)[0]
                           if pu_type == "freeze": powerups.add(FreezePowerUp(fx, fy))
                           elif pu_type == "magnet": powerups.add(MagnetPowerUp(fx, fy))
                           elif pu_type == "shield": powerups.add(ShieldPowerUp(fx, fy))
                           elif pu_type == "double": powerups.add(DoubleSeedPowerUp(fx, fy))
                           break
                      attempts += 1
            powerup_interval = random.uniform(4.0, 8.0)

        # --- Shield / Collision Logic ---
        is_invincible_now = current_time_sec < player.invincible_until
        has_permanent_shield = player.upgrades.get("shield", 0) > 0
        is_temp_shield_powerup_active = current_time_sec < player.temp_shield_end_time

        # Check collisions only if not currently invincible
        if not is_invincible_now:
            # Check Enemy Collision
            # --- FIX: Add radius check and use circle_collision ---
            collided_enemy = pygame.sprite.spritecollideany(player, enemies, circle_collision)
            # --- END FIX ---
            if collided_enemy:
                # --- Shield break/death logic remains the same ---
                if is_temp_shield_powerup_active:
                    print("Temp Shield Powerup BROKEN by Enemy")
                    player.temp_shield_end_time = 0.0
                    player.invincible_until = current_time_sec + SHIELD_BREAK_INVINCIBILITY
                    perform_shield_break_effect = True
                    level_screen_flash_timer = 0.1;
                    level_screen_flash_color = BLUE
                    is_invincible_now = True  # Update invincibility status immediately
                elif has_permanent_shield:
                    print("Permanent Shield BROKEN by Enemy")
                    player.upgrades["shield"] = 0
                    player.invincible_until = current_time_sec + SHIELD_BREAK_INVINCIBILITY
                    perform_shield_break_effect = True
                    level_screen_flash_timer = 0.1;
                    level_screen_flash_color = BLUE
                    is_invincible_now = True  # Update invincibility status immediately
                else:
                    print("Player hit enemy - NO SHIELD")
                    level_outcome = "lose"
                    running = False
                    level_screen_flash_timer = 0.1;
                    level_screen_flash_color = RED
                    # Play dead sound immediately on death determination
                    if os.path.exists(DEAD_SOUND) and mixer_ok:
                        try:
                            pygame.mixer.Sound(DEAD_SOUND).play()
                        except pygame.error as e:
                            print(f"Dead sound error on enemy collision: {e}")

            # Check Projectile Collision (only if still running and not yet invincible from enemy hit)
            if running and not is_invincible_now:
                # --- FIX: Use circle_collision for Projectiles ---
                collided_proj = pygame.sprite.spritecollideany(player, projectiles, circle_collision)
                # --- END FIX ---
                if collided_proj:
                    collided_proj.kill()  # Remove projectile regardless of shield outcome
                    # --- Shield break/death logic remains the same ---
                    if is_temp_shield_powerup_active:
                        print("Temp Shield Powerup BROKEN by Projectile")
                        player.temp_shield_end_time = 0.0
                        player.invincible_until = current_time_sec + SHIELD_BREAK_INVINCIBILITY
                        perform_shield_break_effect = True
                        level_screen_flash_timer = 0.1;
                        level_screen_flash_color = BLUE
                        is_invincible_now = True  # Update invincibility status immediately
                    elif has_permanent_shield:
                        print("Permanent Shield BROKEN by Projectile")
                        player.upgrades["shield"] = 0
                        player.invincible_until = current_time_sec + SHIELD_BREAK_INVINCIBILITY
                        perform_shield_break_effect = True
                        level_screen_flash_timer = 0.1;
                        level_screen_flash_color = BLUE
                        is_invincible_now = True  # Update invincibility status immediately
                    else:
                        print("Player hit projectile - NO SHIELD")
                        level_outcome = "lose"
                        running = False
                        level_screen_flash_timer = 0.1;
                        level_screen_flash_color = RED
                        # Play dead sound immediately on death determination
                        if os.path.exists(DEAD_SOUND) and mixer_ok:
                            try:
                                pygame.mixer.Sound(DEAD_SOUND).play()
                            except pygame.error as e:
                                print(f"Dead sound error on projectile collision: {e}")
        # --- End Collision Check ---

        # Trigger shield break visual/sound effect if the flag was set
        if perform_shield_break_effect:
            create_shield_break_particles(player.rect.center, particles)
            if os.path.exists(BREAK_SHIELD_SOUND) and mixer_ok:
                try: pygame.mixer.Sound(BREAK_SHIELD_SOUND).play()
                except pygame.error as e: print(f"Shield break sound error: {e}")
            perform_shield_break_effect = False # Reset flag

        # Handle game over logic immediately after potential collision outcome
        if level_outcome == "lose":
            if not checkpoint_data:
                print("Game Over.")
                final_run_time = current_run_total_time + (time.time() - level_start_time)
                final_run_seeds = current_run_total_seeds + (current_seed_count - initial_seed_count_for_level)
                game_over_name = show_game_over(screen, level, final_run_time, final_run_seeds)
                save_score(game_over_name, level, final_run_time, final_run_seeds);
            running = False # Stop the level loop
            continue # Skip the rest of the loop for this frame

        # Seed Collection
        seeds_collided = pygame.sprite.spritecollide(player, seeds, True, collide_circle_precise_seed)
        if seeds_collided:
             vault_multiplier = 2 if save_data["vault_upgrades"].get("seed_multiplier", 0) >= 1 else 1
             powerup_multiplier = 2 if double_seed_active else 1
             final_multiplier = vault_multiplier * powerup_multiplier
             seeds_gained = len(seeds_collided) * final_multiplier
             current_seed_count += seeds_gained;
             save_data["total_seeds_accumulated"] = save_data.get("total_seeds_accumulated", 0) + seeds_gained
             for seed_sprite in seeds_collided:
                  particle_count = 5 * powerup_multiplier
                  for _ in range(particle_count): particles.add(Particle(seed_sprite.rect.center))
             if os.path.exists(COLLECT_SOUND) and mixer_ok:
                  try: pygame.mixer.Sound(COLLECT_SOUND).play()
                  except pygame.error as e: print(f"Collect sound error: {e}")

        # Powerup Collection
        powerups_collided = pygame.sprite.spritecollide(player, powerups, True, circle_collision)
        for pu in powerups_collided:
            pu_type = getattr(pu, 'powerup_type', 'unknown')
            if pu_type == "freeze": play_freeze_sound(); freeze_end_time = current_time_sec + FREEZE_DURATION
            elif pu_type == "magnet":
                if os.path.exists(MAGNET_SOUND) and mixer_ok:
                    try: pygame.mixer.Sound(MAGNET_SOUND).play()
                    except pygame.error as e: print(f"Magnet sound error: {e}")
                magnet_active_until = current_time_sec + MAGNET_DURATION
                save_data["total_magnets_collected"] = save_data.get("total_magnets_collected", 0) + 1
                if add_achievement_func:
                    total_magnets_ever = save_data["total_magnets_collected"]
                    if total_magnets_ever >= 100: add_achievement_func(ACH_MAINNET_MAGNET, achievement_banners, unlocked_achievements_this_session)
                    elif total_magnets_ever >= 75: add_achievement_func(ACH_SEED_SINGULARITY, achievement_banners, unlocked_achievements_this_session)
                    elif total_magnets_ever >= 50: add_achievement_func(ACH_GRAVITY_WELL, achievement_banners, unlocked_achievements_this_session)
                    elif total_magnets_ever >= 25: add_achievement_func(ACH_ATTRACTOR_NODE, achievement_banners, unlocked_achievements_this_session)
            elif pu_type == "shield":
                # Re-check shield status *at the moment of pickup*
                has_permanent_shield_local = player.upgrades.get("shield", 0) > 0
                is_temp_shield_powerup_active_local = current_time_sec < player.temp_shield_end_time
                is_chosen_invincible_local = (player.character == 4 and player.ability_active) or (
                            current_time_sec < player.invincible_until)

                # Only activate if no other shield/invincibility is present
                if not has_permanent_shield_local and not is_temp_shield_powerup_active_local and not is_chosen_invincible_local:
                    player.temp_shield_end_time = current_time_sec + SHIELD_POWERUP_DURATION
                    print(f"Temporary shield powerup activated until {player.temp_shield_end_time:.1f}")
                    if os.path.exists(POWERUP_SHIELD_SOUND) and mixer_ok:
                        try:
                            pygame.mixer.Sound(POWERUP_SHIELD_SOUND).play()
                        except pygame.error as e:
                            print(f"Shield powerup sound error: {e}")
                else:
                    print("Shield powerup collected, but another shield/invincibility is already active.")
            elif pu_type == "double":
                 double_seed_end_time = current_time_sec + DOUBLE_SEED_DURATION
                 print(f"Double seeds active until {double_seed_end_time:.1f}")
                 if os.path.exists(POWERUP_DOUBLE_SOUND) and mixer_ok:
                     try: pygame.mixer.Sound(POWERUP_DOUBLE_SOUND).play()
                     except pygame.error as e: print(f"Double seed powerup sound error: {e}")

        # Finish Line Collision
        if running and circle_collision(player, finish_goal):
             level_outcome = "win"; running = False
             level_time_taken = time.time() - level_start_time
             if add_achievement_func:
                 add_achievement_func(ACH_SPROUTED, achievement_banners, unlocked_achievements_this_session)
                 if level_time_taken < 2.0: add_achievement_func(ACH_WARP_SPEED_ENGAGED, achievement_banners, unlocked_achievements_this_session)
                 if inverse_controls: add_achievement_func(ACH_NAVIGATING_THE_NOISE, achievement_banners, unlocked_achievements_this_session)
                 if current_seed_count >= 100: add_achievement_func(ACH_DIAMOND_HANDS, achievement_banners, unlocked_achievements_this_session)
                 if level >= 20 and player.last_ability < level_start_time: add_achievement_func(ACH_PACIFIST_RUN, achievement_banners, unlocked_achievements_this_session)


        render_offset_x = 0 # No offset
        render_offset_y = 0 # No offset

        # --- Drawing (Static View) ---
        if bg_texture: screen.blit(bg_texture, (0, 0)) # Draw background at 0,0
        else: screen.fill(get_scene_color(level)) # Use ui.get_scene_color

        # --- Draw game world elements (Order Matters!) ---
        for s in seeds: screen.blit(s.image, s.rect)
        for e in enemies: screen.blit(e.image, e.rect)
        for sh in shooter_group: screen.blit(sh.image, sh.rect)
        for pu in powerups: screen.blit(pu.image, pu.rect)
        for proj in projectiles:
             screen.blit(proj.image, proj.rect) # Draw projectile
             # Draw projectile trail (absolute coords)
             trail_length_proj = 15
             if abs(proj.vel_x) > 0.1 or abs(proj.vel_y) > 0.1:
                vel_mag_proj = math.hypot(proj.vel_x, proj.vel_y)
                if vel_mag_proj > 0:
                    start_x_p = proj.rect.centerx - proj.vel_x * (trail_length_proj / vel_mag_proj)
                    start_y_p = proj.rect.centery - proj.vel_y * (trail_length_proj / vel_mag_proj)
                    try: pygame.draw.line(screen, proj.color, (int(start_x_p), int(start_y_p)), proj.rect.center, 2)
                    except TypeError: pass
        for p in particles: screen.blit(p.image, p.rect)

        # Player Trail Drawing (Absolute coords)
        player_trail_color = PLAYER_TRAIL_COLORS.get(player.character, TRAIL_COLOR_DEFAULT)
        trail_alpha_mult = player.trail_intensity_multiplier
        for i, pos in enumerate(player.trail):
            alpha = int(255 * (i / player.trail_length) * 0.5 * trail_alpha_mult)
            alpha = max(0, min(255, alpha))
            trail_surf = pygame.Surface((player.trail_segment_size, player.trail_segment_size), pygame.SRCALPHA)
            draw_color = (*player_trail_color, alpha)
            pygame.draw.circle(trail_surf, draw_color, (player.trail_segment_size // 2, player.trail_segment_size // 2), player.trail_segment_size // 2)
            draw_pos_x = pos[0] - player.trail_segment_size // 2
            draw_pos_y = pos[1] - player.trail_segment_size // 2
            screen.blit(trail_surf, (draw_pos_x, draw_pos_y))

        # Draw player (Absolute coords using get_draw_rect)
        player_draw_rect = player.get_draw_rect()
        screen.blit(player.image, player_draw_rect)

        # Draw Auras (Absolute coords)
        # Player position doesn't need temporary adjustment anymore
        draw_shield_aura(screen, player, current_time_sec) # This handles Chosen/Temp/Mesky/Permanent shield visuals
        aura_level_v = save_data["vault_upgrades"].get("enemy_slow_aura", 0)
        if aura_level_v > 0:
             aura_radius_v = 40 + aura_level_v * 10; aura_alpha_v = 60 + aura_level_v * 20
             aura_surf_v = pygame.Surface((aura_radius_v*2, aura_radius_v*2), pygame.SRCALPHA)
             pygame.draw.circle(aura_surf_v, (0, 150, 255, aura_alpha_v), (aura_radius_v, aura_radius_v), aura_radius_v, 2)
             screen.blit(aura_surf_v, (int(player.pos_x - aura_radius_v), int(player.pos_y - aura_radius_v)))

        # Draw Ability Effects (Absolute coords)
        for effect in ability_effects: screen.blit(effect.image, effect.rect)

        # Weather Effects Rendering (Absolute coords)
        if weather == "rain":
            for drop in raindrops:
                drop[1] += drop[2] * dt
                if drop[1] > TRACK_BOTTOM: drop[1] = TRACK_TOP - random.randint(5, 20); drop[0] = random.randint(TRACK_LEFT, TRACK_RIGHT)
                pygame.draw.line(screen, RAIN_COLOR, (drop[0], drop[1]), (drop[0], drop[1] + drop[3]), 1)
        elif weather == "snow":
            for flake in snowflakes:
                flake[0] += flake[4] * dt; flake[1] += flake[2] * dt
                if flake[1] > TRACK_BOTTOM: flake[1] = TRACK_TOP - random.randint(5, 10); flake[0] = random.randint(TRACK_LEFT, TRACK_RIGHT)
                pygame.draw.circle(screen, SNOW_COLOR, (int(flake[0]), int(flake[1])), flake[3])
        elif weather == "wind":
            for _ in range(WIND_STREAK_COUNT):
                start_x = random.randint(TRACK_LEFT, TRACK_RIGHT); start_y = random.randint(TRACK_TOP, TRACK_BOTTOM)
                wind_mag = WIND_STREAK_LENGTH * wind_direction_persistent
                end_x = start_x + wind_mag; end_y = start_y
                pygame.draw.line(screen, WIND_COLOR, (start_x, start_y), (end_x, end_y), 1)

        # --- FIX: Draw Finish Line AFTER game objects but BEFORE border/UI ---
        screen.blit(finish_goal.image, finish_goal.rect)
        # --- END FIX ---

        # --- FIX: Draw screen flash using renamed variable ---
        if level_screen_flash_timer > 0:
            level_screen_flash_timer -= dt
            flash_alpha = int(180 * max(0, level_screen_flash_timer / 0.1)) # Base flash duration 0.1s
            flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA);
            flash_surf.fill((*level_screen_flash_color[:3], flash_alpha))
            screen.blit(flash_surf, (0,0))
        # --- END FIX ---

        # --- UI Elements (Draw without shake offset) ---
        # --- FIX: Draw border AFTER finish line ---
        draw_game_border(screen) # Border drawn directly
        # --- END FIX ---

        # Level/Seed text
        level_text = LEVEL_TEXT_FONT.render(f"Level {level} | Seeds: {current_seed_count}", True, WHITE)
        screen.blit(level_text, (TRACK_LEFT + 10, TRACK_TOP + 10))

        # World/Weather info
        world_weather_surf = pygame.Surface((400, world_weather_max_height), pygame.SRCALPHA)
        world_weather_surf.fill((0,0,0,0))
        drawn_height = draw_current_world_and_weather(world_weather_surf, world_name, weather)
        base_world_weather_pos = (TRACK_LEFT + 10, TRACK_TOP + LEVEL_TEXT_FONT.get_height() + 15)
        screen.blit(world_weather_surf, base_world_weather_pos, (0, 0, 400, drawn_height))
        weather_bottom_y_base = base_world_weather_pos[1] + drawn_height

        # Double Seed Timer
        if double_seed_active:
             time_left_double = max(0, double_seed_end_time - current_time_sec)
             timer_surf = pygame.Surface((timer_max_width, timer_max_height), pygame.SRCALPHA)
             timer_surf.fill((0,0,0,0))
             draw_seed_doubler_timer(timer_surf, time_left_double) # Call the draw function
             timer_y_base = weather_bottom_y_base + 5
             base_timer_pos = (TRACK_LEFT + 10, timer_y_base)
             screen.blit(timer_surf, base_timer_pos)

        # Ability Icon
        draw_ability_icon(screen, player, current_time_sec)

        # Attributes
        attr_rect_base = pygame.Rect(CHECKPOINT_RECT.left, HELP_BUTTON_RECT.bottom + 10, attr_width, attr_height)
        attr_surf = pygame.Surface(attr_rect_base.size, pygame.SRCALPHA)
        draw_attributes(attr_surf, shop_upgrades, player_upgrades, save_data) # <<< Pass save_data
        screen.blit(attr_surf, attr_rect_base.topleft) # Blit at base position

        # Buttons
        cp_surf = pygame.Surface(CHECKPOINT_RECT.size, pygame.SRCALPHA)
        cp_surf.fill((0,0,0,0))
        draw_checkpoint_button(cp_surf, checkpoint_count, can_use_checkpoint_now, checkpoint_feedback_time, save_data)
        screen.blit(cp_surf, CHECKPOINT_RECT.topleft) # Blit at base position
        # Draw checkpoint feedback text separately
        if checkpoint_feedback_time and time.time() - checkpoint_feedback_time < 1.0:
            fb_cp_surf = CP_FONT.render("Saved!", True, GREEN)
            fb_cp_rect_base = fb_cp_surf.get_rect(midtop=(CHECKPOINT_RECT.centerx, CHECKPOINT_RECT.bottom + 5))
            screen.blit(fb_cp_surf, fb_cp_rect_base)
        elif can_use_checkpoint_now:
             press_c_font_cp = FONT_TINY
             press_c_surf_cp = press_c_font_cp.render("(Press C)", True, WHITE)
             press_c_rect_base_cp = press_c_surf_cp.get_rect(midtop=(CHECKPOINT_RECT.centerx, CHECKPOINT_RECT.bottom + 3))
             press_c_bg_rect_cp = press_c_rect_base_cp.inflate(6, 2)
             press_c_bg_surf_cp = pygame.Surface(press_c_bg_rect_cp.size, pygame.SRCALPHA)
             press_c_bg_surf_cp.fill((0, 0, 0, 100))
             screen.blit(press_c_bg_surf_cp, press_c_bg_rect_cp.topleft)
             screen.blit(press_c_surf_cp, press_c_rect_base_cp)

        shop_surf = pygame.Surface(SHOP_BUTTON_RECT.size, pygame.SRCALPHA)
        shop_surf.fill((0,0,0,0))
        draw_shop_button(shop_surf)
        screen.blit(shop_surf, SHOP_BUTTON_RECT.topleft) # Blit at base position

        help_surf = pygame.Surface(HELP_BUTTON_RECT.size, pygame.SRCALPHA)
        help_surf.fill((0,0,0,0))
        draw_help_button(help_surf)
        screen.blit(help_surf, HELP_BUTTON_RECT.topleft) # Blit at base position

        # Pause Text
        pause_font = FONT_IMPACT_XSM; pause_info_surf = pause_font.render("P: Pause | K: Help", True, WHITE); # Added Help key hint
        pause_info_rect_base = pause_info_surf.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 10)
        screen.blit(pause_info_surf, pause_info_rect_base)

        # Freeze Timer
        if freeze_active:
             freeze_timer_text = FONT_MD.render(f"Freeze: {freeze_end_time - current_time_sec:.1f}s", True, CYAN)
             freeze_rect_base = freeze_timer_text.get_rect(centerx=SCREEN_WIDTH // 2, top=60);
             screen.blit(freeze_timer_text, freeze_rect_base)

        # --- FIX: Achievement Banner Drawing Logic ---
        active_banners = []
        banner_y_start = 60 # Start higher up
        banner_spacing = 10 # Keep spacing
        max_banners_at_once = 3
        banner_draw_count = 0

        for i, banner in enumerate(achievement_banners):
            elapsed = current_time_sec - banner["time"]
            if elapsed < ACHIEVEMENT_BANNER_DURATION:
                active_banners.append(banner) # Keep banner if still active
                if banner_draw_count < max_banners_at_once:
                    target_y = banner_y_start + banner_draw_count * (FONT_MD.get_height() + banner_spacing)
                    slide_speed = 300
                    fade_time = 0.5

                    # Smooth sliding animation
                    if elapsed < fade_time: # Slide in
                        banner["y"] = min(target_y, banner["y"] + slide_speed * dt)
                    elif elapsed > ACHIEVEMENT_BANNER_DURATION - fade_time: # Slide out
                        banner["y"] = max(-60, banner["y"] - slide_speed * dt)
                    else: # Hold position
                        banner["y"] = target_y

                    final_banner_x_base = SCREEN_WIDTH // 2 # Center X
                    final_banner_y_base = banner["y"] # Use the calculated sliding Y

                    # Only draw if on screen
                    if final_banner_y_base > -50:
                         # Calculate alpha for fade in/out
                         alpha = 255
                         if elapsed < fade_time:
                             alpha = int(255 * (elapsed / fade_time))
                         elif elapsed > ACHIEVEMENT_BANNER_DURATION - fade_time:
                             alpha = int(255 * (1 - (elapsed - (ACHIEVEMENT_BANNER_DURATION - fade_time)) / fade_time))
                         alpha = max(0, min(255, alpha))

                         banner_surf = FONT_MD.render(banner["text"], True, banner["tier_color"])
                         banner_surf.set_alpha(alpha) # Apply fade alpha
                         banner_rect = banner_surf.get_rect(centerx=final_banner_x_base, top=int(final_banner_y_base))

                         bg_rect = banner_rect.inflate(20, 10);
                         bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA);
                         bg_surf.fill((0, 0, 0, int(180 * (alpha / 255)))) # Scale bg alpha
                         screen.blit(bg_surf, bg_rect.topleft);
                         screen.blit(banner_surf, banner_rect)
                         banner_draw_count += 1
            # else: Banner has expired, don't add to active_banners

        achievement_banners = active_banners # Update list with only active banners
        # --- END FIX ---
        # --- END UI Elements ---

        pygame.mouse.set_visible(True)
        pygame.display.flip()


    # --- Level End ---
    level_end_time = time.time()
    level_duration = level_end_time - level_start_time
    seeds_collected_this_level = current_seed_count - initial_seed_count_for_level
    save_data["total_time_played"] = save_data.get("total_time_played", 0.0) + level_duration
    save_data["highest_level_reached"] = max(save_data.get("highest_level_reached", 0), level)

    save_save_data(save_data)
    print(f"Level {level} ended: {level_outcome}, Duration: {level_duration:.2f}s, Seeds collected: {seeds_collected_this_level}")

    minigame_occurred = False
    # --- FIX: Handle minigame results and death ---
    if level_outcome == "win" and level < MAX_LEVEL and random.random() < 0.05:
         minigame_occurred = True
         minigames = [ ("Seed Harvest Frenzy", minigame_1, "Seeds Collected"), ("David’s Revenge", minigame_2, "1 SUPR"), ("Inverse Gauntlet", minigame_3, "2 SUPR") ]
         minigame_name, minigame_func, rewards = random.choice(minigames)
         announce_mini_game(screen, minigame_name, rewards)
         minigame_result = minigame_func(screen, selected_character=character)

         if isinstance(minigame_result, tuple): # Seed Harvest (minigame_1)
             success, extra_seeds = minigame_result
             if success is True:
                 current_seed_count += extra_seeds
                 save_data["total_seeds_accumulated"] = save_data.get("total_seeds_accumulated", 0) + extra_seeds
                 if add_achievement_func: add_achievement_func(ACH_SEED_HARVEST_VICTOR, None, unlocked_achievements_this_session_main)
                 save_save_data(save_data)
             elif success == "menu": level_outcome = "menu" # Quit to main menu
             else: print(f"{minigame_name} failed or exited (loss).") # Treat False as loss (no reward)

         elif isinstance(minigame_result, bool): # David's Revenge (minigame_2) or Inverse Gauntlet (minigame_3)
             if minigame_result is True: # Player won the minigame
                 ach_name = ""; supr_reward = 0
                 if minigame_name == "David’s Revenge":
                     supr_reward = 1; ach_name = ACH_DAVID_REVENGE_VICTOR
                 elif minigame_name == "Inverse Gauntlet":
                     supr_reward = 2; ach_name = ACH_INVERSE_GAUNTLET_VICTOR
                 if supr_reward > 0:
                     save_data["supercollateral_coins"] = save_data.get("supercollateral_coins", 0) + supr_reward
                     if ach_name and add_achievement_func: add_achievement_func(ach_name, None, unlocked_achievements_this_session_main)
                     save_save_data(save_data)
             else: # Player lost the minigame (minigame_result is False)
                 print(f"{minigame_name} failed (player lost).")
                 # If lost Inverse Gauntlet, end the run
                 if minigame_name == "Inverse Gauntlet":
                     print("Lost Inverse Gauntlet, ending run.")
                     level_outcome = "lose" # Set outcome to trigger game over logic

         elif minigame_result == "menu": # Player chose 'Main Menu' from pause
              level_outcome = "menu"

    # --- END FIX ---
    # --- FIX: Return current_seed_count instead of undefined current_seeds ---
    return (level_outcome, current_seed_count, level_duration, shop_upgrades, player_upgrades, checkpoint_count,
            seeds_collected_this_level, checkpoint_data if level_outcome == 'lose' and checkpoint_saved_this_level else None,
            player.last_ability) # Pass back player.last_ability
    # --- END FIX ---


# Function moved to ui.py
# def show_world_transition(screen, next_world): ...

def play_story_video(screen, clock, play_from_menu=False):
    """Plays the story video if libraries are available."""
    global MOVIEPY_AVAILABLE, np, NUMPY_AVAILABLE, VideoFileClip

    print(f"[Video Playback] Status Check - Moviepy: {MOVIEPY_AVAILABLE}, NumPy: {NUMPY_AVAILABLE}")
    if not MOVIEPY_AVAILABLE or not NUMPY_AVAILABLE or VideoFileClip is None:
        print("[Video Playback] Cannot play video: moviepy/numpy not available or VideoFileClip class missing.")
        placeholder_surf = FONT_MD.render("Story Video Skipped (moviepy/numpy not installed)", True, WHITE)
        placeholder_rect = placeholder_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.fill(BLACK); screen.blit(placeholder_surf, placeholder_rect); pygame.mouse.set_visible(True); pygame.display.flip(); pygame.time.wait(3000)
        return False

    video_path = STORY_VIDEO
    print(f"[Video Playback] Attempting to play video from: {video_path}")
    if not os.path.exists(video_path) or not os.path.isfile(video_path):
        print(f"[Video Playback] Story video file not found or is not a file: {video_path}")
        placeholder_surf = FONT_MD.render(f"Story Video Missing: {os.path.basename(video_path)}", True, RED)
        placeholder_rect = placeholder_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.fill(BLACK); screen.blit(placeholder_surf, placeholder_rect); pygame.mouse.set_visible(True); pygame.display.flip(); pygame.time.wait(3000)
        return False

    print("[Video Playback] Loading story video clip...")
    mixer_ok = pygame.mixer.get_init()
    original_volume = 0.6; was_music_playing_before_video = False
    if mixer_ok:
        was_music_playing_before_video = pygame.mixer.music.get_busy()
        if was_music_playing_before_video: original_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.stop()

    clip = None; video_played_successfully = False; temp_audio_path = None; audio_played_pygame = False; audio_ready_to_play = False

    try:
        print("[Video Playback] Loading VideoFileClip..."); clip = VideoFileClip(video_path, audio=True)
        print(f"[Video Playback] Video loaded: Duration={clip.duration:.2f}s, FPS={clip.fps}, Size={clip.size}")
        target_fps = clip.fps if clip.fps and clip.fps > 0 else FPS
        screen_w, screen_h = screen.get_size(); skip = False

        if mixer_ok and clip.audio:
            try:
                temp_audio_filename = f"temp_story_audio_{int(time.time())}.ogg"; temp_audio_path = os.path.join(os.path.dirname(video_path), temp_audio_filename)
                print(f"[Video Playback] Writing temporary audio to: {temp_audio_path}"); clip.audio.write_audiofile(temp_audio_path, codec='libvorbis', logger=None)
                if os.path.exists(temp_audio_path):
                    print(f"[Video Playback] Temporary audio written. Loading into Pygame mixer..."); pygame.mixer.music.load(temp_audio_path); pygame.mixer.music.set_volume(original_volume)
                    print(f"[Video Playback] Pygame mixer loaded audio. Playing..."); pygame.mixer.music.play(); audio_played_pygame = True; print("[Video Playback] Audio playback via Pygame Mixer started.")
                    audio_start_wait_time = time.time(); max_audio_wait_sec = 2.0
                    while not pygame.mixer.music.get_busy():
                        pygame.time.wait(10)
                        if time.time() - audio_start_wait_time > max_audio_wait_sec: print("[Video Playback WARNING] Audio did not start playing within timeout. Continuing video anyway."); break
                        for ev_wait in pygame.event.get():
                            if ev_wait.type == pygame.QUIT: pygame.quit(); exit()
                            if ev_wait.type == pygame.KEYDOWN and ev_wait.key == pygame.K_k: play_click_sound(); skip = True; print("[Video Playback] Video skipped while waiting for audio."); break
                        if skip: break
                    if not skip:
                         if pygame.mixer.music.get_busy(): print("[Video Playback] Audio confirmed playing. Starting video frames."); audio_ready_to_play = True
                         else: print("[Video Playback WARNING] Audio failed to start playing after wait period.")
                else: print(f"[Video Playback ERROR] Failed to create temporary audio file: {temp_audio_path}"); temp_audio_path = None; audio_played_pygame = False
            except Exception as audio_err:
                print(f"[Video Playback ERROR] Pygame mixer failed to load/play extracted audio: {audio_err}."); traceback.print_exc(); audio_played_pygame = False
                if temp_audio_path and os.path.exists(temp_audio_path):
                    try: os.remove(temp_audio_path)
                    except OSError: pass # Ignore error if removal fails here
                temp_audio_path = None # Reset path variable
        elif not clip.audio: print("[Video Playback WARNING] Video clip has no audio track.")
        else: print("[Video Playback WARNING] Pygame mixer not initialized. Video audio will not play.")

        video_w, video_h = clip.size; start_x = max(0, (screen_w - video_w) // 2); start_y = max(0, (screen_h - video_h) // 2)
        print(f"[Video Playback] Video size: {clip.size}. Positioning at ({start_x}, {start_y})")

        print("[Video Playback] Starting video frame iteration..."); video_start_time = time.time(); pygame.mouse.set_visible(False)
        video_time = 0.0; dt_video = 0.0

        if not skip and (audio_ready_to_play or not audio_played_pygame):
            while video_time < clip.duration and not skip:
                if audio_played_pygame and mixer_ok and pygame.mixer.music.get_busy():
                    current_audio_time = pygame.mixer.music.get_pos() / 1000.0
                    if current_audio_time > video_time + 0.1: video_time = current_audio_time - 0.05
                    elif video_time > current_audio_time + 0.2: pygame.time.wait(10); continue
                    dt_video = 1.0 / target_fps
                else: dt_video = clock.tick(target_fps) / 1000.0

                for ev in pygame.event.get():
                     if ev.type == pygame.QUIT: pygame.quit(); exit()
                     if ev.type == pygame.KEYDOWN and ev.key == pygame.K_k: play_click_sound(); skip = True; print("[Video Playback] Video skipped by user."); break
                if skip: break

                try: frame_array = clip.get_frame(video_time)
                except (IndexError, EOFError, ValueError) as frame_err: print(f"[Video Playback WARNING] Error getting frame at time {video_time:.2f}s: {frame_err}"); break
                except Exception as frame_err: print(f"[Video Playback ERROR] Unexpected error getting frame at time {video_time:.2f}s: {frame_err}"); traceback.print_exc(); video_time += 1.0 / target_fps; continue

                if frame_array is not None:
                    frame_shape = frame_array.shape
                    if len(frame_shape) == 3 and frame_shape[2] == 3:
                        try: frame_surface = pygame.surfarray.make_surface(np.swapaxes(frame_array, 0, 1))
                        except Exception as make_surf_err: print(f"[Video Playback ERROR] Error creating surface from frame: {make_surf_err}"); frame_surface = None
                        if frame_surface:
                            screen.fill(BLACK); screen.blit(frame_surface, (start_x, start_y))
                            skip_surf = FONT_SM.render("Press K to skip", True, WHITE)
                            skip_rect = skip_surf.get_rect(centerx=screen_w // 2, bottom=screen_h - 20)
                            text_bg_rect = skip_rect.inflate(10, 5); text_bg = pygame.Surface(text_bg_rect.size, pygame.SRCALPHA); text_bg.fill((0,0,0,150)); screen.blit(text_bg, text_bg_rect.topleft)
                            screen.blit(skip_surf, skip_rect); pygame.display.flip()
                        else: print(f"[Video Playback WARNING] Frame surface creation failed at time {video_time:.2f}")
                    else: print(f"[Video Playback WARNING] Invalid frame shape {frame_shape} at time {video_time:.2f}")
                else: print(f"[Video Playback WARNING] Got None frame at time {video_time:.2f}")

                video_time += dt_video
                if audio_played_pygame and mixer_ok and not pygame.mixer.music.get_busy() and (video_time > 0.5): print("[Video Playback] Audio finished playing according to mixer (secondary check). Ending video."); skip = True

        if not skip: video_played_successfully = True
        print("[Video Playback] Video finished or skipped.")

    except FileNotFoundError as fnf_err: print(f"!!!!!!!!!! [Video Playback ERROR] File Not Found !!!!!!!!!!!"); print(f"Specific Error: {fnf_err}"); error_surf = FONT_SM.render(f"Video File Missing: {os.path.basename(video_path)}", True, RED); error_rect = error_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)); screen.fill(BLACK); screen.blit(error_surf, error_rect); pygame.mouse.set_visible(True); pygame.display.flip(); pygame.time.wait(4000)
    except Exception as e: print(f"!!!!!!!!!! [Video Playback ERROR] Error during video setup or playback !!!!!!!!!!!"); traceback.print_exc(); print(f"Specific Error: {e}"); error_surf = FONT_SM.render(f"Error playing video. Check console.", True, RED); error_rect = error_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)); screen.fill(BLACK); screen.blit(error_surf, error_rect); pygame.mouse.set_visible(True); pygame.display.flip(); pygame.time.wait(4000)
    finally:
        pygame.mouse.set_visible(True)
        if audio_played_pygame and mixer_ok:
            try: pygame.mixer.music.stop(); pygame.mixer.music.unload()
            except Exception as stop_err: print(f"[Video Playback ERROR] Error stopping/unloading pygame music: {stop_err}")
        if temp_audio_path and os.path.exists(temp_audio_path):
            for _ in range(5):
                 try: print(f"[Video Playback] Removing temporary audio file: {temp_audio_path}"); os.remove(temp_audio_path); print(f"[Video Playback] Temporary audio file removed successfully."); break
                 except OSError as remove_err: print(f"[Video Playback ERROR] Error removing temporary audio file (Attempt {_ + 1}): {remove_err}"); time.sleep(0.2)
            else: print(f"[Video Playback CRITICAL ERROR] Could not remove temporary audio file after multiple attempts: {temp_audio_path}")
        if clip:
            try:
                if hasattr(clip, 'audio') and clip.audio is not None: print("[Video Playback] Closing clip audio resource..."); clip.audio.close()
                print("[Video Playback] Closing video clip resource..."); clip.close(); print("[Video Playback] Video clip closed.")
            except Exception as close_err: print(f"[Video Playback ERROR] Error closing video clip resources: {close_err}")

    print(f"[Video Playback] Returning video played successfully: {video_played_successfully}")
    return video_played_successfully


def main():
    """Main game function."""
    pygame.init(); mixer_ok = False
    try: pygame.mixer.init(); mixer_ok = True; print("Pygame mixer initialized successfully.")
    except pygame.error as e: print(f"Mixer init failed: {e}")

    screen_flags = pygame.FULLSCREEN | pygame.SCALED
    try: screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_flags); print(f"Using Fullscreen SCALED mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    except pygame.error as e:
        print(f"Fullscreen SCALED failed: {e}. Falling back to windowed."); screen_flags = pygame.RESIZABLE; window_width, window_height = 1280, 720
        try: screen = pygame.display.set_mode((window_width, window_height), screen_flags); print(f"Using windowed mode: {window_width}x{window_height}")
        except pygame.error as e2: print(f"Failed to set any display mode: {e2}. Exiting."); pygame.quit(); return

    pygame.display.set_caption("Superspeed Seeds: Racing Royale"); pygame.mouse.set_visible(True)
    clock = pygame.time.Clock(); load_save_data()

    def add_achievement(ach_name, achievement_banners_list, session_set):
        global save_data
        if ach_name not in MASTER_ACHIEVEMENT_LIST: print(f"Warning: Attempted to add unknown achievement '{ach_name}'"); return
        if "achievements" not in save_data or not isinstance(save_data["achievements"], list): save_data["achievements"] = []
        current_achievements = save_data["achievements"]
        if ach_name not in current_achievements and ach_name not in session_set:
            tier = ACHIEVEMENT_TIER_MAP.get(ach_name, "Bronze"); reward = ACHIEVEMENT_SUPR_REWARDS.get(tier, 0)
            current_achievements.append(ach_name); save_data["achievements"] = current_achievements
            save_data["supercollateral_coins"] = save_data.get("supercollateral_coins", 0) + reward
            session_set.add(ach_name); save_save_data(save_data)
            if achievement_banners_list is not None and isinstance(achievement_banners_list, list):
                 banner_text = f"Unlocked: {ach_name} (+{reward} SUPR)"; banner_color = ACHIEVEMENT_TIERS.get(tier, GOLD)
                 # --- FIX: Ensure banner 'y' starts off-screen ---
                 achievement_banners_list.append({"text": banner_text, "time": time.time(), "y": -60, "tier_color": banner_color})
                 # --- END FIX ---
                 print(f"Achievement Banner Added: {banner_text}")
            elif achievement_banners_list is None: pass # Do nothing if None (e.g., called from minigame end)
            else: print(f"Warning: achievement_banners_list is not None but not a list (type: {type(achievement_banners_list)})")
            print(f"Achievement Unlocked: {ach_name} ({tier}, +{reward} SUPR)")

            # --- Check for True Superseed achievement ---
            if ach_name != ACH_TRUE_SUPERSEED: # Avoid recursion
                unlocked_count = 0
                for master_ach in MASTER_ACHIEVEMENT_LIST:
                    if master_ach != ACH_TRUE_SUPERSEED and master_ach in save_data["achievements"]:
                        unlocked_count += 1
                # Check if all *other* achievements are unlocked
                if unlocked_count >= len(MASTER_ACHIEVEMENT_LIST) - 1:
                    add_achievement(ACH_TRUE_SUPERSEED, achievement_banners_list, session_set)
            # --- End check ---

    def play_menu_music():
        if mixer_ok and os.path.exists(BG_MUSIC):
            try:
                if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                     pygame.mixer.music.load(BG_MUSIC); pygame.mixer.music.set_volume(0.6); pygame.mixer.music.play(-1); print("Playing main menu music.")
            except pygame.error as e: print(f"Error playing main menu music: {e}")
    play_menu_music()

    while True:
        play_menu_music()
        option = main_menu(screen, save_data)

        if option == "exit": break
        elif option == "seederboard": display_leaderboard(screen, load_scores, save_data)
        elif option == "hall": hall_of_seeds(screen, save_data)
        elif option == "vault": repayment_vault_shop(screen, save_data); save_save_data(save_data)
        elif option == "tutorial":
            if os.path.exists(TUTORIAL_IMAGE): show_tutorial_image(screen, TUTORIAL_IMAGE, from_menu=True)
            if os.path.exists(TUTORIAL2_IMAGE): show_tutorial_image(screen, TUTORIAL2_IMAGE, from_menu=True)
            save_data["tutorial_shown"] = True; save_save_data(save_data)
        elif option == "story":
            play_story_video(screen, clock, play_from_menu=True); save_data["story_shown"] = True; save_save_data(save_data)
        elif option == "manwha": show_manwha_reader(screen)
        elif option == "start":
            difficulty = select_difficulty(screen);
            if difficulty is None: continue
            selected_driver = character_select(screen, save_data)
            if selected_driver is None: continue

            video_played_this_session = False; tutorials_shown_this_session = False
            show_story = not save_data.get("story_shown", False)
            show_tutorials = not save_data.get("tutorial_shown", False)

            if show_story:
                if mixer_ok: pygame.mixer.music.stop()
                video_played_this_session = play_story_video(screen, clock)
                if video_played_this_session: save_data["story_shown"] = True; save_save_data(save_data)
            if show_tutorials:
                if mixer_ok and not show_story: pygame.mixer.music.stop()
                if os.path.exists(TUTORIAL_IMAGE): show_tutorial_image(screen, TUTORIAL_IMAGE, from_menu=False)
                if os.path.exists(TUTORIAL2_IMAGE): show_tutorial_image(screen, TUTORIAL2_IMAGE, from_menu=False)
                tutorials_shown_this_session = True; save_data["tutorial_shown"] = True; save_save_data(save_data)

            pygame.event.clear()

            current_level = 1; total_time = 0.0; current_seeds = 0; total_seeds_collected_run = 0
            shop_upgrades = {"speed": 0, "seed_enemy": 0, "enemy_slow": 0}
            player_upgrades = {"shield": save_data.get("vault_upgrades", {}).get("starting_shield", 0)}
            checkpoint_count = INITIAL_CHECKPOINT_COUNT + save_data.get("vault_upgrades", {}).get("extra_life", 0)
            saved_checkpoint_data = None; level_duration = 0.0; unlocked_achievements_this_session_main.clear(); last_ability_time = -float('inf') # Reset last ability time at start of run

            if mixer_ok:
                if os.path.exists(INGAME_MUSIC):
                    try: pygame.mixer.music.load(INGAME_MUSIC); pygame.mixer.music.set_volume(0.6); pygame.mixer.music.play(-1); print("Playing in-game music.")
                    except pygame.error as e: print(f"Error playing in-game music: {e}")
                else: print(f"Warning: In-game music file not found: {INGAME_MUSIC}. No music will play."); pygame.mixer.music.stop()

            game_running = True
            while game_running and current_level <= MAX_LEVEL:
                start_pos, start_angle = None, None; was_loaded_from_checkpoint = False

                if saved_checkpoint_data:
                     load_result = load_from_checkpoint(saved_checkpoint_data)
                     if load_result:
                          (loaded_level, start_pos, start_angle, current_seeds, shop_upgrades, checkpoint_count, difficulty, last_ability_time) = load_result
                          current_level = loaded_level; player_upgrades['shield'] = save_data.get("vault_upgrades", {}).get("starting_shield", 0)
                          total_seeds_collected_run = current_seeds; was_loaded_from_checkpoint = True; print(f"Loaded level {current_level} from checkpoint.")
                     else: print("Error loading checkpoint data.")
                     saved_checkpoint_data = None

                initial_seeds_for_level = current_seeds

                if not was_loaded_from_checkpoint and current_level > 1:
                     prev_world = get_scene_description(current_level - 1); current_world = get_scene_description(current_level)
                     if prev_world != current_world: show_world_transition(screen, current_world)

                try:
                    # Pass current total_time to run_level
                    # --- FIX: Use correct variable name 'current_seeds' for the seed count ---
                    level_outcome, current_seeds, level_duration, shop_upgrades, player_upgrades, checkpoint_count, seeds_this_level, cp_data_on_loss, last_ability_time = run_level(
                        screen, current_level, current_seeds, shop_upgrades, player_upgrades, checkpoint_count, last_ability_time,
                        difficulty, start_pos, start_angle, selected_driver, add_achievement,
                        total_time, total_seeds_collected_run # Pass run totals
                    )
                    # --- END FIX ---
                except Exception as e:
                    print(f"!!! Critical Error during run_level call (Level {current_level}): {e} !!!"); traceback.print_exc()
                    level_outcome = "menu"; level_duration = 0; seeds_this_level = 0; cp_data_on_loss = None; last_ability_time = -float('inf')

                total_time += level_duration # Accumulate total time
                if not was_loaded_from_checkpoint: total_seeds_collected_run += seeds_this_level # Accumulate seeds only if not loaded

                if save_data.get("total_seeds_accumulated", 0) >= 1000: add_achievement(ACH_SEED_BANK_BARON, None, unlocked_achievements_this_session_main)
                # Check Bountiful Harvest using seeds collected *in that level*
                if seeds_this_level >= 100: add_achievement(ACH_BOUNTIFUL_HARVEST, None, unlocked_achievements_this_session_main)

                if level_outcome == "win":
                    show_level_clear(screen, current_level, level_duration)
                    # Pacifist run check happens *within* run_level now, just before returning "win"
                    current_level += 1
                    # --- Check win condition AFTER incrementing level ---
                    if current_level > MAX_LEVEL:
                         if total_time < (30 * 60): # Check if total time is under 30 minutes
                             add_achievement(ACH_TGE_ACHIEVED, None, unlocked_achievements_this_session_main)
                             print(f"TGE Achieved! Time: {total_time:.2f}s")
                         else:
                             print(f"Game Won! Time: {total_time:.2f}s (Over 30 mins for TGE achievement)")

                         # Check character-specific win achievements
                         if selected_driver == 1: add_achievement(ACH_WIN_SEEDGUY, None, unlocked_achievements_this_session_main)
                         elif selected_driver == 2: add_achievement(ACH_WIN_JOAO, None, unlocked_achievements_this_session_main)
                         elif selected_driver == 3: add_achievement(ACH_WIN_MESKY, None, unlocked_achievements_this_session_main)
                         elif selected_driver == 4: add_achievement(ACH_WIN_CHOSEN, None, unlocked_achievements_this_session_main)

                         # --- FIX: Show WIN screen instead of game over screen ---
                         win_game_name = show_win_screen(screen, total_time, total_seeds_collected_run) # Call the win screen
                         save_score(win_game_name, MAX_LEVEL, total_time, total_seeds_collected_run) # Save score
                         # --- END FIX ---

                         save_data["total_runs_completed"] = save_data.get("total_runs_completed", 0) + 1
                         save_save_data(save_data)
                         game_running = False; break

                elif level_outcome == "lose":
                    add_achievement(ACH_SPROUTED, None, unlocked_achievements_this_session_main) # Check "Sprouted" on loss too
                    if cp_data_on_loss:
                         saved_checkpoint_data = cp_data_on_loss
                         print("Player died, attempting to load last saved checkpoint.")
                         # No game over screen here, loop will continue and load checkpoint
                    else:
                        print("No checkpoint, game ended.")
                        save_data["total_runs_completed"] = save_data.get("total_runs_completed", 0) + 1
                        save_save_data(save_data)
                        # --- Show Game Over Screen AFTER loss and NO checkpoint ---
                        game_over_name = show_game_over(screen, current_level, total_time, total_seeds_collected_run)
                        save_score(game_over_name, current_level, total_time, total_seeds_collected_run)
                        # --- End Game Over Screen ---
                        game_running = False; break
                elif level_outcome == "menu": game_running = False; break
                elif level_outcome == "exit": game_running = False; option = "exit"; break

            print("Exiting level loop.")
            if mixer_ok: pygame.mixer.music.stop()

    pygame.quit()

if __name__ == "__main__":
    main()
# --- END OF FILE main.py ---