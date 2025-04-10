import pygame, time, os, math, json, random # Added random for wind effect
from settings import * # Imports all settings, including fonts and MASTER_ACHIEVEMENT_LIST

# Define consistent fonts locally in case they weren't imported via *
# (This section remains the same as before)
try:
    FONT_IMPACT_LG = pygame.font.SysFont("impact", 64)
    FONT_IMPACT_MD = pygame.font.SysFont("impact", 48)
    FONT_IMPACT_SM = pygame.font.SysFont("impact", 32)
    FONT_IMPACT_XSM = pygame.font.SysFont("impact", 24)
    FONT_IMPACT_XXSM = pygame.font.SysFont("impact", 20)
    FONT_IMPACT_XXXSM = pygame.font.SysFont("impact", 18) # <<< Added one smaller size
    FONT_IMPACT_TINY = pygame.font.SysFont("impact", 16)
    # --- Impact fonts for leaderboard (replaces Courier) ---
    FONT_LEADERBOARD_HEADER = pygame.font.SysFont("impact", 32) # Impact SM for header
    FONT_LEADERBOARD_SCORE = pygame.font.SysFont("impact", 48)  # Impact MD for scores
    # --- Font for Hall of Seeds SUPR count ---
    FONT_HALL_SUPR_COUNT = pygame.font.SysFont("impact", 42)
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
    FONT_HALL_SUPR_COUNT = pygame.font.Font(None, 42)


# UI Font Aliases (from settings.py, redefined for safety if needed)
ATTR_FONT = FONT_IMPACT_TINY
STORY_FONT = FONT_IMPACT_XXXSM
BUTTON_FONT = FONT_IMPACT_XSM
LEVEL_TEXT_FONT = FONT_IMPACT_SM
TITLE_FONT = FONT_IMPACT_MD
FONT_WEATHER = FONT_IMPACT_XXSM
CP_FONT = FONT_IMPACT_XSM
FONT_LG = FONT_IMPACT_LG
FONT_MD = FONT_IMPACT_MD
FONT_SM = FONT_IMPACT_SM
FONT_TINY = FONT_IMPACT_TINY # Alias added

# Vault shop text uses slightly smaller fonts
VAULT_SHOP_BUTTON_FONT = FONT_IMPACT_XXXSM # <<< CHANGED FONT ALIAS (was FONT_IMPACT_XXSM)
VAULT_COST_FONT = FONT_IMPACT_XXXSM # Slightly smaller font

# Define smaller font specifically for menu buttons
MENU_BUTTON_FONT = FONT_IMPACT_XSM # Use XSM size for menu buttons
# Use smaller vault close button font
VAULT_CLOSE_BUTTON_FONT = FONT_IMPACT_XXSM

# --- REMOVED global icon loading ---

# --- Sound Functions ---
def play_click_sound():
    if os.path.exists(CLICK_SOUND):
        try:
            if pygame.mixer.get_init():
                sound = pygame.mixer.Sound(CLICK_SOUND)
                sound.play()
            else:
                print("Warning: Mixer not initialized, cannot play click sound.")
        except pygame.error as e:
            print(f"Error playing click sound: {e}")

def play_freeze_sound():
    if os.path.exists(FREEZE_SOUND):
        try:
            if pygame.mixer.get_init():
                sound = pygame.mixer.Sound(FREEZE_SOUND)
                sound.play()
            else:
                print("Warning: Mixer not initialized, cannot play freeze sound.")
        except pygame.error as e:
            print(f"Error playing freeze sound: {e}")
# --- End Sound Functions ---

# --- Cache for Mesky Aura Image ---
MESKY_AURA_IMAGE_CACHE = None
MESKY_AURA_ROTATED_CACHE = None # <<< NEW Cache for the rotated image

# --- NEW: Moved get_scene_color from main.py to ui.py ---
# Helper function needed by show_world_transition
def get_scene_description_local(level): # Local helper, avoids importing from main
    level = max(1, level) # Ensure level is at least 1
    if level < 10: return "Earth World"
    elif level < 21: return "Fire World"
    elif level < 31: return "Water World"
    elif level < 41: return "Frost World"
    elif level < 51: return "Underworld"
    elif level < 61: return "Desert World"
    elif level < 71: return "Jungle World"
    elif level < 81: return "Space World"
    elif level < 91: return "Cyber World"
    elif level < 95: return "Mystic World (Inverse Controls)"
    else: return "Superseed World"

def get_scene_color(level):
    """Determines the background color based on the game level."""
    level = max(1, level)
    world_name = get_scene_description_local(level)
    color_map = {
        "Earth World": (50, 150, 50),
        "Fire World": (200, 50, 0),
        "Water World": (30, 100, 200),
        "Frost World": (180, 220, 250),
        "Underworld": (100, 0, 0),
        "Desert World": (237, 201, 175),
        "Jungle World": (0, 100, 0),
        "Space World": (10, 10, 30),
        "Cyber World": (0, 150, 150),
        "Mystic World (Inverse Controls)": (75, 0, 130),
        # Superseed World has special handling
    }
    # Superseed world color logic (Rainbow effect)
    if world_name == "Superseed World":
        # Generate a pseudo-random but somewhat consistent color based on level
        # This ensures it changes but doesn't flicker too wildly frame-to-frame if static
        r = (level * 30 + 50) % 205 + 50 # Range 50-255
        g = (level * 40 + 100) % 205 + 50
        b = (level * 50 + 150) % 205 + 50
        # Dim overly bright colors
        if r > 200 and g > 200 and b > 200:
            choice = level % 3
            if choice == 0: r = random.randint(50, 150)
            elif choice == 1: g = random.randint(50, 150)
            else: b = random.randint(50, 150)
        return (r, g, b)

    return color_map.get(world_name, BLACK) # Default to black if world not found
# --- END NEW ---


def draw_current_world_and_weather(surface, world_name, weather):
    """
    Draws the world name, weather name, and weather effect onto the provided surface.
    Returns the total height of the rendered block.
    """
    font_world = FONT_SM
    font_effect = FONT_IMPACT_XXXSM # Smaller font for effect
    line_spacing = 5

    # World Name
    world_surf = font_world.render(f"{world_name}", True, WHITE)
    world_rect = world_surf.get_rect(topleft=(0, 0)) # Position relative to surface

    # Weather Name
    weather_name_surf = font_world.render(f" | Weather: {weather.capitalize()}", True, WHITE)
    weather_name_rect = weather_name_surf.get_rect(midleft=(world_rect.right + 5, world_rect.centery))

    # Weather Effect Description
    effects = {
        "clear": "Effect: None",
        "rain": "Effect: Acceleration -20%",
        "wind": "Effect: Horizontal drift",
        "snow": "Effect: Acceleration -50%",
    }
    effect_text = effects.get(weather, "Effect: Unknown")
    effect_surf = font_effect.render(effect_text, True, GRAY)
    effect_rect = effect_surf.get_rect(topleft=(world_rect.left, world_rect.bottom + line_spacing)) # Position below world name

    # Blit onto the provided surface
    surface.blit(world_surf, world_rect)
    surface.blit(weather_name_surf, weather_name_rect)
    surface.blit(effect_surf, effect_rect)

    # Return the total height occupied
    total_height = effect_rect.bottom - world_rect.top
    return total_height


def draw_text_3d(screen, text, font, color, pos):
    main_text = font.render(text, True, color)
    screen.blit(main_text, pos)


def draw_button(screen, rect, text, font, text_color=WHITE):
    pygame.draw.rect(screen, WHITE, rect)
    main_text = font.render(text, True, BLACK)
    screen.blit(main_text, (rect.centerx - main_text.get_width() // 2,
                              rect.centery - main_text.get_height() // 2))

# Updated draw_plain_button to handle image backgrounds better and hover effect
def draw_plain_button(screen, rect, text, font, text_color=BLACK, border_color=BLACK, bg_color=WHITE, button_image_path=None, hover=False):
    btn_img = None
    draw_rect = rect
    hover_scale_factor = 1.03 # Scale slightly on hover

    if button_image_path and os.path.exists(button_image_path):
        try:
            btn_img_orig = pygame.image.load(button_image_path).convert_alpha()
            # Scale image based on hover state
            current_width = int(rect.width * hover_scale_factor) if hover else rect.width
            current_height = int(rect.height * hover_scale_factor) if hover else rect.height
            btn_img = pygame.transform.smoothscale(btn_img_orig, (current_width, current_height)) # Use smoothscale

            # Adjust rect for scaled image to keep it centered
            if hover:
                draw_rect = btn_img.get_rect(center=rect.center)

        except pygame.error as e:
            print(f"Error loading/scaling button image {button_image_path}: {e}")
            btn_img = None # Fallback to drawing rect if image fails
            draw_rect = rect # Use original rect if image fails
        except ValueError as e:
            print(f"Error during button image processing {button_image_path}: {e}")
            btn_img = None
            draw_rect = rect

    if btn_img:
        screen.blit(btn_img, draw_rect.topleft)
        # Optional: Add a subtle highlight border on hover even with image
        # if hover:
        #     pygame.draw.rect(screen, GOLD, draw_rect, 2, border_radius=5) # Example highlight
    else:
        # Fallback: Draw colored rect with border
        hover_bg_color = tuple(min(255, c + 20) for c in bg_color[:3]) if len(bg_color) >= 3 else WHITE # Slightly lighter bg on hover
        final_bg_color = hover_bg_color if hover else bg_color
        pygame.draw.rect(screen, final_bg_color, draw_rect) # Use draw_rect which might be scaled
        if border_color:
            hover_border_color = GOLD if hover else border_color # Change border color on hover
            pygame.draw.rect(screen, hover_border_color, draw_rect, 2) # Use draw_rect

    # Draw text centered on the original button's center, regardless of hover scaling
    txt = font.render(text, True, text_color)
    pos = (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2)
    screen.blit(txt, pos)


def draw_shop_overlay(screen, rect, text, font, button_image=BUTTON_IMAGE, text_color=BLACK):
    btn_img = None
    image_path_to_use = button_image if button_image and os.path.exists(button_image) else BUTTON_IMAGE

    if image_path_to_use and os.path.exists(image_path_to_use):
        try:
            btn_img = pygame.image.load(image_path_to_use).convert_alpha()
            btn_img = pygame.transform.scale(btn_img, (rect.width, rect.height))
        except pygame.error as e:
            print(f"Error loading/scaling button image {image_path_to_use}: {e}")
            btn_img = None

    if btn_img:
        screen.blit(btn_img, rect.topleft)
    else:
        pygame.draw.rect(screen, DARK_GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

    words = text.split(' ')
    lines = []
    current_line = ""
    max_width = rect.width - 40 # Adjusted padding
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())

    total_text_height = len(lines) * font.get_height()
    y = rect.centery - total_text_height // 2

    for line in lines:
        txt = font.render(line, True, text_color)
        screen.blit(txt, (rect.centerx - txt.get_width() // 2, y)) # Centered text
        y += font.get_height()

def draw_weather_info(screen, weather):
    effects = {
        "clear": "Clear - No effect",
        "rain": "Rainy - Acceleration -20%",
        # "fog": "Foggy - Reduced visibility", # --- REMOVED FOG ---
        "wind": "Windy - Horizontal drift (+40% Max Speed Force)",
        "snow": "Snowing - Acceleration -50%",
    }
    # --- FIX: Handle case where weather might be fog if code isn't fully updated ---
    text = effects.get(weather, "No effect") if weather != "fog" else "No effect"
    text_surf = FONT_WEATHER.render(text, True, WHITE)
    pos = (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, 10 + LEVEL_TEXT_FONT.get_height() + FONT_SM.get_height() + 10)
    # screen.blit(text_surf, pos) # This display is now handled in draw_current_world_and_weather

    # --- REMOVED FOG RENDERING LOGIC ---
    # if weather == "fog": ...

    if weather == "wind":
        wind_offset = (pygame.time.get_ticks() // 100) % 50
        for i in range(10):
            start_x = random.randint(TRACK_LEFT, TRACK_RIGHT)
            start_y = random.randint(TRACK_TOP, TRACK_BOTTOM)
            end_x = start_x + 15
            end_y = start_y
            pygame.draw.line(screen, GRAY, (start_x, start_y), (end_x, end_y), 1)


SHOP_BUTTON_WIDTH = 150
SHOP_BUTTON_HEIGHT = 40
SHOP_BUTTON_MARGIN = 10

CP_BUTTON_WIDTH = 220
CP_BUTTON_HEIGHT = 40
CP_BUTTON_RIGHT_MARGIN = 10 # Make sure this is defined (used in draw_attributes)

# --- FIX: Re-calculate button positions relative to TRACK_RIGHT and TRACK_TOP ---
SHOP_BUTTON_RECT = pygame.Rect(
    TRACK_RIGHT - SHOP_BUTTON_WIDTH - SHOP_BUTTON_MARGIN,
    TRACK_TOP + SHOP_BUTTON_MARGIN,
    SHOP_BUTTON_WIDTH,
    SHOP_BUTTON_HEIGHT
)

CHECKPOINT_RECT = pygame.Rect(
    SHOP_BUTTON_RECT.left - CP_BUTTON_WIDTH - CP_BUTTON_RIGHT_MARGIN,
    SHOP_BUTTON_RECT.top,
    CP_BUTTON_WIDTH,
    CP_BUTTON_HEIGHT
)

# --- FIX: Re-calculate HELP_BUTTON_RECT position ---
HELP_BUTTON_SIZE = 35
HELP_BUTTON_MARGIN = 10
HELP_BUTTON_RECT = pygame.Rect(
    TRACK_RIGHT - HELP_BUTTON_SIZE - HELP_BUTTON_MARGIN, # Align with right edge like shop button
    SHOP_BUTTON_RECT.bottom + HELP_BUTTON_MARGIN, # Below shop button
    HELP_BUTTON_SIZE, # Width
    HELP_BUTTON_SIZE # Height
)
# --- END FIX ---

def draw_checkpoint_button(surface, checkpoint_count, can_use, checkpoint_feedback_time, save_data):
    simple_font = CP_FONT
    vault_upgrades = save_data.get("vault_upgrades", {})
    max_checkpoints = INITIAL_CHECKPOINT_COUNT + vault_upgrades.get("extra_life", 0)
    txt = f"Checkpoints: {checkpoint_count}/{max_checkpoints}"

    text_surf = simple_font.render(txt, True, BLACK)
    text_rect = text_surf.get_rect(center=CHECKPOINT_RECT.center)

    can_use_cp = checkpoint_count > 0 and can_use # Check if usable *this level*

    fill_color = GOLD if can_use_cp else GRAY
    pygame.draw.rect(surface, fill_color, (0, 0, CHECKPOINT_RECT.width, CHECKPOINT_RECT.height)) # Draw relative to surface
    pygame.draw.rect(surface, BLACK, (0, 0, CHECKPOINT_RECT.width, CHECKPOINT_RECT.height), 2) # Draw relative to surface

    # Center text on the surface
    surface.blit(text_surf, text_surf.get_rect(center=(CHECKPOINT_RECT.width // 2, CHECKPOINT_RECT.height // 2)))

    if checkpoint_feedback_time and time.time() - checkpoint_feedback_time < 1.0:
        fb = "Saved!"
        fb_surf = simple_font.render(fb, True, GREEN)
        # Draw feedback relative to the button's *original* position on the main screen
        # This part might need adjustment depending on how the surface is blitted
        fb_rect = fb_surf.get_rect(midtop=(CHECKPOINT_RECT.centerx, CHECKPOINT_RECT.bottom + 5))
        # screen.blit(fb_surf, fb_rect) # Can't draw directly on 'screen' here, caller needs to handle feedback
    elif can_use_cp: # Only show if usable
        press_c_font = FONT_TINY # Use smallest font
        press_c_surf = press_c_font.render("(Press C)", True, WHITE)
        # Draw below the button's original position
        press_c_rect = press_c_surf.get_rect(midtop=(CHECKPOINT_RECT.centerx, CHECKPOINT_RECT.bottom + 3))
        # Add background for readability
        press_c_bg_rect = press_c_rect.inflate(6, 2)
        press_c_bg_surf = pygame.Surface(press_c_bg_rect.size, pygame.SRCALPHA)
        press_c_bg_surf.fill((0, 0, 0, 100))
        # screen.blit(press_c_bg_surf, press_c_bg_rect.topleft) # Caller needs to handle this
        # screen.blit(press_c_surf, press_c_rect)


def draw_shop_button(surface):
    button_font = CP_FONT
    txt = "Shop"
    text_surf = button_font.render(txt, True, BLACK)

    fill_color = GREEN
    pygame.draw.rect(surface, fill_color, (0, 0, SHOP_BUTTON_RECT.width, SHOP_BUTTON_RECT.height)) # Draw relative
    pygame.draw.rect(surface, BLACK, (0, 0, SHOP_BUTTON_RECT.width, SHOP_BUTTON_RECT.height), 2) # Draw relative
    # Center text on the surface
    surface.blit(text_surf, text_surf.get_rect(center=(SHOP_BUTTON_RECT.width // 2, SHOP_BUTTON_RECT.height // 2)))


# --- NEW: Draw Help Button ---
def draw_help_button(surface):
    help_font = FONT_IMPACT_XSM # Use a small-ish font
    txt = "?"
    text_surf = help_font.render(txt, True, BLACK)

    fill_color = TURQUOISE # Use a distinct color
    pygame.draw.rect(surface, fill_color, (0, 0, HELP_BUTTON_RECT.width, HELP_BUTTON_RECT.height), border_radius=5) # Draw relative
    pygame.draw.rect(surface, BLACK, (0, 0, HELP_BUTTON_RECT.width, HELP_BUTTON_RECT.height), 2, border_radius=5) # Draw relative
    # Center text on the surface
    surface.blit(text_surf, text_surf.get_rect(center=(HELP_BUTTON_RECT.width // 2, HELP_BUTTON_RECT.height // 2)))

# --- END NEW ---

# --- UPDATED: draw_attributes to include Vault info ---
def draw_attributes(surface, shop_upgrades, player_upgrades, save_data): # Added save_data parameter
    """Draws player attributes and relevant vault upgrades onto the provided surface."""
    # global save_data # REMOVED - Use parameter instead
    surface.fill((50, 50, 50, 180)) # Fill surface with background

    attr_width = surface.get_width()
    attr_height = surface.get_height()

    # Shop Upgrades
    shop_speed_lvl = shop_upgrades.get('speed', 0)
    shop_seed_enemy_lvl = shop_upgrades.get('seed_enemy', 0)
    shop_enemy_slow_lvl = shop_upgrades.get('enemy_slow', 0)
    has_shield = player_upgrades.get('shield', 0) > 0

    # Vault Upgrades
    vault_upgrades = save_data.get("vault_upgrades", {})
    vault_speed_lvl = vault_upgrades.get("node_speed_boost", 0)
    vault_shield = vault_upgrades.get("starting_shield", 0) >= 1
    vault_cd = vault_upgrades.get("cooldown_reduction", 0) >= 1
    vault_aura_lvl = vault_upgrades.get("enemy_slow_aura", 0)

    texts = [
        f"Speed Lvl: {shop_speed_lvl}",
        f"Seed/Enemy Lvl: {shop_seed_enemy_lvl}/{SHOP_SEED_ENEMY_MAX_LEVEL}",
        f"Shield: {'Active' if has_shield else 'None'}",
        f"Enemy Slow Lvl: {shop_enemy_slow_lvl}",
    ]

    # Add Vault info if active
    vault_texts = []
    if vault_speed_lvl > 0: vault_texts.append(f"Vault Speed: +{vault_speed_lvl*4}%")
    if vault_shield: vault_texts.append("Vault Shield: Active")
    if vault_cd: vault_texts.append("Vault CD: -20%")
    if vault_aura_lvl > 0: vault_texts.append(f"Vault Aura: {vault_aura_lvl*7}%")

    all_lines = texts + vault_texts

    y_pos = 5
    x_pos = 10
    line_height = ATTR_FONT.get_height() + 3
    # Adjust columns based on total lines
    num_lines = len(all_lines)
    max_lines_per_col = (num_lines + 1) // 2 # Try to balance columns
    col_width = attr_width // 2 - 10

    for i, text in enumerate(all_lines):
        plain = ATTR_FONT.render(text, True, WHITE)
        col = i // max_lines_per_col
        row = i % max_lines_per_col
        current_x = x_pos + col * col_width
        current_y = y_pos + row * line_height
        surface.blit(plain, (current_x, current_y))

    pygame.draw.rect(surface, WHITE, surface.get_rect(), 1) # Draw border on the surface itself
# --- END UPDATE ---


# --- UPDATED: draw_shield_aura for Ability VFX, Mesky Image, and Chosen Pulse ---
def draw_shield_aura(screen, player, current_time):
    global MESKY_AURA_IMAGE_CACHE, MESKY_AURA_ROTATED_CACHE # Use the caches

    has_permanent_shield = player.upgrades.get('shield', 0) > 0 # Check if player has a purchased/vault shield
    is_temporarily_invincible = current_time < player.invincible_until # Generic invincibility (e.g. after shield break)
    is_temp_shield_powerup_active = hasattr(player, 'temp_shield_end_time') and current_time < player.temp_shield_end_time # Check powerup specifically
    is_chosen_ability_active = player.character == 4 and player.ability_active
    is_mesky_ability_active = player.character == 3 and player.ability_active

    radius = player.radius
    color = None
    thickness = 3
    image_to_draw = None # For Mesky's aura image
    img_alpha = 255
    img_size = player.size # Default to player size for Mesky aura

    # Order of precedence: Chosen > Temp Shield Powerup > Generic Temp Invincible > Mesky > Permanent Shield
    if is_chosen_ability_active:
        # Chosen ability aura (Smaller gold pulsing circle)
        pulse_freq = 10.0 # Faster pulse
        pulse_factor = abs(math.sin(current_time * pulse_freq))
        base_radius_chosen = int(player.radius * 0.8) # Smaller base
        radius = int(base_radius_chosen + 5 * pulse_factor) # Pulsate radius slightly
        alpha = int(180 + 75 * pulse_factor) # Strong alpha
        color = (255, 215, 0, alpha) # Gold pulse
        thickness = 3 # Reduced thickness slightly
    elif is_temp_shield_powerup_active: # Check temp shield powerup BEFORE generic invincibility
        # Faint blue aura, slightly larger than permanent
        radius = int(player.radius + 8) # Slightly larger than permanent shield radius
        pulse_alpha = abs(math.sin(current_time * 2.5)) # Slightly faster pulse
        alpha = int(60 + 90 * pulse_alpha) # Slightly stronger alpha
        color = (0, 180, 255, alpha) # Slightly different blue
        thickness = 3
    elif is_temporarily_invincible:
        # Generic invincibility flash (e.g., after shield break)
        radius = int(player.radius + 10)
        pulse_alpha = abs(math.sin(current_time * 5))
        alpha = int(100 + 155 * pulse_alpha)
        color = (255, 255, 0, alpha) # Yellow flash
        thickness = 5
    elif is_mesky_ability_active:
        # --- Load and Rotate Mesky Aura Image (if needed) ---
        if MESKY_AURA_ROTATED_CACHE is None: # Only load and rotate once
            if MESKY_AURA_IMAGE_CACHE is None and os.path.exists(SLOW_AURA_IMAGE):
                try:
                    MESKY_AURA_IMAGE_CACHE = pygame.image.load(SLOW_AURA_IMAGE).convert_alpha()
                    print("Loaded Mesky slow aura image.")
                except Exception as e:
                    print(f"Error loading Mesky slow aura image: {e}")
                    MESKY_AURA_IMAGE_CACHE = "error" # Mark as error to avoid retrying

            if MESKY_AURA_IMAGE_CACHE and MESKY_AURA_IMAGE_CACHE != "error":
                try:
                    # Rotate 90 degrees counter-clockwise (adjust if base image orientation is different)
                    MESKY_AURA_ROTATED_CACHE = pygame.transform.rotate(MESKY_AURA_IMAGE_CACHE, 90)
                    print("Rotated and cached Mesky slow aura image.")
                except Exception as e:
                    print(f"Error rotating Mesky aura image: {e}")
                    MESKY_AURA_ROTATED_CACHE = "error"
            else:
                MESKY_AURA_ROTATED_CACHE = "error" # Mark rotated as error if base failed
        # --- End Load/Rotate ---

        if MESKY_AURA_ROTATED_CACHE and MESKY_AURA_ROTATED_CACHE != "error":
            image_to_draw = MESKY_AURA_ROTATED_CACHE # Use the rotated image
            # Pulsate alpha
            pulse_freq = 3.0
            pulse_alpha = abs(math.sin(current_time * pulse_freq))
            img_alpha = int(100 + 60 * pulse_alpha) # Pulsating alpha for the image
            # Pulsate size slightly around player size - make it smaller overall
            size_pulse = 0.9 + 0.05 * pulse_alpha # Scale between 0.9 and 0.95 of player size
            img_size = (int(player.size[0] * size_pulse), int(player.size[1] * size_pulse))

        else: # Fallback circle if image failed
            radius = int(player.radius * 1.5) # Larger than player, smaller than old circle
            pulse_alpha = abs(math.sin(current_time * 3))
            alpha = int(60 + 50 * pulse_alpha)
            color = (100, 0, 150, alpha) # Purple-ish color
            thickness = 4

    elif has_permanent_shield:
        # Faint blue aura for active shield (purchased or vault)
        radius = int(player.radius + 5) # Slightly larger than player
        pulse_alpha = abs(math.sin(current_time * 2)) # Slow pulse
        alpha = int(50 + 70 * pulse_alpha) # Faint alpha
        color = (0, 150, 255, alpha) # Blue shield color
        thickness = 2

    # --- Draw Logic ---
    # Draw the image first if it exists
    if image_to_draw:
        try:
            # Ensure positive size for scaling
            if img_size[0] > 0 and img_size[1] > 0:
                scaled_img = pygame.transform.smoothscale(image_to_draw, img_size)
                scaled_img.set_alpha(img_alpha)
                img_rect = scaled_img.get_rect(center=(int(player.pos_x), int(player.pos_y)))
                screen.blit(scaled_img, img_rect)
            else:
                 print(f"Warning: Invalid Mesky aura size for scaling: {img_size}")
        except (ValueError, pygame.error) as e:
            print(f"Error scaling/drawing Mesky aura image: {e}")

    # Draw the circle overlay if color is defined
    if color and radius > 0:
        aura_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        try:
            pygame.draw.circle(aura_surf, color, (radius, radius), radius, thickness)
            screen.blit(aura_surf, (int(player.pos_x - radius), int(player.pos_y - radius)))
        except ValueError: # Handle potential errors with radius/thickness
            pass
# --- END UPDATE ---


def draw_game_border(screen):
    border_thickness = 5
    pygame.draw.rect(screen, (139, 0, 0),
                     (TRACK_LEFT - border_thickness, TRACK_TOP - border_thickness,
                      TRACK_RIGHT - TRACK_LEFT + 2 * border_thickness,
                      TRACK_BOTTOM - TRACK_TOP + 2 * border_thickness),
                     border_thickness)

def draw_ability_icon(screen, player, current_time):
    # --- Position relative to screen center top ---
    meter_width = 150
    meter_height = 15
    meter_x = SCREEN_WIDTH // 2 - meter_width // 2
    meter_y = 15 # Keep Y position

    icon_size_base = 60
    icon_size = (int(icon_size_base * 0.85), int(icon_size_base * 0.85)) # Reduced by 15%
    icon_padding = 10 # Keep padding

    time_since_ability = current_time - player.last_ability
    cooldown_ratio = min(time_since_ability / player.cooldown, 1.0) if player.cooldown > 0 else 1.0
    is_ready = cooldown_ratio >= 1.0

    # Draw Cooldown Meter
    pygame.draw.rect(screen, GRAY, (meter_x, meter_y, meter_width, meter_height))
    fill_color = GREEN if is_ready else RED
    pygame.draw.rect(screen, fill_color, (meter_x, meter_y, int(meter_width * cooldown_ratio), meter_height))
    pygame.draw.rect(screen, WHITE, (meter_x, meter_y, meter_width, meter_height), 2)

    # Draw Ability Icon (Right of Meter)
    icon_x = meter_x + meter_width + icon_padding
    icon_y = meter_y + (meter_height // 2) - (icon_size[1] // 2)

    ability_icon_to_draw = player.ability_icon
    if ability_icon_to_draw and ability_icon_to_draw.get_width() > 1 and ability_icon_to_draw.get_height() > 1:
        try:
            scaled_icon = pygame.transform.smoothscale(ability_icon_to_draw, icon_size) # Use smoothscale
            screen.blit(scaled_icon, (icon_x, icon_y))
            if is_ready:
                glow_radius_factor = 1.05 # Relative glow size
                glow_radius = int(icon_size[0] / 2 * glow_radius_factor)
                glow_thickness = 3
                glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 255, 255, 80), (glow_radius, glow_radius), glow_radius, glow_thickness) # Draw glow on separate surface
                screen.blit(glow_surf, (icon_x + icon_size[0]//2 - glow_radius, icon_y + icon_size[1]//2 - glow_radius)) # Center glow around icon

        except (pygame.error, ValueError) as e:
            print(f"Error scaling ability icon for display: {e}")
            fallback_surf = pygame.Surface(icon_size, pygame.SRCALPHA)
            fallback_surf.fill(DARK_GRAY)
            pygame.draw.line(fallback_surf, RED, (0, 0), (icon_size[0]-1, icon_size[1]-1), 2)
            pygame.draw.line(fallback_surf, RED, (0, icon_size[1]-1), (icon_size[0]-1, 0), 2)
            screen.blit(fallback_surf, (icon_x, icon_y))

    else:
        fallback_surf = pygame.Surface(icon_size, pygame.SRCALPHA)
        fallback_surf.fill(DARK_GRAY)
        pygame.draw.line(fallback_surf, RED, (0, 0), (icon_size[0]-1, icon_size[1]-1), 2)
        pygame.draw.line(fallback_surf, RED, (0, icon_size[1]-1), (icon_size[0]-1, 0), 2)
        screen.blit(fallback_surf, (icon_x, icon_y))

    # Draw Cooldown Text (Left of Meter)
    text_x = meter_x - icon_padding
    cooldown_font = FONT_TINY
    if is_ready:
         ready_text_surf = cooldown_font.render("Ready! [SPACE]", True, WHITE)
         ready_rect = ready_text_surf.get_rect(midright=(text_x, meter_y + meter_height // 2))
         screen.blit(ready_text_surf, ready_rect)
    else:
         time_left = max(0.0, player.cooldown - time_since_ability) # Prevent negative display
         cd_text_surf = cooldown_font.render(f"{time_left:.1f}s", True, WHITE)
         cd_rect = cd_text_surf.get_rect(midright=(text_x, meter_y + meter_height // 2))
         screen.blit(cd_text_surf, cd_rect)


# --- NEW: Function to draw key representations ---
def draw_key_box(screen, text, center_pos, font, width=40, height=40, bg_color=DARK_GRAY, text_color=WHITE, border_color=WHITE):
    key_rect = pygame.Rect(0, 0, width, height)
    key_rect.center = center_pos
    pygame.draw.rect(screen, bg_color, key_rect, border_radius=5)
    pygame.draw.rect(screen, border_color, key_rect, 1, border_radius=5)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=key_rect.center)
    screen.blit(text_surf, text_rect)
    return key_rect # Return rect for positioning other elements
# --- END NEW ---

# --- UPDATED: show_controls_overlay with LAYOUT FIXES ---
def show_controls_overlay(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))

    # --- Panel for Controls ---
    panel_width_controls = 900 # Keep width
    panel_height_controls = 430 # Keep height
    panel_rect_controls = pygame.Rect(0, 0, panel_width_controls, panel_height_controls)
    panel_rect_controls.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100) # Move panel slightly up
    panel_bg_color = (30, 30, 30)
    panel_border_color = TURQUOISE

    # --- Adjusted Fonts ---
    control_font = FONT_IMPACT_XXSM # <<< CHANGED FONT (was XSM)
    key_font = FONT_IMPACT_XXXSM # <<< CHANGED FONT (was XXSM)
    title_font = FONT_IMPACT_MD # <<< KEPT MD (smaller was requested but MD looks ok)

    # --- Panel for Description ---
    panel_width_desc = 900 # Match controls width
    panel_height_desc = 220 # Keep description height
    panel_rect_desc = pygame.Rect(0, 0, panel_width_desc, panel_height_desc)
    panel_rect_desc.center = (SCREEN_WIDTH // 2, panel_rect_controls.bottom + panel_height_desc // 2 + 20)
    desc_font = FONT_IMPACT_XXXSM # Keep description font
    desc_line_height = desc_font.get_height() + 4 # Keep description line height

    # Draw Controls Panel
    pygame.draw.rect(overlay, panel_bg_color, panel_rect_controls, border_radius=10)
    pygame.draw.rect(overlay, panel_border_color, panel_rect_controls, 2, border_radius=10)

    # Controls Title
    title_surf = title_font.render("Controls", True, WHITE)
    title_rect = title_surf.get_rect(centerx=panel_rect_controls.centerx, top=panel_rect_controls.top + 15) # Reduced top padding
    overlay.blit(title_surf, title_rect)

    # --- Control Layout Adjustments ---
    label_x = panel_rect_controls.left + 80  # Keep left padding for labels
    key_area_x_start = panel_rect_controls.centerx - 150  # Keep WASD block position
    start_y = title_rect.bottom + 35  # Reduced space below title
    line_spacing = 55  # <<< REDUCED line spacing (was 65)
    key_box_size = 35  # <<< REDUCED key box size (was 40)
    key_spacing_wasd = 18  # <<< INCREASED spacing for WASD (was 15)
    key_spacing_arrows = 18  # <<< INCREASED spacing for Arrows (was 15)

    # Movement
    move_y = start_y
    move_label = control_font.render("Movement", True, WHITE)
    wasd_block_height = key_box_size * 2 + key_spacing_wasd  # Use new spacing
    move_label_centery = move_y + wasd_block_height / 2
    move_rect = move_label.get_rect(left=label_x, centery=move_label_centery)
    overlay.blit(move_label, move_rect)

    # WASD Keys (Increased spacing)
    w_key_center_x = key_area_x_start + key_box_size / 2 + key_spacing_wasd  # X for W and S keys
    a_key_center_x = key_area_x_start  # X for A key
    d_key_center_x = key_area_x_start + key_box_size + key_spacing_wasd * 2  # X for D key

    w_key_center_y = move_y + key_box_size / 2  # Y for W key
    as_key_center_y = move_y + key_box_size + key_spacing_wasd + key_box_size / 2  # Y for A, S, D keys

    w_key = draw_key_box(overlay, "W", (w_key_center_x, w_key_center_y), key_font, width=key_box_size,
                         height=key_box_size)
    a_key = draw_key_box(overlay, "A", (a_key_center_x, as_key_center_y), key_font, width=key_box_size,
                         height=key_box_size)
    s_key = draw_key_box(overlay, "S", (w_key_center_x, as_key_center_y), key_font, width=key_box_size,
                         height=key_box_size)
    d_key = draw_key_box(overlay, "D", (d_key_center_x, as_key_center_y), key_font, width=key_box_size,
                         height=key_box_size)

    # OR Text (Positioned between WASD and Arrows)
    or_text = FONT_TINY.render("OR", True, GRAY)
    or_text_x = d_key.right + 75  # Keep space
    or_rect = or_text.get_rect(centerx=or_text_x, centery=move_rect.centery)
    overlay.blit(or_text, or_rect)

    # Arrow Keys (Increased spacing)
    arrow_x_start = or_rect.right + 75  # Keep space
    arrow_key_size = key_box_size  # <<< Make arrows same size as WASD
    up_key_center_x = arrow_x_start + arrow_key_size / 2 + key_spacing_arrows
    left_key_center_x = arrow_x_start
    right_key_center_x = arrow_x_start + arrow_key_size + key_spacing_arrows * 2

    up_key_center_y = w_key_center_y
    lr_key_center_y = as_key_center_y

    up_key = draw_key_box(overlay, "^", (up_key_center_x, up_key_center_y), key_font, width=arrow_key_size,
                          height=arrow_key_size)
    left_key = draw_key_box(overlay, "<", (left_key_center_x, lr_key_center_y), key_font, width=arrow_key_size,
                            height=arrow_key_size)
    down_key = draw_key_box(overlay, "v", (up_key_center_x, lr_key_center_y), key_font, width=arrow_key_size,
                            height=arrow_key_size)
    right_key = draw_key_box(overlay, ">", (right_key_center_x, lr_key_center_y), key_font, width=arrow_key_size,
                             height=arrow_key_size)

    # --- Other Controls (Positioned Below Movement, Aligned Left) ---
    other_controls_start_x = panel_rect_controls.left + 120  # Keep start position
    # --- FIX: Calculate fixed X for key boxes based on longest label ---
    longest_label_surf = control_font.render("Checkpoint", True, WHITE)
    key_box_x_fixed = other_controls_start_x + longest_label_surf.get_width() + 60  # Add fixed gap
    # --- END FIX ---

    # Ability
    ability_y = move_y + key_box_size * 2 + key_spacing_wasd * 2 + line_spacing + 5  # Adjusted Y start, used reduced line_spacing
    ability_label = control_font.render("Ability", True, WHITE)
    ability_rect = ability_label.get_rect(left=other_controls_start_x, centery=ability_y)
    overlay.blit(ability_label, ability_rect)
    # --- FIX: Use fixed X for key box ---
    draw_key_box(overlay, "SPACE", (key_box_x_fixed + (100 - key_box_size) // 2, ability_rect.centery), key_font,
                 width=100, height=key_box_size)

    # Pause
    pause_y = ability_y + line_spacing
    pause_label = control_font.render("Pause", True, WHITE)
    pause_rect = pause_label.get_rect(left=other_controls_start_x, centery=pause_y)
    overlay.blit(pause_label, pause_rect)
    # --- FIX: Use fixed X for key box ---
    draw_key_box(overlay, "P", (key_box_x_fixed, pause_rect.centery), key_font, width=key_box_size, height=key_box_size)

    # Checkpoint
    cp_y = pause_y + line_spacing
    cp_label = control_font.render("Checkpoint", True, WHITE)
    cp_rect = cp_label.get_rect(left=other_controls_start_x, centery=cp_y)
    overlay.blit(cp_label, cp_rect)
    # --- FIX: Use fixed X for key box ---
    draw_key_box(overlay, "C", (key_box_x_fixed, cp_rect.centery), key_font, width=key_box_size, height=key_box_size)
    # --- END FIX ---

    # --- Draw Description Panel ---
    pygame.draw.rect(overlay, panel_bg_color, panel_rect_desc, border_radius=10)
    pygame.draw.rect(overlay, panel_border_color, panel_rect_desc, 2, border_radius=10)

    desc_title_surf = FONT_SM.render("Game Info", True, WHITE) # Smaller font for title
    desc_title_rect = desc_title_surf.get_rect(centerx=panel_rect_desc.centerx, top=panel_rect_desc.top + 12) # Reduced padding
    overlay.blit(desc_title_surf, desc_title_rect)

    # --- Game Description Text ---
    desc_text_lines = [
        "• Goal: Reach the Exit Portal! Collect Seeds for Shop upgrades.",
        "• Avoid Enemies & Projectiles. Use Checkpoints (C) wisely.",
        "• Abilities (SPACE): Unique skill for each character.",
        "• Power-ups: Freeze (Slows), Magnet (Pulls), Shield, Seed Doubler.",
        "• Minigames: Chance for bonus Seeds or SUPR after levels.",
        "• Vault (Menu): Use SUPR from Achievements for permanent upgrades.",
        "• Difficulty: Hard = More/faster enemies.",
    ]
    current_desc_y = desc_title_rect.bottom + 12 # Reduced space
    desc_left_padding = 25 # Reduced indent

    for line in desc_text_lines:
        words = line.split(' ')
        wrapped_lines = []; current_line = ""
        max_desc_width = panel_rect_desc.width - (desc_left_padding * 2)

        for word in words:
            test_line = current_line + word + " ";
            if desc_font.size(test_line)[0] < max_desc_width: current_line = test_line
            else: wrapped_lines.append(current_line.strip()); current_line = word + " "
        wrapped_lines.append(current_line.strip())

        for i, wrapped_line in enumerate(wrapped_lines):
            if current_desc_y + desc_line_height < panel_rect_desc.bottom - 10:
                indent = desc_left_padding if i == 0 else desc_left_padding + 10 # Slightly less indent for wrapped lines
                line_surf = desc_font.render(wrapped_line, True, WHITE);
                line_rect = line_surf.get_rect(left=panel_rect_desc.left + indent, top=current_desc_y)
                overlay.blit(line_surf, line_rect)
                current_desc_y += desc_line_height
            else: break
        if not (current_desc_y + desc_line_height < panel_rect_desc.bottom - 10): break

    # --- Close Instruction (Common) ---
    close_font = FONT_IMPACT_XXXSM
    close_text = close_font.render("Press K or ESC to Close", True, GRAY)
    close_rect = close_text.get_rect(centerx=SCREEN_WIDTH // 2, top=panel_rect_desc.bottom + 12) # Slightly closer
    overlay.blit(close_text, close_rect)

    # Blit the overlay onto the main screen
    screen.blit(overlay, (0, 0))
    pygame.mouse.set_visible(True)
    pygame.display.flip()

    # Pause Loop
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_k or event.key == pygame.K_p: # Added P as exit key too
                    play_click_sound(); waiting_for_input = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                 play_click_sound(); waiting_for_input = False
        pygame.time.Clock().tick(30)
# --- END UPDATE ---


def main_menu(screen, save_data):
    bg_menu = None
    if os.path.exists(BACKGROUND_MENU):
        try:
            bg_menu = pygame.image.load(BACKGROUND_MENU).convert()
            bg_menu = pygame.transform.scale(bg_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading main menu background: {e}")

    menu_font = MENU_BUTTON_FONT

    button_width = 350
    button_height = 60
    button_spacing = 18
    num_buttons = 8
    total_button_block_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
    start_y = (SCREEN_HEIGHT // 2) - (total_button_block_height // 2) + 50 + 5 # Keep button block position

    start_journey_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 0 * (button_height + button_spacing), button_width, button_height)
    story_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 1 * (button_height + button_spacing), button_width, button_height)
    board_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    hall_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height)
    vault_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 4 * (button_height + button_spacing), button_width, button_height)
    manwha_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 5 * (button_height + button_spacing), button_width, button_height)
    tutorial_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 6 * (button_height + button_spacing), button_width, button_height)
    exit_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 7 * (button_height + button_spacing), button_width, button_height)

    buttons = [
        (start_journey_button, "Start Journey", "start"),
        (story_button, "Story", "story"),
        (board_button, "Seederboard", "seederboard"),
        (hall_button, "Hall of Seeds", "hall"),
        (vault_button, "Repayment Vault", "vault"),
        (manwha_button, "Manwha", "manwha"),
        (tutorial_button, "Tutorial", "tutorial"), # Button remains, but links only to images
        (exit_button, "Exit", "exit")
    ]

    credit_font = pygame.font.SysFont("impact", 20)
    cred_text = "Made by FarmingLegendX - SuperSeed Tesla Contest"
    cred_surf = credit_font.render(cred_text, True, WHITE)
    cred_rect = cred_surf.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 10)

    while True:
        if bg_menu:
            screen.blit(bg_menu, (0, 0))
        else:
            screen.fill(GREEN)

        mouse_pos = pygame.mouse.get_pos()

        for btn_rect, btn_text, action in buttons:
            hover = btn_rect.collidepoint(mouse_pos)
            draw_plain_button(screen, btn_rect, btn_text, menu_font, button_image_path=VAULT_BUTTON_IMAGE, hover=hover)

        screen.blit(cred_surf, cred_rect)

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    play_click_sound()
                    for btn_rect, btn_text, action in buttons:
                        if btn_rect.collidepoint(mouse_pos):
                            if action == "start":
                                if os.path.exists(START_SOUND):
                                    try:
                                        if pygame.mixer.get_init():
                                            start_sound = pygame.mixer.Sound(START_SOUND)
                                            start_sound.play()
                                    except pygame.error as e:
                                        print(f"Error playing start sound: {e}")
                            return action

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_click_sound()
                    return "exit"

        pygame.time.Clock().tick(FPS)

# --- REMOVED show_tutorial FUNCTION ---

def show_tutorial_image(screen, image_path, from_menu=False):
    tutorial_img = None
    if os.path.exists(image_path):
        try:
            tutorial_img = pygame.image.load(image_path).convert()
            # Ensure aspect ratio is maintained if scaling non-fullscreen images
            img_w, img_h = tutorial_img.get_size()
            if img_w != SCREEN_WIDTH or img_h != SCREEN_HEIGHT:
                # Scale to fit screen height, maintain aspect ratio
                scale_ratio = SCREEN_HEIGHT / img_h
                new_w = int(img_w * scale_ratio)
                new_h = SCREEN_HEIGHT
                if new_w > SCREEN_WIDTH:
                    # If width exceeds screen, scale by width instead
                    scale_ratio = SCREEN_WIDTH / img_w
                    new_w = SCREEN_WIDTH
                    new_h = int(img_h * scale_ratio)

                if new_w > 0 and new_h > 0:
                     tutorial_img = pygame.transform.smoothscale(tutorial_img, (new_w, new_h))
                else:
                     tutorial_img = pygame.transform.scale(tutorial_img, (SCREEN_WIDTH, SCREEN_HEIGHT)) # Fallback if calc fails
            else:
                 tutorial_img = pygame.transform.scale(tutorial_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        except pygame.error as e:
            print(f"Error loading or scaling tutorial image {image_path}: {e}")
            tutorial_img = None
        except ValueError as e:
            print(f"Value error during tutorial image scaling {image_path}: {e}")
            tutorial_img = None


    if not tutorial_img:
        tutorial_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        tutorial_img.fill(BLACK)
        text = FONT_MD.render(f"Tutorial Image Missing: {os.path.basename(image_path)}", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        tutorial_img.blit(text, text_rect)

    img_rect = tutorial_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))


    skip_font = FONT_SM
    skip_text = skip_font.render("Press K to skip", True, WHITE)
    skip_rect = skip_text.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 30)

    waiting = True
    while waiting:
        screen.fill(BLACK) # Fill background in case image doesn't cover all
        screen.blit(tutorial_img, img_rect) # Blit centered image

        text_bg_rect = skip_rect.inflate(20, 10)
        text_bg_surf = pygame.Surface(text_bg_rect.size, pygame.SRCALPHA)
        text_bg_surf.fill((0, 0, 0, 150))
        screen.blit(text_bg_surf, text_bg_rect.topleft)
        screen.blit(skip_text, skip_rect)

        pygame.mouse.set_visible(True)

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_k:
                    play_click_sound()
                    waiting = False
                    break
                elif ev.key == pygame.K_ESCAPE and from_menu:
                    waiting = False
                    break

        pygame.time.Clock().tick(FPS)


def show_level_clear(screen, level, level_time):
    msg_text = f"Level {level} cleared in {level_time:.2f}s"
    msg_surf = FONT_MD.render(msg_text, True, GOLD)
    msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(BLACK)

    fade_duration = 0.5
    total_display_time = 1.0
    start_time = time.time()

    while time.time() - start_time < total_display_time:
        elapsed = time.time() - start_time
        alpha = 0
        if elapsed < fade_duration:
            alpha = int(255 * (elapsed / fade_duration))
        elif elapsed > total_display_time - fade_duration:
            alpha = int(255 * (1 - (elapsed - (total_display_time - fade_duration)) / fade_duration))
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        msg_surf.set_alpha(alpha)
        screen.blit(msg_surf, msg_rect)

        pygame.mouse.set_visible(True)
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)


def display_leaderboard(screen, load_scores_func, save_data):
    all_scores = load_scores_func()
    scores_to_display = all_scores[:MAX_SCORES_DISPLAY] # Limit to 20

    bg_leaderboard = None
    bg_leaderboard_darkened = None # Surface for darkened background
    if SEEDERBOARD_BACKGROUND and os.path.exists(SEEDERBOARD_BACKGROUND):
        try:
            bg_loaded = pygame.image.load(SEEDERBOARD_BACKGROUND).convert()
            bg_leaderboard = pygame.transform.scale(bg_loaded, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Create darkened version (using existing alpha value)
            bg_leaderboard_darkened = bg_leaderboard.copy()
            darken_overlay = pygame.Surface(bg_leaderboard_darkened.get_size(), pygame.SRCALPHA)
            darken_alpha = int(255 * 0.20) # 20% darkness
            darken_overlay.fill((0, 0, 0, darken_alpha))
            bg_leaderboard_darkened.blit(darken_overlay, (0,0))
        except pygame.error as e:
            print(f"Error loading seederboard background: {e}")
            bg_leaderboard_darkened = None # Ensure it's None if loading/darkening fails

    clock = pygame.time.Clock()

    # --- Use Impact fonts for leaderboard ---
    score_font_lb = FONT_LEADERBOARD_SCORE # Impact MD for score lines
    col_font_lb = FONT_LEADERBOARD_HEADER # Impact SM for column headers

    header_y = 60 # Start column headers higher up
    rank_header = col_font_lb.render("Rank", True, WHITE)
    name_header = col_font_lb.render("Name", True, WHITE)
    level_header = col_font_lb.render("Level", True, WHITE)
    time_header = col_font_lb.render("Time", True, WHITE) # Changed header text
    seeds_header = col_font_lb.render("Seeds", True, WHITE)
    avg_time_header = col_font_lb.render("Avg Time/Lvl", True, WHITE)

    # Adjust column widths if needed for Impact font
    col_width_rank = 120
    col_width_name = 400
    col_width_level = 140
    col_width_time = 180 # Keep width, format changes
    col_width_seeds = 150
    col_width_avg = 220

    total_table_width = col_width_rank + col_width_name + col_width_level + col_width_time + col_width_seeds + col_width_avg + 50
    x_start = (SCREEN_WIDTH - total_table_width) // 2

    x_rank = x_start
    x_name = x_rank + col_width_rank + 10
    x_level = x_name + col_width_name + 10
    x_time = x_level + col_width_level + 10
    x_seeds = x_time + col_width_time + 10
    x_avg_time = x_seeds + col_width_seeds + 10
    table_end_x = x_avg_time + col_width_avg

    col_line_y = header_y + col_font_lb.get_height() + 5

    score_items = []
    line_height = score_font_lb.get_height() + 10 # Use score font height
    current_y_offset = 0
    total_content_height = 0
    score_list_start_y = col_line_y + 25

    for i, (name, level, total_time, total_seeds) in enumerate(scores_to_display, 1):
        rank_str = f"{i}."
        name_str = f"{name[:15]}"
        level_str = f"{level}"
        # --- CHANGE: Format time to M:S.s ---
        minutes = int(total_time // 60)
        seconds = total_time % 60
        time_str = f"{minutes}m {seconds:.1f}s"
        # --- END CHANGE ---
        # Ensure seeds are not negative
        seeds_str = f"{max(0, total_seeds)}"
        avg_time_str = f"{(total_time / level if level > 0 else 0):.2f}"
        text_color = WHITE # Change text color to WHITE
        surfaces = [
            score_font_lb.render(rank_str, True, text_color),
            score_font_lb.render(name_str, True, text_color),
            score_font_lb.render(level_str, True, text_color),
            score_font_lb.render(time_str, True, text_color),
            score_font_lb.render(seeds_str, True, text_color),
            score_font_lb.render(avg_time_str, True, text_color)
        ]
        positions = [x_rank, x_name, x_level, x_time, x_seeds, x_avg_time]
        score_items.append({'y': current_y_offset, 'surfaces': surfaces, 'positions': positions})
        current_y_offset += line_height
        total_content_height += line_height

    scroll_offset = 0
    scroll_speed = 450
    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, 300, 50)
    scroll_area_height = back_button.top - score_list_start_y - 10
    max_scroll = max(0, total_content_height - scroll_area_height)

    leaderboard_bg_rect = pygame.Rect(x_start - 20, header_y - 10, total_table_width + 40, back_button.top - (header_y - 10) - 10 ) # Adjusted height calculation
    leaderboard_bg_surf = pygame.Surface(leaderboard_bg_rect.size, pygame.SRCALPHA)
    leaderboard_bg_surf.fill((0, 0, 0, 140)) # Darker background for leaderboard (55% opacity)

    # --- ADDED: Define separator line properties ---
    separator_color = GRAY
    separator_thickness = 1
    separator_padding = 5 # Padding above/below separator line
    # ---------------------------------------------

    waiting = True
    while waiting:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos() # Get mouse pos for hover
        scroll_change = 0
        if keys[pygame.K_UP]: scroll_change -= scroll_speed * dt
        if keys[pygame.K_DOWN]: scroll_change += scroll_speed * dt

        mouse_wheel = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m: play_click_sound(); waiting = False; break
                if event.key == pygame.K_PAGEUP: scroll_change -= scroll_area_height * 0.8
                if event.key == pygame.K_PAGEDOWN: scroll_change += scroll_area_height * 0.8
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos): play_click_sound(); waiting = False; break
                if event.button == 4: mouse_wheel = -1
                if event.button == 5: mouse_wheel = 1

        scroll_offset += scroll_change
        scroll_offset += mouse_wheel * scroll_speed * dt * 1.5
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        # Use darkened background
        if bg_leaderboard_darkened:
            screen.blit(bg_leaderboard_darkened, (0, 0))
        elif bg_leaderboard: # Fallback if darkening failed
            screen.blit(bg_leaderboard, (0,0))
        else:
            screen.fill(BLACK)

        screen.blit(leaderboard_bg_surf, leaderboard_bg_rect.topleft)

        # Draw column headers
        screen.blit(rank_header, (x_rank, header_y))
        screen.blit(name_header, (x_name, header_y))
        screen.blit(level_header, (x_level, header_y))
        screen.blit(time_header, (x_time, header_y))
        screen.blit(seeds_header, (x_seeds, header_y))
        screen.blit(avg_time_header, (x_avg_time, header_y))
        pygame.draw.line(screen, GRAY, (x_start, col_line_y), (table_end_x, col_line_y), 2)

        visible_area_top = score_list_start_y
        visible_area_bottom = back_button.top - 10

        list_clip_rect = pygame.Rect(leaderboard_bg_rect.left, score_list_start_y,
                                      leaderboard_bg_rect.width, scroll_area_height)
        screen.set_clip(list_clip_rect)

        # Draw scores relative to the screen, they will be clipped
        for item_index, item in enumerate(score_items): # Use enumerate to check if it's the last item
            y_offset = item['y']
            surfaces = item['surfaces']
            positions = item['positions']
            draw_y_on_screen = score_list_start_y + y_offset - scroll_offset
            if draw_y_on_screen + line_height > score_list_start_y and draw_y_on_screen < visible_area_bottom:
                for surf, x_pos in zip(surfaces, positions):
                    screen.blit(surf, (x_pos, draw_y_on_screen))

                # --- ADDED: Draw separator line after each score (except the last) ---
                if item_index < len(score_items) - 1: # Don't draw after the last score
                    separator_y = draw_y_on_screen + line_height - separator_padding # Position line below text
                    # Only draw if the line itself is within the visible area
                    if separator_y > score_list_start_y and separator_y < visible_area_bottom:
                         pygame.draw.line(screen, separator_color,
                                          (x_start + 5, separator_y), # Start slightly indented
                                          (table_end_x - 5, separator_y), # End slightly indented
                                          separator_thickness)
                # --------------------------------------------------------------------

        # Reset clipping area for other UI elements (like back button)
        screen.set_clip(None)

        draw_plain_button(screen, back_button, "Back to Menu", MENU_BUTTON_FONT, text_color=BLACK, bg_color=WHITE, border_color=BLACK, hover=back_button.collidepoint(mouse_pos))

        pygame.mouse.set_visible(True)
        pygame.display.flip()
        if not waiting: break


# --- UPDATED: hall_of_seeds with Locked/Unlocked Icons and Borders ---
def hall_of_seeds(screen, save_data):
    # --- Icon scaling factor ---
    icon_scale_factor = 1.10 # Increase size by 10%
    # --- Initialize icons ---
    LOCK_ICON, UNLOCKED_ICON = None, None
    lock_icon_target_height = 0
    ach_font = FONT_IMPACT_XXSM # Define ach_font early to calculate height

    if pygame.display.get_init():
        # Calculate target height based on font height and scale factor
        lock_icon_target_height = int((ach_font.get_height()) * icon_scale_factor)
    else:
        print("Warning: Display not initialized, cannot accurately scale icons in Hall of Seeds.")
        lock_icon_target_height = 20 # Fallback height

    # --- Load and Scale Lock Icon ---
    if os.path.exists(LOCK_ICON_PATH):
        try:
            icon_img = pygame.image.load(LOCK_ICON_PATH).convert_alpha()
            icon_width = int(icon_img.get_width() * (lock_icon_target_height / icon_img.get_height())) if icon_img.get_height() > 0 else lock_icon_target_height
            if icon_width > 0 and lock_icon_target_height > 0:
                LOCK_ICON = pygame.transform.smoothscale(icon_img, (icon_width, lock_icon_target_height))
            else: LOCK_ICON = None
        except Exception as e: print(f"Error loading/scaling lock icon: {e}")

    # --- Load and Scale Unlocked Icon ---
    if os.path.exists(UNLOCKED_ICON_PATH):
        try:
            icon_img = pygame.image.load(UNLOCKED_ICON_PATH).convert_alpha()
            # Use the same target height as the lock icon for consistency
            icon_width = int(icon_img.get_width() * (lock_icon_target_height / icon_img.get_height())) if icon_img.get_height() > 0 else lock_icon_target_height
            if icon_width > 0 and lock_icon_target_height > 0:
                UNLOCKED_ICON = pygame.transform.smoothscale(icon_img, (icon_width, lock_icon_target_height))
            else: UNLOCKED_ICON = None
        except Exception as e: print(f"Error loading/scaling unlocked icon: {e}")

    screen.fill(BLACK)
    clock = pygame.time.Clock()

    bg_hall = None; bg_hall_darkened = None
    if os.path.exists(HALL_OF_SEEDS_BACKGROUND):
        try:
            bg_loaded = pygame.image.load(HALL_OF_SEEDS_BACKGROUND).convert()
            bg_hall = pygame.transform.scale(bg_loaded, (SCREEN_WIDTH, SCREEN_HEIGHT))
            bg_hall_darkened = bg_hall.copy(); darken_overlay = pygame.Surface(bg_hall_darkened.get_size(), pygame.SRCALPHA)
            darken_alpha = int(255 * 0.14); darken_overlay.fill((0, 0, 0, darken_alpha)); bg_hall_darkened.blit(darken_overlay, (0,0))
        except pygame.error as e: print(f"Error loading Hall of Seeds background: {e}")

    supr_icon = None; seed_icon_hall = None; magnet_icon_hall = None
    hall_icon_base_size = (40, 40); hall_icon_display_size = (int(hall_icon_base_size[0] * 1.3), int(hall_icon_base_size[1] * 1.3))

    if os.path.exists(SUPR_TOKEN_IMAGE):
        try: supr_icon = pygame.transform.scale(pygame.image.load(SUPR_TOKEN_IMAGE).convert_alpha(), hall_icon_display_size)
        except pygame.error as e: print(f"Error loading SUPR token icon: {e}")
    if os.path.exists(SEED_IMAGE):
        try: seed_icon_hall = pygame.transform.scale(pygame.image.load(SEED_IMAGE).convert_alpha(), hall_icon_display_size)
        except pygame.error as e: print(f"Error loading seed icon for Hall: {e}")
    if os.path.exists(MAGNET_IMAGE):
        try: magnet_icon_hall = pygame.transform.scale(pygame.image.load(MAGNET_IMAGE).convert_alpha(), hall_icon_display_size)
        except pygame.error as e: print(f"Error loading magnet icon for Hall: {e}")

    info_font = FONT_IMPACT_XXXSM
    info_text_lines = ["Earn SUPR Tokens by unlocking Achievements:", "Bronze: +1 SUPR | Silver: +2 SUPR | Gold: +3 SUPR",]
    info_text_surfs = [info_font.render(line, True, GRAY) for line in info_text_lines]
    info_start_x = 50; info_start_y = 180; info_line_height = info_font.get_height() + 3; info_block_height = len(info_text_lines) * info_line_height

    stats_header_font = FONT_SM; stats_header_text = "Total Stats"; stats_header_surf = stats_header_font.render(stats_header_text, True, WHITE)
    stats_header_y = info_start_y + info_block_height + 20; stats_header_rect = stats_header_surf.get_rect(left=info_start_x, top=stats_header_y)

    supr_display_y = stats_header_rect.bottom + 15; supr_count_font = FONT_HALL_SUPR_COUNT; current_supr = save_data.get('supercollateral_coins', 0)
    token_str = "Token" if current_supr == 1 else "Tokens"; supr_text_str = f"{current_supr} SUPR {token_str}"; supr_text = supr_count_font.render(supr_text_str, True, WHITE)
    supr_icon_rect = None
    if supr_icon: icon_y_center_offset = supr_count_font.get_height() // 2; supr_icon_rect = supr_icon.get_rect(midleft=(info_start_x, supr_display_y + icon_y_center_offset)); supr_text_rect = supr_text.get_rect(midleft=(supr_icon_rect.right + 10, supr_icon_rect.centery))
    else: supr_text_rect = supr_text.get_rect(midleft=(info_start_x, supr_display_y + supr_count_font.get_height() // 2))

    total_seeds = save_data.get("total_seeds_accumulated", 0); total_magnets = save_data.get("total_magnets_collected", 0)
    stats_font = FONT_SM; stats_icon_gap = 8; stats_line_gap = 15

    seeds_display_y = supr_text_rect.bottom + stats_line_gap; seed_text_surf = stats_font.render(f"{total_seeds} Seeds Collected", True, WHITE)
    seed_icon_rect = None
    if seed_icon_hall: icon_y_center_offset_seed = stats_font.get_height() // 2; seed_icon_rect = seed_icon_hall.get_rect(midleft=(info_start_x, seeds_display_y + icon_y_center_offset_seed)); seed_text_rect = seed_text_surf.get_rect(midleft=(seed_icon_rect.right + stats_icon_gap, seed_icon_rect.centery))
    else: seed_text_rect = seed_text_surf.get_rect(midleft=(info_start_x, seeds_display_y + stats_font.get_height() // 2))

    magnets_display_y = seed_text_rect.bottom + stats_line_gap; magnet_text_surf = stats_font.render(f"{total_magnets} Magnets Collected", True, WHITE)
    magnet_icon_rect = None
    if magnet_icon_hall: icon_y_center_offset_magnet = stats_font.get_height() // 2; magnet_icon_rect = magnet_icon_hall.get_rect(midleft=(info_start_x, magnets_display_y + icon_y_center_offset_magnet)); magnet_text_rect = magnet_text_surf.get_rect(midleft=(magnet_icon_rect.right + stats_icon_gap, magnet_icon_rect.centery))
    else: magnet_text_rect = magnet_text_surf.get_rect(midleft=(info_start_x, magnets_display_y + stats_font.get_height() // 2))

    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, 300, 50)
    ach_button_height = 55; ach_list_start_y = 150; max_display_height = back_button.top - ach_list_start_y - 20

    tiered_achs = {"Gold": [], "Silver": [], "Bronze": []}; unlocked_achs = save_data.get("achievements", [])
    for ach_name in MASTER_ACHIEVEMENT_LIST:
        tier = ACHIEVEMENT_TIER_MAP.get(ach_name, "Bronze"); status = "Unlocked" if ach_name in unlocked_achs else "Locked"
        description = ACHIEVEMENT_INFO.get(ach_name, "???"); tiered_achs[tier].append((ach_name, description, status))

    ach_display_items = []; total_content_height = 0
    for tier in ["Gold", "Silver", "Bronze"]:
        if not tiered_achs[tier]: continue
        tier_color = ACHIEVEMENT_TIERS.get(tier, WHITE); tier_text_surf = FONT_MD.render(f"--- {tier} Tier ---", True, tier_color)
        tier_text_rect = tier_text_surf.get_rect(centerx=SCREEN_WIDTH // 2); item_height = tier_text_rect.height + 35
        ach_display_items.append({'surf': tier_text_surf, 'rect': tier_text_rect, 'height': item_height})
        total_content_height += item_height

        for ach_name, description, status in tiered_achs[tier]:
            is_unlocked = status == "Unlocked"; text_color = WHITE if is_unlocked else GRAY
            ach_text_str = f"{ach_name} | {description}";
            ach_surf = ach_font.render(ach_text_str, True, text_color)
            ach_rect_width = 800; ach_rect = pygame.Rect(0, 0, ach_rect_width, ach_button_height)
            ach_rect.centerx = SCREEN_WIDTH // 2; status_indicator_color = tier_color if is_unlocked else DARK_GRAY # << Color for the small box
            status_icon = UNLOCKED_ICON if is_unlocked else LOCK_ICON # << Select the correct icon

            ach_display_items.append({
                'surf': ach_surf, 'rect': ach_rect, 'height': ach_button_height + 5, 'is_button': True,
                'status_color': status_indicator_color, 'is_unlocked': is_unlocked, 'status_icon': status_icon
            })
            total_content_height += ach_button_height + 5

    scroll_offset = 0; scroll_speed = 500; waiting = True
    while waiting:
        dt = clock.tick(FPS) / 1000.0; keys = pygame.key.get_pressed(); mouse_pos = pygame.mouse.get_pos()
        scroll_change = 0
        if keys[pygame.K_UP]: scroll_change -= scroll_speed * dt
        if keys[pygame.K_DOWN]: scroll_change += scroll_speed * dt

        mouse_wheel = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m: play_click_sound(); waiting = False; break
                if event.key == pygame.K_PAGEUP: scroll_change -= max_display_height * 0.8
                if event.key == pygame.K_PAGEDOWN: scroll_change += max_display_height * 0.8
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos): play_click_sound(); waiting = False; break
                if event.button == 4: mouse_wheel = -1
                if event.button == 5: mouse_wheel = 1

        scroll_offset += scroll_change + mouse_wheel * scroll_speed * dt * 1.5
        max_scroll = max(0, total_content_height - max_display_height); scroll_offset = max(0, min(scroll_offset, max_scroll))

        if bg_hall_darkened: screen.blit(bg_hall_darkened, (0, 0))
        elif bg_hall: screen.blit(bg_hall, (0,0))
        else: screen.fill(BLACK)

        current_info_y = info_start_y; [screen.blit(surf, (info_start_x, current_info_y + i*info_line_height)) for i, surf in enumerate(info_text_surfs)]
        screen.blit(stats_header_surf, stats_header_rect)
        if supr_icon and supr_icon_rect: screen.blit(supr_icon, supr_icon_rect)
        screen.blit(supr_text, supr_text_rect)
        if seed_icon_hall and seed_icon_rect: screen.blit(seed_icon_hall, seed_icon_rect)
        screen.blit(seed_text_surf, seed_text_rect)
        if magnet_icon_hall and magnet_icon_rect: screen.blit(magnet_icon_hall, magnet_icon_rect)
        screen.blit(magnet_text_surf, magnet_text_rect)

        current_draw_y = ach_list_start_y - scroll_offset
        scroll_surface = pygame.Surface((SCREEN_WIDTH, max_display_height), pygame.SRCALPHA); scroll_surface.fill((0,0,0,0))

        for item in ach_display_items:
            item_rect = item['rect'].copy(); item_rect.top = int(current_draw_y - ach_list_start_y); item_rect.centerx = SCREEN_WIDTH // 2

            if item_rect.bottom > 0 and item_rect.top < max_display_height:
                if item.get('is_button', False):
                    # --- Draw Bordered Background ---
                    button_bg_color = (0, 0, 0, 100) # Semi-transparent black background
                    pygame.draw.rect(scroll_surface, button_bg_color, item_rect, border_radius=5)
                    pygame.draw.rect(scroll_surface, WHITE, item_rect, 1, border_radius=5) # White border

                    # --- Draw Status Box ---
                    status_box_width = 15
                    status_box_height = item_rect.height * 0.8 # Slightly smaller than button height
                    status_box_x = item_rect.left + 10
                    status_box_y = item_rect.centery - status_box_height // 2
                    status_box_rect = pygame.Rect(status_box_x, status_box_y, status_box_width, status_box_height)
                    # Background color is always black for the status box
                    pygame.draw.rect(scroll_surface, BLACK, status_box_rect, border_radius=3)
                    # Fill with tier color if unlocked, otherwise keep black
                    if item['is_unlocked']:
                        pygame.draw.rect(scroll_surface, item['status_color'], status_box_rect.inflate(-4, -4), border_radius=2) # Inner colored part
                    # --- End Status Box ---

                    text_surf = item['surf']
                    # --- Adjust text rect to make space for icon on the right AND status box on the left ---
                    text_rect = text_surf.get_rect(midleft=(status_box_rect.right + 15, item_rect.centery)) # Align text left of status box
                    scroll_surface.blit(text_surf, text_rect)

                    # --- FIX: Draw lock/unlock icon on the right side ---
                    status_icon = item.get('status_icon')
                    if status_icon:
                        # Use a fixed offset from the right edge of the button
                        icon_right_margin = 15
                        icon_rect = status_icon.get_rect(midright=(item_rect.right - icon_right_margin, item_rect.centery))
                        scroll_surface.blit(status_icon, icon_rect)
                    # --- END FIX ---

                else: # Tier Header
                    header_rect = item['rect'].copy(); header_rect.top = item_rect.top; header_rect.centerx = SCREEN_WIDTH // 2
                    scroll_surface.blit(item['surf'], header_rect)

            current_draw_y += item['height']

        screen.blit(scroll_surface, (0, ach_list_start_y))
        draw_plain_button(screen, back_button, "Back to Menu", MENU_BUTTON_FONT, text_color=BLACK, bg_color=WHITE, border_color=BLACK, hover=back_button.collidepoint(mouse_pos))
        pygame.mouse.set_visible(True); pygame.display.flip()
        if not waiting: break
# --- END UPDATE ---


# --- UPDATED: character_select with ability info ---
def character_select(screen, save_data):
    char_options = save_data.get("unlocked_characters", [1])
    char_images = save_data.get("character_images", {})
    selection_sounds = {
        1: SEEDGUY_SELECT_SOUND, 2: JOAO_SELECT_SOUND,
        3: MESKY_SELECT_SOUND, 4: CHOSEN_SELECT_SOUND
    }
    # --- NEW: Ability descriptions ---
    ability_descriptions = {
        1: "Ability: Short forward dash. (Cooldown: 6s)",
        2: "Ability: Speed boost for 5s. (Cooldown: 30s)",
        3: "Ability: Slow nearby enemies for 5s. (Cooldown: 30s)", # Note: Functionality will be updated elsewhere
        4: "Ability: Become immune to damage for 5s. (Cooldown: 45s)", # Updated Cooldown
    }
    desc_font = FONT_IMPACT_XXXSM # Font for descriptions
    # --- END NEW ---

    bg_char_select = None
    if os.path.exists(CHARACTER_SELECT_BACKGROUND):
        try:
            bg_char_select = pygame.image.load(CHARACTER_SELECT_BACKGROUND).convert()
            bg_char_select = pygame.transform.scale(bg_char_select, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e: print(f"Error loading character select background: {e}")

    num_chars = len(char_options)
    size_multiplier = 1.3
    base_box_width = int(250 * size_multiplier)
    box_height = int(350 * size_multiplier)
    box_spacing = int(20 * size_multiplier)

    total_width = num_chars * base_box_width + (num_chars - 1) * box_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = (SCREEN_HEIGHT - box_height) // 2 + 30

    char_rects = {}
    char_display_elements = []

    for i, char_index in enumerate(char_options):
        x = start_x + i * (base_box_width + box_spacing)
        rect = pygame.Rect(x, y_pos, base_box_width, box_height)
        char_rects[char_index] = rect

        display_img_name = os.path.basename(char_images.get(str(char_index), SEEDGUY_DISPLAY_IMAGE))
        display_img_path = os.path.join(ASSETS_DIR, display_img_name)
        char_img = None
        img_draw_rect = None
        if os.path.exists(display_img_path):
            try:
                loaded_img = pygame.image.load(display_img_path).convert_alpha()
                orig_w, orig_h = loaded_img.get_size()

                image_scale_increase = 1.9602
                padding = 10 # Box padding remains the same
                max_img_w = (rect.width - 2 * padding) * image_scale_increase # Use the new factor
                max_img_h = (rect.height - 2 * padding - 30) * image_scale_increase # Use the new factor

                img_ratio = orig_w / orig_h if orig_h > 0 else 1

                final_h = max_img_h
                final_w = final_h * img_ratio
                if final_w > max_img_w:
                    final_w = max_img_w
                    final_h = final_w / img_ratio if img_ratio > 0 else max_img_h

                if final_w > 0 and final_h > 0:
                     char_img = pygame.transform.smoothscale(loaded_img, (int(final_w), int(final_h)))
                     img_draw_rect = char_img.get_rect(center=rect.center) # Center enlarged image in box

            except pygame.error as e: print(f"Error loading/scaling character image {display_img_path}: {e}")
            except ValueError as e: print(f"Error during image processing {display_img_path}: {e}")

        char_display_elements.append({'index': char_index, 'image': char_img, 'draw_rect': img_draw_rect, 'button_rect': rect})

    selected_char_index = -1
    confirm_button_width = 250
    confirm_button_height = 60
    confirm_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - confirm_button_width // 2, SCREEN_HEIGHT - 100, confirm_button_width, confirm_button_height)

    # --- NEW: Variable for description ---
    current_description_surf = None
    current_description_rect = None
    # --- END NEW ---

    while True:
        if bg_char_select: screen.blit(bg_char_select, (0, 0))
        else: screen.fill(BLACK)

        mouse_pos = pygame.mouse.get_pos()

        # --- NEW: Reset description each frame ---
        current_description_surf = None
        current_description_rect = None
        # --- END NEW ---

        for element in char_display_elements:
            rect = element['button_rect']
            is_selected = element['index'] == selected_char_index
            is_hovered = rect.collidepoint(mouse_pos)

            # Draw box border/background
            border_color = GOLD if is_selected else (WHITE if is_hovered else DARK_GRAY)
            border_thickness = 3 if is_selected else 2 # Thicker border when selected
            bg_color = (70, 70, 70, 180) if is_selected else (50, 50, 50, 150)

            bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            bg_surf.fill(bg_color)
            screen.blit(bg_surf, rect.topleft)
            pygame.draw.rect(screen, border_color, rect, border_thickness)

            # Draw the enlarged image
            if element['image'] and element['draw_rect']:
                screen.blit(element['image'], element['draw_rect'])
            else:
                fallback_text = FONT_SM.render(f"Character {element['index']}", True, WHITE)
                fallback_rect = fallback_text.get_rect(center=element['button_rect'].center)
                screen.blit(fallback_text, fallback_rect)

            # --- NEW: Prepare description if selected ---
            if is_selected:
                desc_text = ability_descriptions.get(element['index'], "No ability info.")
                current_description_surf = desc_font.render(desc_text, True, WHITE)
                # Position below the selected box
                current_description_rect = current_description_surf.get_rect(centerx=rect.centerx, top=rect.bottom + 10)
            # --- END NEW ---

        # --- NEW: Draw description if prepared ---
        if current_description_surf and current_description_rect:
            # Draw a semi-transparent background behind the description
            desc_bg_rect = current_description_rect.inflate(10, 5)
            desc_bg_surf = pygame.Surface(desc_bg_rect.size, pygame.SRCALPHA)
            desc_bg_surf.fill((0, 0, 0, 150))
            screen.blit(desc_bg_surf, desc_bg_rect.topleft)
            screen.blit(current_description_surf, current_description_rect)
        # --- END NEW ---

        if selected_char_index != -1:
             draw_plain_button(screen, confirm_button_rect, "Confirm", MENU_BUTTON_FONT, text_color=BLACK, bg_color=WHITE, border_color=BLACK, hover=confirm_button_rect.collidepoint(mouse_pos))

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                clicked_on_char = False
                for char_index, rect in char_rects.items():
                    if rect.collidepoint(mx, my):
                        play_click_sound()
                        selected_char_index = char_index
                        clicked_on_char = True
                        sound_path = selection_sounds.get(selected_char_index)
                        if sound_path and os.path.exists(sound_path):
                           try:
                               if pygame.mixer.get_init():
                                   sound_obj = pygame.mixer.Sound(sound_path)
                                   if selected_char_index == 3: # If Mesky
                                       sound_obj.set_volume(1.0) # Set volume to max (or adjust as needed)
                                       print(f"Playing Mesky sound ({sound_path}) with increased volume.")
                                   else:
                                       sound_obj.set_volume(0.7) # Default volume for others
                                   sound_obj.play()
                           except pygame.error as e: print(f"Error playing selection sound {sound_path}: {e}")
                        break
                if selected_char_index != -1 and confirm_button_rect.collidepoint(mx,my):
                     play_click_sound()
                     return selected_char_index
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: play_click_sound(); return None

        pygame.time.Clock().tick(FPS)
# --- END UPDATE ---


def announce_mini_game(screen, minigame_name, rewards):
    screen.fill(BLACK)

    title_font = FONT_LG
    info_font = FONT_SM

    title_surf = title_font.render("Mini-Game Incoming!", True, GOLD)
    title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=SCREEN_HEIGHT // 2 - 100)

    name_surf = info_font.render(f"{minigame_name}", True, WHITE)
    name_rect = name_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=title_rect.bottom + 20)

    rewards_surf = info_font.render(f"{rewards}", True, SILVER) # Use rewards string directly
    rewards_rect = rewards_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=name_rect.bottom + 10)

    screen.blit(title_surf, title_rect)
    screen.blit(name_surf, name_rect)
    screen.blit(rewards_surf, rewards_rect)

    pygame.mouse.set_visible(True)

    pygame.display.flip()
    pygame.time.wait(3000)


# --- UPDATED: repayment_vault_shop with adjusted button height ---
def repayment_vault_shop(screen, save_data):
    vault = save_data.get("vault_upgrades", {})
    shop_font = VAULT_SHOP_BUTTON_FONT # Uses FONT_IMPACT_XXXSM now (via settings.py)
    cost_font = VAULT_COST_FONT # Uses FONT_IMPACT_XXXSM now (via settings.py)

    bg_vault = None
    bg_vault_darkened = None # Surface for darkened background
    if os.path.exists(REPAYMENT_VAULT_BACKGROUND):
        try:
            bg_loaded = pygame.image.load(REPAYMENT_VAULT_BACKGROUND).convert()
            bg_vault = pygame.transform.scale(bg_loaded, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Darken background slightly more (14% -> 19%)
            bg_vault_darkened = bg_vault.copy()
            darken_overlay = pygame.Surface(bg_vault_darkened.get_size(), pygame.SRCALPHA)
            darken_alpha = int(255 * 0.19) # 19% darkness (was 14%)
            darken_overlay.fill((0, 0, 0, darken_alpha))
            bg_vault_darkened.blit(darken_overlay, (0,0))
        except pygame.error as e:
            print(f"Error loading Repayment Vault background: {e}")
            bg_vault_darkened = None # Ensure it's None if loading/darkening fails

    base_button_width = 950
    base_button_height = 68
    button_width = int(base_button_width * 0.75) # Keep 25% smaller width
    button_height = int(base_button_height * 0.95) + 1 # Net +1px height from original
    button_spacing = 15
    scc_display_height = FONT_LG.get_height() + 60

    # SUPR Display remains on the left
    supr_y_center = SCREEN_HEIGHT // 2
    supr_x = 50

    # Explanation text setup (moved to left)
    persist_lines = [
        "Vault upgrades are permanent",
        "and persist after death.",
        "",
        "Earn SUPR through Achievements:", # Updated currency
        "(View in Hall of Seeds)",
        "",
        "Bronze: +1 SUPR", # Updated currency
        "Silver: +2 SUPR", # Updated currency
        "Gold:   +3 SUPR" # Updated currency
    ]
    persist_font = FONT_IMPACT_XXXSM
    explanation_max_width = 0
    rendered_explanation_lines = []
    line_height_exp = persist_font.get_height() + 3
    total_exp_height = 0
    for line in persist_lines:
        persist_text = persist_font.render(line, True, WHITE) # White text for explanation
        explanation_max_width = max(explanation_max_width, persist_text.get_width())
        rendered_explanation_lines.append(persist_text)
        total_exp_height += line_height_exp

    # Position explanation block below SUPR display on the left
    explanation_x = supr_x
    explanation_start_y = supr_y_center + scc_display_height // 2 + 40 # Below SUPR display

    # Explanation Background Box
    exp_bg_width = explanation_max_width + 30
    exp_bg_height = total_exp_height + 15
    exp_bg_rect = pygame.Rect(explanation_x - 15, explanation_start_y - 7, exp_bg_width, exp_bg_height)
    exp_bg_surf = pygame.Surface(exp_bg_rect.size, pygame.SRCALPHA)
    exp_bg_surf.fill((0, 0, 0, 100)) # Semi-transparent black background

    # Use existing Y start position for buttons, shifted slightly
    upgrade_buttons_start_y = 200 + 20 + 20
    options_center_x = SCREEN_WIDTH // 2 + 100 - 10 # Keep buttons shifted left

    options_data = [
        ("node_speed_boost", "Node Speed Boost: Lvl {}/{} | +4% Base Speed per Lvl", VAULT_COST_NODE_SPEED, "node_speed_boost"),
        ("extra_life", "Respawn Node: Lvl {}/{} | +1 Max Checkpoint at Start", VAULT_COST_EXTRA_LIFE, "extra_life"),
        ("seed_multiplier", "SeedFi Powerhouse: {} | Seeds collected count as 2x", VAULT_COST_MULTIPLIER, "seed_multiplier"),
        ("seed_radius", "Pick up Lines: Lvl {}/{} | +5px pickup radius per Lvl", lambda v: VAULT_COST_RADIUS_BASE + v.get("seed_radius", 0) * VAULT_COST_RADIUS_INCREMENT, "seed_radius"),
        ("cooldown_reduction", "2Chairs 1 Goal: {} | Reduce ability cooldown by 20%", VAULT_COST_COOLDOWN, "cooldown_reduction"),
        ("starting_shield", "Joao's Loophole: {} | Begin each run with a shield", VAULT_COST_SHIELD, "starting_shield"),
        ("enemy_slow_aura", "Mesky's Anger: Lvl {}/{} | Slow nearby enemies by 7% per Lvl", VAULT_COST_AURA, "enemy_slow_aura"),
        ("blessing_superseed", "Blessing of Superseed: {} | Increase power-up chance (+10%)", VAULT_COST_BLESSING, "blessing_superseed")
    ]

    option_rects = []
    current_button_y = upgrade_buttons_start_y
    for i in range(len(options_data)):
        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (options_center_x, current_button_y + button_height // 2)
        option_rects.append(rect)
        current_button_y += button_height + button_spacing

    close_btn_width = 250 # Reduced from 300
    close_btn_height = 45 # Reduced from 50
    close_btn = pygame.Rect(0, 0, close_btn_width, close_btn_height)
    close_btn.center = (options_center_x, current_button_y + 40) # Position below the last calculated button Y

    while True:
        # Use darkened background
        if bg_vault_darkened:
            screen.blit(bg_vault_darkened, (0,0))
        elif bg_vault: # Fallback if darkening failed
             screen.blit(bg_vault, (0,0))
        else:
            screen.fill(BLACK)

        mouse_pos = pygame.mouse.get_pos()
        current_supr = save_data.get("supercollateral_coins", 0) # Keep internal key

        # SUPR Display (Stays on Left)
        supr_icon_obj = None
        coin_icon_vault_size = (int(60 * 1.2), int(60 * 1.2))
        icon_rect = None
        if os.path.exists(SUPR_TOKEN_IMAGE):
             try:
                  supr_icon_obj = pygame.image.load(SUPR_TOKEN_IMAGE).convert_alpha() # Load SUPR image
                  supr_icon_obj = pygame.transform.scale(supr_icon_obj, coin_icon_vault_size)
                  icon_rect = supr_icon_obj.get_rect(midleft=(supr_x, supr_y_center))
                  screen.blit(supr_icon_obj, icon_rect) # Blit the SUPR icon
             except pygame.error as e: print(f"Error loading SUPR token image: {e}")

        supr_text_surf = FONT_LG.render(f"{current_supr} SUPR", True, WHITE) # Display SUPR
        text_x_pos = icon_rect.right + 15 if icon_rect else supr_x
        supr_text_rect = supr_text_surf.get_rect(midleft=(text_x_pos, supr_y_center))
        screen.blit(supr_text_surf, supr_text_rect)

        # Draw Explanation Text and Background on Left
        screen.blit(exp_bg_surf, exp_bg_rect.topleft)
        current_exp_y = explanation_start_y
        for text_surf in rendered_explanation_lines:
            # Position text relative to the explanation area's top-left
            text_rect = text_surf.get_rect(left=explanation_x, top=current_exp_y)
            screen.blit(text_surf, text_rect)
            current_exp_y += line_height_exp


        # Upgrade Buttons (Moved Down and Right)
        for i, (key, text_format, cost_data, max_level_key) in enumerate(options_data):
            rect = option_rects[i] # Use the pre-calculated smaller rect
            current_level = vault.get(key, 0)
            max_level = VAULT_MAX_LEVELS.get(max_level_key, 1)

            cost = 0
            if current_level < max_level:
                if callable(cost_data): cost = cost_data(vault)
                else: cost = cost_data

            can_afford = current_supr >= cost
            is_maxed = current_level >= max_level

            main_text_part = ""
            desc_parts = text_format.split("|")
            base_desc = desc_parts[0].strip()
            effect_desc = desc_parts[1].strip() if len(desc_parts) > 1 else ""

            if max_level > 1: main_text_part = base_desc.format(current_level, max_level)
            else: status = "Owned" if is_maxed else "Available"; main_text_part = base_desc.format(status)

            full_main_text = f"{main_text_part}" # Start with the main part
            if effect_desc: # Add effect description below if it exists
                full_effect_text = f"{effect_desc}"
            else:
                full_effect_text = ""


            cost_text_part = ""; cost_text_color = BLACK
            if is_maxed: cost_text_part = "(MAX)"; cost_text_color = GRAY
            elif cost > 0: cost_text_part = f"Cost: {cost} SUPR"; # Updated currency
            if not can_afford and not is_maxed: cost_text_color = RED

            button_image_to_use = VAULT_BUTTON_IMAGE
            hovering_button = rect.collidepoint(mouse_pos) and not is_maxed
            draw_plain_button(screen, rect, "", shop_font, button_image_path=button_image_to_use, hover=hovering_button)

            # --- Draw main text and effect text separately ---
            main_text_surf = shop_font.render(full_main_text, True, BLACK)
            # Adjust Y position slightly up to make space for effect text
            main_text_rect = main_text_surf.get_rect(center=(rect.centerx, rect.centery - 12))
            screen.blit(main_text_surf, main_text_rect)

            # Draw Effect text part below main text
            if full_effect_text:
                effect_text_surf = cost_font.render(full_effect_text, True, DARK_GRAY) # Use cost font size, grey color
                effect_text_rect = effect_text_surf.get_rect(center=(rect.centerx, main_text_rect.bottom + 8)) # Below main text
                screen.blit(effect_text_surf, effect_text_rect)

            # Draw Cost text part (aligned to the right, below effect text or main text if no effect)
            cost_text_surf = cost_font.render(cost_text_part, True, cost_text_color) if cost_text_part else None
            if cost_text_surf:
                cost_text_rect = cost_text_surf.get_rect(midright=(rect.right - 80, rect.centery)) # Keep adjusted horizontal alignment
                screen.blit(cost_text_surf, cost_text_rect)

            if is_maxed:
                 overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
                 overlay.fill((100, 100, 100, 150))
                 screen.blit(overlay, rect.topleft) # Apply overlay to original rect position

        # Draw Close Button (Moved Down)
        draw_plain_button(screen, close_btn, "Close Vault", VAULT_CLOSE_BUTTON_FONT, text_color=BLACK, bg_color=WHITE, border_color=BLACK, hover=close_btn.collidepoint(mouse_pos))

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return
            elif ev.type == pygame.KEYDOWN:
                 if ev.key == pygame.K_ESCAPE: play_click_sound(); return
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if close_btn.collidepoint(ev.pos): play_click_sound(); return
                for i, (key, _, cost_data, max_level_key) in enumerate(options_data):
                    rect = option_rects[i]
                    if rect.collidepoint(ev.pos):
                        current_level = vault.get(key, 0)
                        max_level = VAULT_MAX_LEVELS.get(max_level_key, 1)
                        if current_level < max_level:
                            cost = 0
                            if callable(cost_data): cost = cost_data(vault)
                            else: cost = cost_data
                            if current_supr >= cost:
                                play_click_sound()
                                save_data["supercollateral_coins"] = current_supr - cost # Keep internal key
                                vault[key] = current_level + 1
                                current_supr = save_data["supercollateral_coins"] # Update local variable
                                # Immediately update vault reference for cost calculations like radius
                                save_data["vault_upgrades"] = vault
                        break
        pygame.time.Clock().tick(FPS)
# --- END UPDATE ---


def show_ingame_shop_overlay(screen, seed_count, current_level, shop_upgrades, player_upgrades, checkpoint_count):
    overlay_rect = screen.get_rect()

    shop_bg = None
    shop_bg_darkened = None # Surface for darkened background
    if SHOP_BACKGROUND and os.path.exists(SHOP_BACKGROUND):
        try:
            shop_bg_loaded = pygame.image.load(SHOP_BACKGROUND).convert()
            shop_bg = pygame.transform.scale(shop_bg_loaded, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Darken Merchant background more (15% -> 25%)
            shop_bg_darkened = shop_bg.copy()
            darken_overlay = pygame.Surface(shop_bg_darkened.get_size(), pygame.SRCALPHA)
            darken_alpha = int(255 * 0.25) # 25% darkness (was 15%)
            darken_overlay.fill((0, 0, 0, darken_alpha))
            shop_bg_darkened.blit(darken_overlay, (0,0))

        except pygame.error as e:
            print(f"Error loading shop overlay background: {e}")

    shop_font = BUTTON_FONT
    info_font = FONT_LG # Using FONT_LG for larger seed display text
    cost_font = FONT_IMPACT_XSM
    desc_font = FONT_IMPACT_XXXSM

    button_width = 1000
    base_button_height = 70
    button_height = int(base_button_height * 1.20)
    button_spacing = 20
    num_options = 5

    buttons_start_y = SCREEN_HEIGHT // 2 - (num_options * (button_height + button_spacing) // 2) + 50 # Start near center, offset down slightly

    option_keys = ["speed", "seed_enemy", "shield", "enemy_slow", "checkpoint"]
    option_rects = []
    current_button_y = buttons_start_y
    button_center_x = SCREEN_WIDTH // 2
    for i in range(len(option_keys)):
         rect = pygame.Rect(0, 0, button_width, button_height)
         rect.center = (button_center_x, current_button_y + button_height // 2)
         option_rects.append(rect)
         current_button_y += button_height + button_spacing

    close_button = pygame.Rect(0, 0, 300, 50)
    close_button.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)

    clock = pygame.time.Clock()
    shop_looping = True

    mixer_ok = pygame.mixer.get_init()
    was_music_playing = False
    if mixer_ok:
        was_music_playing = pygame.mixer.music.get_busy()

    while shop_looping:
        mouse_pos = pygame.mouse.get_pos()

        # Use darkened background
        if shop_bg_darkened:
            screen.blit(shop_bg_darkened, (0, 0))
        elif shop_bg: # Fallback to original if darkening failed
             screen.blit(shop_bg, (0, 0))
        else: screen.fill(BLACK)

        # Seed Display (Top-Right, Larger)
        seed_icon_obj = None
        seed_icon_rect = None
        seed_disp_x = SCREEN_WIDTH - 350 # Adjusted X position for wider block (was 250)
        seed_disp_y = 80 # Y position (upper half)

        if os.path.exists(SEED_IMAGE):
            try:
                 seed_icon_img_orig = pygame.image.load(SEED_IMAGE).convert_alpha()
                 seed_icon_size_base = ORIGINAL_SEED_BASE_SIZE * SEED_SIZE_MULTIPLIER
                 seed_icon_display_scale_factor = 1.40 # 40% larger
                 seed_icon_size = (int(seed_icon_size_base * seed_icon_display_scale_factor), int(seed_icon_size_base * seed_icon_display_scale_factor))

                 if seed_icon_size[0] > 0 and seed_icon_size[1] > 0:
                    seed_icon_obj = pygame.transform.smoothscale(seed_icon_img_orig, seed_icon_size) # Use smoothscale
                    # Position icon first
                    icon_y_centered = seed_disp_y + (info_font.get_height() // 2) - (seed_icon_size[1] // 2)
                    seed_icon_rect = seed_icon_obj.get_rect(topleft=(seed_disp_x, icon_y_centered))
                    screen.blit(seed_icon_obj, seed_icon_rect)
                 else:
                    seed_icon_obj = None # Failed scale
                    print(f"Warning: Calculated seed icon size is invalid in shop: {seed_icon_size}")
            except Exception as e: print(f"Error loading/scaling seed icon in shop: {e}")

        # Position text next to the icon (using larger info_font)
        current_disp = info_font.render(f"Seeds: {seed_count}", True, WHITE)
        text_start_x = seed_icon_rect.right + 15 if seed_icon_rect and seed_icon_obj else seed_disp_x # Increased gap
        disp_rect = current_disp.get_rect(midleft=(text_start_x , seed_disp_y + info_font.get_height() // 2))
        screen.blit(current_disp, disp_rect)


        # Calculate costs (logic remains the same, factor changed in settings)
        base_speed_level = 0
        shop_speed_level = shop_upgrades.get("speed", 0)
        cost_speed = (shop_speed_level + 1) * SHOP_SPEED_COST_FACTOR
        cost_seed_enemy = (shop_upgrades.get("seed_enemy", 0) + 1) * SHOP_SEED_ENEMY_COST_FACTOR if shop_upgrades.get("seed_enemy", 0) < SHOP_SEED_ENEMY_MAX_LEVEL else None
        cost_shield = SHOP_SHIELD_COST_LOW if current_level < SHOP_SHIELD_LEVEL_THRESHOLD else SHOP_SHIELD_COST_HIGH
        cost_slow = 0
        if current_level < SHOP_SLOW_LEVEL_THRESH1: cost_slow = SHOP_SLOW_COST_LOW
        elif current_level < SHOP_SLOW_LEVEL_THRESH2: cost_slow = SHOP_SLOW_COST_MID
        else: cost_slow = SHOP_SLOW_COST_HIGH
        cost_checkpoint = SHOP_CHECKPOINT_COST

        costs = {
            "speed": cost_speed, "seed_enemy": cost_seed_enemy, "shield": cost_shield,
            "enemy_slow": cost_slow, "checkpoint": cost_checkpoint
        }

        # --- CHANGE: Update Speed description AND Seed/Enemy description ---
        descriptions = {
            "speed": "+5% Max Speed / +2% Enemy Speed per level", # Updated speed description
            "seed_enemy": "+2 Seeds Dropped & +1 Enemy Spawn per level", # Updated seed/enemy description
            "shield": "Provides a one-hit shield (lost on use)",
            "enemy_slow": "Slows enemies by 5% per level",
            "checkpoint": "Grants one extra checkpoint use this run"
        }
        # --- END CHANGE ---

        # Draw Shop Buttons (position determined by buttons_start_y)
        for i, key in enumerate(option_keys):
            rect = option_rects[i]
            cost = costs[key]
            is_maxed = (key == "seed_enemy" and cost is None) or \
                       (key == "shield" and player_upgrades.get('shield', 0) > 0)
            can_afford = cost is not None and seed_count >= cost

            main_text = ""; cost_text_str = ""; cost_text_color = BLACK
            desc_text = descriptions.get(key, "")

            if key == "speed": main_text = f"Speed Upgrade: Lvl {shop_speed_level}"; cost_text_str = f"Cost: {cost_speed} Seeds"
            elif key == "seed_enemy": main_text = f"Seed/Enemy: Lvl {shop_upgrades.get('seed_enemy', 0)}/{SHOP_SEED_ENEMY_MAX_LEVEL}"; cost_text_str = f"Cost: {cost_seed_enemy} Seeds" if cost_seed_enemy is not None else "(MAX)"
            elif key == "shield": main_text = f"Purchase Shield: {'Owned' if player_upgrades.get('shield', 0) > 0 else 'Available'}"; cost_text_str = f"Cost: {cost_shield} Seeds" if not is_maxed else "(Owned)"
            elif key == "enemy_slow": main_text = f"Enemy Slow: Lvl {shop_upgrades.get('enemy_slow', 0)}"; cost_text_str = f"Cost: {cost_slow} Seeds"
            elif key == "checkpoint": main_text = "Purchase Checkpoint Use"; cost_text_str = f"Cost: {cost_checkpoint} Seeds"

            if not is_maxed and not can_afford and cost is not None: cost_text_color = RED
            if is_maxed: cost_text_color = GRAY

            # Hover effect for shop buttons
            hovering_shop_button = rect.collidepoint(mouse_pos) and not is_maxed
            # Use draw_plain_button for background/image and hover scaling
            draw_plain_button(screen, rect, "", shop_font, button_image_path=VAULT_BUTTON_IMAGE, hover=hovering_shop_button)

            # --- Centering text in shop buttons ---
            main_surf = shop_font.render(main_text, True, BLACK)
            desc_surf = desc_font.render(desc_text, True, DARK_GRAY)
            cost_surf = cost_font.render(cost_text_str, True, cost_text_color) if cost_text_str else None

            # Calculate total height required by text elements
            total_text_block_height = main_surf.get_height() + desc_surf.get_height() + 5 # Gap between desc and main
            # Calculate starting Y position to center the block vertically within the *original* rect
            start_text_y = rect.centery - total_text_block_height // 2

            # Position Main Text (centered horizontally in original rect)
            main_rect = main_surf.get_rect(centerx=rect.centerx, top=start_text_y)
            screen.blit(main_surf, main_rect)

            # Position Description Text below Main Text (centered horizontally in original rect)
            desc_rect = desc_surf.get_rect(centerx=rect.centerx, top=main_rect.bottom + 5)
            screen.blit(desc_surf, desc_rect)

            # Position Cost Text (aligned right within original rect)
            if cost_surf:
                cost_rect = cost_surf.get_rect(midright=(rect.right - 70, rect.centery)) # Increased offset from 55 to 70
                screen.blit(cost_surf, cost_rect)

            if is_maxed:
                 overlay = pygame.Surface(rect.size, pygame.SRCALPHA); overlay.fill((100, 100, 100, 100)); screen.blit(overlay, rect.topleft) # Apply to original rect

        # Draw Close Button
        draw_plain_button(screen, close_button, "Close Shop", MENU_BUTTON_FONT, text_color=BLACK, bg_color=WHITE, border_color=BLACK, hover=close_button.collidepoint(mouse_pos))

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return "exit", seed_count, checkpoint_count, shop_upgrades, player_upgrades
            elif ev.type == pygame.KEYDOWN:
                 if ev.key == pygame.K_ESCAPE or ev.key == pygame.K_p: play_click_sound(); return "close", seed_count, checkpoint_count, shop_upgrades, player_upgrades
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if close_button.collidepoint(ev.pos): play_click_sound(); return "close", seed_count, checkpoint_count, shop_upgrades, player_upgrades
                for i, key in enumerate(option_keys):
                     rect = option_rects[i]
                     if rect.collidepoint(ev.pos):
                          cost = costs[key]
                          is_maxed = (key == "seed_enemy" and cost is None) or \
                                     (key == "shield" and player_upgrades.get('shield', 0) > 0)
                          if not is_maxed and cost is not None and seed_count >= cost:
                               play_click_sound(); seed_count -= cost
                               if key == "speed": shop_upgrades["speed"] = shop_upgrades.get("speed", 0) + 1
                               elif key == "seed_enemy": shop_upgrades["seed_enemy"] = shop_upgrades.get("seed_enemy", 0) + 1
                               elif key == "shield": player_upgrades["shield"] = 1
                               elif key == "enemy_slow": shop_upgrades["enemy_slow"] = shop_upgrades.get("enemy_slow", 0) + 1
                               elif key == "checkpoint": checkpoint_count += 1
                          break
        clock.tick(FPS)


def pause_menu(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    pause_font = FONT_LG
    resume_text = "P: Resume"
    menu_text = "M: Main Menu"

    resume_surf = pause_font.render(resume_text, True, WHITE)
    menu_surf = pause_font.render(menu_text, True, WHITE)

    resume_rect = resume_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    menu_rect = menu_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

    screen.blit(resume_surf, resume_rect)
    screen.blit(menu_surf, menu_rect)

    pygame.mouse.set_visible(True)

    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.KEYDOWN:
                play_click_sound()
                if event.key == pygame.K_p:
                    return "resume"
                if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                    return "menu"

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        pygame.time.Clock().tick(30)


def show_game_over(screen, level_reached, total_time, total_seeds_collected_run): # Changed signature
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        if os.path.exists(DEAD_SOUND):
            try: pygame.mixer.Sound(DEAD_SOUND).play()
            except pygame.error as e: print(f"Error playing dead sound: {e}")

    game_over_bg = None
    if os.path.exists(GAMEOVER_IMAGE):
        try:
            game_over_bg = pygame.image.load(GAMEOVER_IMAGE).convert()
            game_over_bg = pygame.transform.scale(game_over_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading game over background: {e}")

    if game_over_bg:
        screen.blit(game_over_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0,0))
    else:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

    stats_font = FONT_SM
    stats_y = SCREEN_HEIGHT // 4 # Start stats higher up since title is gone
    stats_lines = [
        f"You reached Level: {level_reached}", # Use passed argument
        f"Total Time: {total_time:.2f}s",
        f"Seeds Collected this run: {total_seeds_collected_run}"
    ]
    rendered_stats_surfs = []
    for line in stats_lines:
        line_surf = stats_font.render(line, True, WHITE)
        line_rect = line_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=stats_y)
        rendered_stats_surfs.append((line_surf, line_rect))
        stats_y += stats_font.get_height() + 10

    input_prompt = FONT_SM.render("Enter Name & Press S to Save Score:", True, WHITE)
    prompt_rect = input_prompt.get_rect(centerx=SCREEN_WIDTH // 2, top=stats_y + 60)

    input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, prompt_rect.bottom + 15, 400, 50)
    input_name = ""
    input_active = True

    while True:
        if game_over_bg:
            screen.blit(game_over_bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0,0))
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))

        # Draw stats
        current_stats_y = SCREEN_HEIGHT // 4 # Reset Y pos for drawing
        for surf, rect in rendered_stats_surfs:
             rect.top = current_stats_y # Update Y position for drawing
             screen.blit(surf, rect)
             current_stats_y += stats_font.get_height() + 10

        # Draw input prompt below stats
        prompt_rect.top = current_stats_y + 60
        screen.blit(input_prompt, prompt_rect)

        # Draw input box below prompt
        input_box_rect.top = prompt_rect.bottom + 15

        box_color = GOLD if input_active else WHITE
        pygame.draw.rect(screen, box_color, input_box_rect)
        pygame.draw.rect(screen, BLACK, input_box_rect, 2)

        name_surf = FONT_SM.render(input_name, True, BLACK)
        name_rect = name_surf.get_rect(midleft=(input_box_rect.x + 10, input_box_rect.centery))
        screen.blit(name_surf, name_rect)

        if input_active and time.time() % 1 < 0.5:
            cursor_x = name_rect.right + 2
            cursor_x = min(cursor_x, input_box_rect.right - 5)
            cursor_y = name_rect.top; cursor_height = name_rect.height
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return "Player" # Return default if quit
            if ev.type == pygame.KEYDOWN:
                if input_active:
                    if ev.key == pygame.K_RETURN or ev.key == pygame.K_s:
                        play_click_sound(); input_active = False
                        return input_name.strip() if input_name.strip() else "Player"
                    elif ev.key == pygame.K_BACKSPACE: input_name = input_name[:-1]
                    elif len(input_name) < 15:
                         # Allow letters, numbers, and spaces
                         if ev.unicode.isalnum() or ev.unicode == ' ':
                             input_name += ev.unicode
            if ev.type == pygame.MOUSEBUTTONDOWN:
                 input_active = input_box_rect.collidepoint(ev.pos)

        pygame.time.Clock().tick(FPS)

# --- NEW: Function for WIN screen ---
def show_win_screen(screen, total_time, total_seeds_collected_run):
    """Displays the game win screen and handles score submission."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        # Optionally play a win sound here
        # if os.path.exists(WIN_SOUND): # Define WIN_SOUND in settings if needed
        #     try: pygame.mixer.Sound(WIN_SOUND).play()
        #     except pygame.error as e: print(f"Error playing win sound: {e}")

    win_screen_bg = None
    if os.path.exists(ENDSCREEN_IMAGE): # Use the endscreen image path
        try:
            win_screen_bg = pygame.image.load(ENDSCREEN_IMAGE).convert()
            win_screen_bg = pygame.transform.scale(win_screen_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading win screen background (endscreen.png): {e}")

    if win_screen_bg:
        screen.blit(win_screen_bg, (0, 0))
        # Optionally add a darker overlay if the background is too bright
        # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # overlay.fill((0, 0, 0, 70)) # Slight darkening
        # screen.blit(overlay, (0,0))
    else:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 220)) # Dark blue fallback
        screen.blit(overlay, (0, 0))

    # Win Message Text
    win_font = FONT_SM # Use a readable font
    line_height = win_font.get_height() + 5
    win_lines = [
        "Congratulations, you have reached the Mainnet!",
        "Your Superseed powers have returned!",
        "Next step: TGE! Share your scores on X",
        "to show your friends who's the real Superseed expert!"
    ]
    max_text_width = 0
    rendered_win_lines = []
    for line in win_lines:
        surf = win_font.render(line, True, GOLD) # Gold text
        rendered_win_lines.append(surf)
        max_text_width = max(max_text_width, surf.get_width())

    total_text_height = len(win_lines) * line_height
    win_text_y_start = SCREEN_HEIGHT // 2 - total_text_height // 2 - 100 # Position text block

    # Stats Display (Similar to Game Over)
    stats_font = FONT_SM
    stats_y_start = win_text_y_start + total_text_height + 40 # Below win text
    stats_lines = [
        f"Final Level: {MAX_LEVEL}", # Assuming MAX_LEVEL is the win level
        f"Total Time: {total_time:.2f}s",
        f"Seeds Collected: {total_seeds_collected_run}"
    ]
    rendered_stats_surfs = []
    for line in stats_lines:
        line_surf = stats_font.render(line, True, WHITE)
        line_rect = line_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=stats_y_start)
        rendered_stats_surfs.append((line_surf, line_rect))
        stats_y_start += stats_font.get_height() + 10

    input_prompt = FONT_SM.render("Enter Name & Press S to Save Score:", True, WHITE)
    prompt_rect = input_prompt.get_rect(centerx=SCREEN_WIDTH // 2, top=stats_y_start + 40)

    input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, prompt_rect.bottom + 15, 400, 50)
    input_name = ""
    input_active = True

    while True:
        # Redraw background and overlay each frame
        if win_screen_bg:
            screen.blit(win_screen_bg, (0, 0))
            # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # overlay.fill((0, 0, 0, 70))
            # screen.blit(overlay, (0,0))
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 50, 220))
            screen.blit(overlay, (0, 0))

        # Draw win text
        current_win_y = win_text_y_start
        for surf in rendered_win_lines:
            rect = surf.get_rect(centerx=SCREEN_WIDTH // 2, top=current_win_y)
            screen.blit(surf, rect)
            current_win_y += line_height

        # Draw stats
        current_stats_y = win_text_y_start + total_text_height + 40 # Reset Y pos
        for surf, rect in rendered_stats_surfs:
             rect.top = current_stats_y # Update Y position for drawing
             screen.blit(surf, rect)
             current_stats_y += stats_font.get_height() + 10

        # Draw input prompt below stats
        prompt_rect.top = current_stats_y + 40
        screen.blit(input_prompt, prompt_rect)

        # Draw input box below prompt
        input_box_rect.top = prompt_rect.bottom + 15

        box_color = GOLD if input_active else WHITE
        pygame.draw.rect(screen, box_color, input_box_rect)
        pygame.draw.rect(screen, BLACK, input_box_rect, 2)

        name_surf = FONT_SM.render(input_name, True, BLACK)
        name_rect = name_surf.get_rect(midleft=(input_box_rect.x + 10, input_box_rect.centery))
        screen.blit(name_surf, name_rect)

        if input_active and time.time() % 1 < 0.5:
            cursor_x = name_rect.right + 2
            cursor_x = min(cursor_x, input_box_rect.right - 5)
            cursor_y = name_rect.top; cursor_height = name_rect.height
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

        pygame.mouse.set_visible(True)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return "Player" # Return default if quit
            if ev.type == pygame.KEYDOWN:
                if input_active:
                    if ev.key == pygame.K_RETURN or ev.key == pygame.K_s:
                        play_click_sound(); input_active = False
                        return input_name.strip() if input_name.strip() else "Player"
                    elif ev.key == pygame.K_BACKSPACE: input_name = input_name[:-1]
                    elif len(input_name) < 15:
                         if ev.unicode.isalnum() or ev.unicode == ' ':
                             input_name += ev.unicode
                elif ev.key == pygame.K_ESCAPE: # Allow Esc to exit after saving
                    play_click_sound()
                    return input_name.strip() if input_name.strip() else "Player"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                 input_active = input_box_rect.collidepoint(ev.pos)

        pygame.time.Clock().tick(FPS)
# --- END NEW ---


# --- Manwha Viewer Function ---
def show_manwha_reader(screen):
    clock = pygame.time.Clock()
    manwha_images = []
    for img_path in MANWHA_IMAGES:
        if os.path.exists(img_path):
            try:
                img = pygame.image.load(img_path).convert()
                # Scale manwha image to fit screen dimensions
                img_w, img_h = img.get_size()

                scaled_img = img
                scaled_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                if img_w > 0 and img_h > 0:
                    # Try scaling based on height first
                    ratio_h = SCREEN_HEIGHT / img_h
                    scaled_w_if_h = img_w * ratio_h
                    scaled_h_if_h = SCREEN_HEIGHT

                    # Try scaling based on width
                    ratio_w = SCREEN_WIDTH / img_w
                    scaled_w_if_w = SCREEN_WIDTH
                    scaled_h_if_w = img_h * ratio_w

                    target_w, target_h = img_w, img_h # Default to original

                    # Prioritize fitting height unless it makes width too large
                    if scaled_w_if_h <= SCREEN_WIDTH:
                        target_w, target_h = int(scaled_w_if_h), int(scaled_h_if_h)
                    # Otherwise (if scaling by height is too wide), scale by width
                    elif scaled_h_if_w <= SCREEN_HEIGHT:
                        target_w, target_h = int(scaled_w_if_w), int(scaled_h_if_w)
                    # As a fallback (e.g., very wide image), just fit to width
                    else:
                         target_w, target_h = int(scaled_w_if_w), int(scaled_h_if_w)


                    if target_w > 0 and target_h > 0 and (target_w != img_w or target_h != img_h):
                         scaled_img = pygame.transform.smoothscale(img, (target_w, target_h))
                         scaled_rect = scaled_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    else: # Use original if scaling not needed or failed
                         scaled_img = img
                         scaled_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                manwha_images.append({'image': scaled_img, 'rect': scaled_rect})

            except Exception as e:
                print(f"Error loading/scaling manwha image {img_path}: {e}")
                # Add a placeholder if loading fails
                placeholder_surf = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                placeholder_surf.fill(DARK_GRAY)
                font = FONT_SM
                text = font.render(f"Error: {os.path.basename(img_path)}", True, RED)
                rect = text.get_rect(center=placeholder_surf.get_rect().center)
                placeholder_surf.blit(text, rect)
                placeholder_rect = placeholder_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                manwha_images.append({'image': placeholder_surf, 'rect': placeholder_rect})
        else:
             print(f"Manwha image not found: {img_path}") # Keep this warning
             placeholder_surf = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
             placeholder_surf.fill(DARK_GRAY)
             font = FONT_SM
             text = font.render(f"Missing: {os.path.basename(img_path)}", True, RED)
             rect = text.get_rect(center=placeholder_surf.get_rect().center)
             placeholder_surf.blit(text, rect)
             placeholder_rect = placeholder_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
             manwha_images.append({'image': placeholder_surf, 'rect': placeholder_rect})


    bg_manwha = None
    if os.path.exists(MANWHA_BG_IMAGE):
        try:
            bg_manwha = pygame.image.load(MANWHA_BG_IMAGE).convert()
            bg_manwha = pygame.transform.scale(bg_manwha, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading Manwha background: {e}")

    current_index = 0
    num_images = len(manwha_images)
    if num_images == 0:
        print("No manwha images loaded. Returning to menu.")
        return # Exit if no images could be loaded

    arrow_size = 80
    arrow_padding = 30
    # Simple arrow buttons for now
    left_arrow_rect = pygame.Rect(arrow_padding, SCREEN_HEIGHT // 2 - arrow_size // 2, arrow_size, arrow_size)
    right_arrow_rect = pygame.Rect(SCREEN_WIDTH - arrow_padding - arrow_size, SCREEN_HEIGHT // 2 - arrow_size // 2, arrow_size, arrow_size)

    # Transition state variables
    transitioning = False
    transition_progress = 0.0 # 0 to 1
    transition_speed = 2.0 # Higher value = faster transition
    next_index = current_index

    waiting = True
    while waiting:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k or event.key == pygame.K_ESCAPE:
                    play_click_sound(); waiting = False; break
                if not transitioning:
                    if event.key == pygame.K_LEFT and current_index > 0:
                        play_click_sound(); next_index = current_index - 1; transitioning = True; transition_progress = 0.0
                    elif event.key == pygame.K_RIGHT and current_index < num_images - 1:
                        play_click_sound(); next_index = current_index + 1; transitioning = True; transition_progress = 0.0
            if event.type == pygame.MOUSEBUTTONDOWN:
                 if not transitioning:
                     if left_arrow_rect.collidepoint(mouse_pos) and current_index > 0:
                         play_click_sound(); next_index = current_index - 1; transitioning = True; transition_progress = 0.0
                     elif right_arrow_rect.collidepoint(mouse_pos) and current_index < num_images - 1:
                         play_click_sound(); next_index = current_index + 1; transitioning = True; transition_progress = 0.0


        # Draw Background
        if bg_manwha:
            screen.blit(bg_manwha, (0, 0))
        else:
            screen.fill(BLACK)

        # Get current and next images/rects
        current_data = manwha_images[current_index]
        next_data = manwha_images[next_index] if transitioning else current_data # Use next_index only during transition

        current_img = current_data['image']
        current_img_rect = current_data['rect']
        next_img = next_data['image']
        next_img_rect = next_data['rect']


        # Handle transition
        if transitioning:
            transition_progress += transition_speed * dt
            if transition_progress >= 1.0:
                transition_progress = 1.0
                transitioning = False
                current_index = next_index # Complete the transition

            # Simple Fade Transition
            alpha = int(255 * transition_progress)
            current_img.set_alpha(255 - alpha)
            next_img.set_alpha(alpha)

            screen.blit(current_img, current_img_rect)
            screen.blit(next_img, next_img_rect)

        else:
            # Ensure alpha is correct when not transitioning
            current_img.set_alpha(255)
            screen.blit(current_img, current_img_rect)

        # Draw Arrows (only if not transitioning and applicable)
        if not transitioning:
            arrow_color = WHITE
            arrow_hover_color = GOLD
            # Left Arrow
            if current_index > 0:
                left_color = arrow_hover_color if left_arrow_rect.collidepoint(mouse_pos) else arrow_color
                pygame.draw.polygon(screen, left_color, [
                    (left_arrow_rect.left, left_arrow_rect.centery),
                    (left_arrow_rect.right, left_arrow_rect.top),
                    (left_arrow_rect.right, left_arrow_rect.bottom)
                ])
            # Right Arrow
            if current_index < num_images - 1:
                right_color = arrow_hover_color if right_arrow_rect.collidepoint(mouse_pos) else arrow_color
                pygame.draw.polygon(screen, right_color, [
                    (right_arrow_rect.right, right_arrow_rect.centery),
                    (right_arrow_rect.left, right_arrow_rect.top),
                    (right_arrow_rect.left, right_arrow_rect.bottom)
                ])

        # Move Exit Prompt to Left
        prompt_font = FONT_SM
        prompt_text = prompt_font.render("Press K to return", True, WHITE)
        # Position based on left edge + padding
        prompt_rect = prompt_text.get_rect(left=arrow_padding, bottom=SCREEN_HEIGHT - 30)
        # Draw background behind text
        text_bg_rect = prompt_rect.inflate(20, 10);
        text_bg_surf = pygame.Surface(text_bg_rect.size, pygame.SRCALPHA);
        text_bg_surf.fill((0,0,0,150));
        screen.blit(text_bg_surf, text_bg_rect)
        screen.blit(prompt_text, prompt_rect)

        pygame.mouse.set_visible(True)
        pygame.display.flip()
        if not waiting: break


# --- NEW: Function to draw Seed Doubler Timer ---
def draw_seed_doubler_timer(surface, remaining_time):
    """Draws the seed doubler timer onto the provided surface."""
    if remaining_time <= 0:
        return

    timer_font = FONT_SM # Use small impact font
    text = f"Double Seeds: {remaining_time:.1f}s"

    # Pulsating alpha effect
    pulse_freq = 4.0 # Faster pulse than shield
    pulse_alpha = abs(math.sin(time.time() * pulse_freq))
    alpha = int(150 + 105 * pulse_alpha) # Strong but varying alpha

    color = (220, 60, 60, alpha) # Reddish color with alpha

    text_surf = timer_font.render(text, True, WHITE) # Render text in white first
    text_surf.set_alpha(alpha) # Apply alpha to the text surface
    text_rect = text_surf.get_rect(topleft=(0, 0)) # Position relative to surface

    # Draw a subtle background onto the surface
    bg_rect = text_rect.inflate(10, 5)
    # Ensure surface is large enough for the inflated rect
    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surf.fill((color[0], color[1], color[2], int(alpha * 0.5))) # Background uses half alpha
    surface.blit(bg_surf, bg_rect.topleft) # Blit background onto surface

    surface.blit(text_surf, text_rect) # Blit text onto surface

# --- END NEW ---

# --- NEW: Function for Screen Flash ---
def draw_screen_flash(screen, duration=0.1, color=WHITE, alpha=180):
    """Draws a temporary screen flash overlay. Should be called within the main loop."""
    # Note: This function is intended to set flags or timers that the main
    # drawing loop checks. It doesn't handle the drawing itself over time.
    # The actual drawing logic is in run_level using level_screen_flash_timer.
    print("Warning: draw_screen_flash function called directly. Integrate into main loop drawing.")
    # Example of how it *could* work if integrated:
    # Set a global or passed-in timer variable:
    # global_flash_timer = duration
    # global_flash_color = color
    # global_flash_alpha = alpha

# --- Function to draw world transition screen ---
# --- UPDATED: show_world_transition with colors ---
def show_world_transition(screen, next_world_name):
    """Displays a simple screen announcing the next world with world-specific color."""
    # --- Get world color ---
    # Need level number, but we only have name. Let's map name back to a representative level.
    level_map = {
        "Earth World": 1, "Fire World": 11, "Water World": 21, "Frost World": 31,
        "Underworld": 51, "Desert World": 61, "Jungle World": 71, "Space World": 81,
        "Cyber World": 91, "Mystic World (Inverse Controls)": 91, "Superseed World": 95
    }
    representative_level = 1
    for name, lvl in level_map.items():
        if name == next_world_name:
            representative_level = lvl
            break
    world_color = get_scene_color(representative_level) # Use the function defined in this file
    # --- End Get world color ---

    transition_text = FONT_LG.render(f"Entering: {next_world_name}", True, world_color) # Use world color
    screen.fill(BLACK)
    screen.blit(transition_text, transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    pygame.mouse.set_visible(True); pygame.display.flip(); pygame.time.wait(2500)