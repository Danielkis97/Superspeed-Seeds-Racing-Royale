# --- START OF FILE game_objects.py ---

import pygame, os, math, random, time # Import time module
from settings import *

SPRITE_SHEET_CACHE = {}
ABILITY_ICON_CACHE = {}
ABILITY_ANIMATION_CACHE = {} # --- NEW: Cache for ability animations ---


def load_image(path, size):
    try:
        size = (int(size[0]), int(size[1]))
        if size[0] <= 0 or size[1] <= 0:
            print(f"Warning: Attempted to load image {path} with non-positive size {size}. Using 1x1 fallback.")
            size = (1, 1)
    except (IndexError, TypeError):
        print(f"Warning: Invalid size {size} for image {path}. Using 1x1 fallback.")
        size = (1,1)

    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
        except ValueError as e:
            # Add more context to value errors, often related to size
            print(f"Error scaling image {path} to size {size}: {e}. Check image integrity and size parameters.")
    # Fallback surface creation if loading/scaling fails or path doesn't exist
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(GRAY) # Grey background for visibility
    if size[0] > 1 and size[1] > 1:
        try:
            # Draw red 'X' to indicate missing/failed image
            pygame.draw.line(surface, RED, (0, 0), (size[0]-1, size[1]-1), 2)
            pygame.draw.line(surface, RED, (0, size[1]-1), (size[0]-1, 0), 2)
        except pygame.error: # Ignore drawing errors on tiny surfaces
            pass
    return surface

# --- UPDATED: load_sprite_frames with enhanced auto-detection and logging ---
def load_sprite_frames(path, frame_width, frame_height, scale=1.0, is_enemy=False):
    """
    Loads frames from a sprite sheet.
    If frame_width/height is 0 and is_enemy is True, attempts auto-detection
    based on common enemy sprite sheet conventions (single row, 3-12 frames).
    Scales the individual frames.
    If frame_width/height > 0, uses those dimensions explicitly.
    If frame_width/height is 0 and is_enemy is False, treats as single image.
    """
    frames = []
    target_w = int(frame_width * scale) if frame_width > 0 else 0
    target_h = int(frame_height * scale) if frame_height > 0 else 0

    if not os.path.exists(path):
        print(f"Sprite sheet not found: {path}")
        # Use target_w/h if calculated, otherwise fallback to a small default
        fallback_size = (max(1, target_w) if target_w > 0 else 32, max(1, target_h) if target_h > 0 else 32)
        return [load_image(path, fallback_size)]

    cache_key = (path, frame_width, frame_height, scale, is_enemy)
    if cache_key in SPRITE_SHEET_CACHE:
        # print(f"Using cached frames for {os.path.basename(path)}") # Debug cache hit
        return SPRITE_SHEET_CACHE[cache_key]

    try:
        sheet = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading sprite sheet {path}: {e}")
        fallback_size = (max(1, target_w) if target_w > 0 else 32, max(1, target_h) if target_h > 0 else 32)
        return [load_image(path, fallback_size)]

    sheet_rect = sheet.get_rect()
    sheet_w, sheet_h = sheet_rect.size

    effective_frame_width = frame_width
    effective_frame_height = frame_height
    auto_detected = False
    is_single_frame = False

    # --- Determine Effective Frame Size ---
    if frame_width > 0 and frame_height > 0:
        # Explicit dimensions provided - use them
        effective_frame_width = frame_width
        effective_frame_height = frame_height
        # Target size is based on scaling these explicit dimensions
        target_w = int(effective_frame_width * scale)
        target_h = int(effective_frame_height * scale)
        #print(f"Using explicit frame size {effective_frame_width}x{effective_frame_height} for {os.path.basename(path)}. Scaling to {target_w}x{target_h}") # Reduce console spam

    elif frame_width <= 0 and frame_height <= 0 and is_enemy:
        # Auto-detection logic for enemies
        #print(f"Attempting auto-detection for enemy sprite: {os.path.basename(path)}") # Reduce console spam
        min_frames, max_frames = 3, 12
        min_dim, max_dim = 16, 1024 # Increased max_dim for David's large sheet
        possible_frame_counts = range(max_frames, min_frames - 1, -1)
        for num_frames in possible_frame_counts:
            if sheet_w > 0 and sheet_w % num_frames == 0: # Check for clean division & positive width
                potential_fw = sheet_w / num_frames
                potential_fh = sheet_h # Assume single row
                if min_dim <= potential_fw <= max_dim and min_dim <= potential_fh <= max_dim:
                    effective_frame_width = int(potential_fw)
                    effective_frame_height = int(potential_fh)
                    target_w = int(effective_frame_width * scale)
                    target_h = int(effective_frame_height * scale)
                    auto_detected = True
                    #print(f"--> Auto-detected enemy frames for {os.path.basename(path)}: {num_frames} frames of size {effective_frame_width}x{effective_frame_height}. Scaling to {target_w}x{target_h}") # Reduce console spam
                    break
        if not auto_detected:
            #print(f"--> Warning: Could not auto-detect enemy frames for {path}. Treating as single frame {sheet_w}x{sheet_h}.") # Reduce console spam
            effective_frame_width = sheet_w; effective_frame_height = sheet_h
            target_w = int(effective_frame_width * scale); target_h = int(effective_frame_height * scale)
            is_single_frame = True

    else: # Not enemy auto-detect, and no explicit size -> treat as single frame
        #print(f"Treating {os.path.basename(path)} as single frame {sheet_w}x{sheet_h}.") # Reduce console spam
        effective_frame_width = sheet_w; effective_frame_height = sheet_h
        # Target size needs to be based on scaling the *whole sheet*
        target_w = int(effective_frame_width * scale)
        target_h = int(effective_frame_height * scale)
        is_single_frame = True
    # --- End Determine Effective Frame Size ---

    # Ensure positive dimensions
    target_w = max(1, target_w); target_h = max(1, target_h)
    if effective_frame_width <= 0 or effective_frame_height <= 0:
        print(f"Error: Calculated effective frame size is invalid ({effective_frame_width}x{effective_frame_height}) for {path}. Using fallback.")
        return [load_image(path, (target_w, target_h))]

    # --- Extract Frames ---
    if is_single_frame:
        # If it's a single frame, just scale the whole sheet
        try:
            scaled_frame = pygame.transform.scale(sheet, (target_w, target_h))
            frames.append(scaled_frame)
        except (ValueError, pygame.error) as e:
            print(f"Error scaling single frame {path}: {e}")
            frames.append(load_image(path, (target_w, target_h))) # Fallback
    else:
        # Extract multiple frames
        cols = sheet_w // effective_frame_width
        rows = sheet_h // effective_frame_height
        #print(f"Extracting frames for {os.path.basename(path)}: Grid={cols}x{rows}, Frame={effective_frame_width}x{effective_frame_height}, Target={target_w}x{target_h}") # Reduce console spam
        for row in range(rows):
            for col in range(cols):
                frame_rect_on_sheet = pygame.Rect(col * effective_frame_width, row * effective_frame_height, effective_frame_width, effective_frame_height)
                if sheet_rect.contains(frame_rect_on_sheet):
                    try:
                        frame = sheet.subsurface(frame_rect_on_sheet)
                        scaled_frame = pygame.transform.scale(frame, (target_w, target_h))
                        frames.append(scaled_frame)
                    except (ValueError, pygame.error) as e:
                        print(f"Error extracting/scaling frame at ({col},{row}) from {path}: {e}")
                        continue
                else:
                    print(f"Warning: Calculated frame rect {frame_rect_on_sheet} outside bounds of sheet {path} {sheet_rect}. Skipping.")
    # --- End Extract Frames ---

    if not frames:
        print(f"Warning: No frames extracted/created for {path}. Using scaled sheet fallback.")
        frames.append(pygame.transform.scale(sheet, (target_w, target_h)))

    SPRITE_SHEET_CACHE[cache_key] = frames # Cache the result
    return frames
# --- END UPDATE ---


# --- NEW: Function to load and cache ability animation images ---
def load_ability_animation(path):
    if path in ABILITY_ANIMATION_CACHE:
        return ABILITY_ANIMATION_CACHE[path]
    if not os.path.exists(path):
        print(f"Ability animation image not found: {path}")
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        ABILITY_ANIMATION_CACHE[path] = img
        return img
    except pygame.error as e:
        print(f"Error loading ability animation image {path}: {e}")
        return None
# --- END NEW ---


def get_player_pod_image_path(character_index):
    mapping = {
        1: PLAYER_POD1_IMAGE, 2: PLAYER_POD2_IMAGE,
        3: PLAYER_POD3_IMAGE, 4: PLAYER_POD4_IMAGE
    }
    return mapping.get(character_index, PLAYER_POD1_IMAGE)


# --- UPDATED: AbilityEffect Class ---
class AbilityEffect(pygame.sprite.Sprite):
    # --- FIX: Adjusted constructor parameters for size factor ---
    def __init__(self, center_pos, image_path, player_size, lifetime=ABILITY_EFFECT_DURATION, fade_start_time=0.0, initial_scale=1.0, end_scale=1.0, base_size_factor=ABILITY_ANIMATION_SIZE_FACTOR): # Added base_size_factor
        super().__init__()
        self.original_image = load_ability_animation(image_path)
        self.player_size = player_size # Store player size for scaling
        self.initial_scale = initial_scale
        self.end_scale = end_scale
        self.lifetime = lifetime
        self.fade_start_time = max(0, min(fade_start_time, lifetime)) # Clamp fade start time
        self.spawn_time = time.time()
        self.pos_x = float(center_pos[0]) # Store position
        self.pos_y = float(center_pos[1])
        self.base_size_factor = base_size_factor # Store the base size factor

        # Initial image setup
        if self.original_image:
            base_w, base_h = player_size
            # Use base_size_factor here
            target_width = max(1, int(base_w * self.base_size_factor * self.initial_scale))
            target_height = max(1, int(base_h * self.base_size_factor * self.initial_scale))
            try:
                self.image = pygame.transform.smoothscale(self.original_image, (target_width, target_height))
            except (pygame.error, ValueError) as e:
                print(f"Error scaling initial ability effect: {e}")
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA); self.image.fill((255, 0, 255, 100))
        else:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA); self.image.fill((255, 0, 255, 100))
            print(f"Warning: Using placeholder for missing ability effect image: {image_path}")

        self.rect = self.image.get_rect(center=center_pos)
    # --- END FIX ---

    def update(self, dt, player): # << Added player argument
        elapsed_time = time.time() - self.spawn_time
        if elapsed_time >= self.lifetime:
            self.kill()
            return

        # --- Movement: Follow the player ---
        self.pos_x = player.pos_x
        self.pos_y = player.pos_y
        # --- End Movement ---

        # --- Scaling ---
        scale_progress = min(elapsed_time / self.lifetime, 1.0)
        current_scale_factor = self.initial_scale + (self.end_scale - self.initial_scale) * scale_progress
        base_w, base_h = self.player_size
        # --- FIX: Use base_size_factor in scaling update ---
        new_width = max(1, int(base_w * self.base_size_factor * current_scale_factor))
        new_height = max(1, int(base_h * self.base_size_factor * current_scale_factor))
        # --- END FIX ---

        # --- Alpha Fade ---
        alpha = 255
        fade_duration = self.lifetime - self.fade_start_time
        if elapsed_time >= self.fade_start_time and fade_duration > 0:
            fade_progress = (elapsed_time - self.fade_start_time) / fade_duration
            alpha = int(255 * (1.0 - fade_progress))
        elif elapsed_time >= self.fade_start_time: # Handle zero duration fade
             alpha = 0
        alpha = max(0, min(255, alpha)) # Clamp alpha

        # --- Apply Scale and Alpha ---
        if self.original_image:
            try:
                if new_width > 0 and new_height > 0:
                    scaled_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
                else: scaled_image = self.original_image.copy()
                scaled_image.set_alpha(alpha)
                self.image = scaled_image
                self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y))) # Update rect center based on player pos
            except (pygame.error, ValueError) as e: self.kill()
        else:
            current_alpha = self.image.get_alpha()
            if current_alpha is None: current_alpha = 255
            if int(alpha) != current_alpha: self.image.set_alpha(int(alpha))
            self.rect.center = (int(self.pos_x), int(self.pos_y)) # Update rect center based on player pos
# --- END UPDATE ---


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character=1):
        super().__init__()
        self.character = character
        player_image_path = get_player_pod_image_path(self.character)

        self.base_width = int(ORIGINAL_PLAYER_BASE_WIDTH * PLAYER_CUMULATIVE_SIZE_INCREASE)
        self.base_height = int(ORIGINAL_PLAYER_BASE_HEIGHT * PLAYER_CUMULATIVE_SIZE_INCREASE)
        self.size = (self.base_width, self.base_height)

        self.original_image = load_image(player_image_path, self.size)
        initial_rect = self.original_image.get_rect(center=(x, y))

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.angle = 270.0 # Start facing down (Movement angle)
        self.visual_angle = 270.0 # Visual angle starts facing down

        self.vel_x = 0.0 # Velocity x
        self.vel_y = 0.0 # Velocity y
        self.speed = 0.0 # Current magnitude of velocity (for compatibility)
        self.friction = PLAYER_FRICTION # Use adjusted friction from settings

        self.base_max_speed = BASE_PLAYER_MAX_SPEED
        self.base_acceleration = BASE_PLAYER_ACCEL
        self.rotation_speed = PLAYER_ROT_SPEED

        self.max_speed = self.base_max_speed
        self.acceleration = self.base_acceleration

        self.invincible_until = 0.0
        self.temp_shield_end_time = 0.0 # Added to track shield powerup duration

        self.trail = []
        self.base_trail_length = TRAIL_LENGTH
        self.trail_length = self.base_trail_length
        self.trail_intensity_multiplier = 1.0 # For Joao's speed boost
        self.trail_segment_size = 10 # Default size

        self.last_ability = -float('inf') # Initialize to allow immediate use
        self.ability_active = False
        self.ability_start_time = 0.0
        self.base_cooldown = self.get_base_cooldown()
        self.cooldown = self.base_cooldown
        self.ability_duration = self.get_ability_duration()
        self.ability_activated_this_frame = False
        self.ability_effects = pygame.sprite.Group()
        self.particle_group_ref = None # This will be set by main.py
        self.is_brightened = False

        self.upgrades = {"shield": 0}

        self.vault_speed_boost_mult = 1.0
        self.vault_cooldown_reduction = 1.0
        self.vault_pickup_radius_bonus = 0

        self.ability_icon = self.load_ability_icon()

        # --- FIX: Set correct initial rotation (assuming base sprite faces DOWN) ---
        initial_rotation_value = 0 # No initial rotation needed if base image faces down
        try:
            self.image = pygame.transform.rotate(self.original_image, initial_rotation_value)
            self.rect = self.image.get_rect(center=initial_rect.center)
        except pygame.error as e:
            print(f"Error rotating initial player image: {e}")
            self.image = self.original_image.copy() # Use unrotated original
            self.rect = self.original_image.get_rect(center=initial_rect.center)
        # --- END FIX ---

        self.radius = ((self.rect.width + self.rect.height) / 2) * 0.4

        self.bounce_timer = 0.0
        self.bounce_offset = 0

    def load_ability_icon(self):
        icon_path = ABILITY_ICONS.get(self.character)
        if not icon_path: print(f"Warning: No ability icon path defined for character {self.character}"); return None
        if icon_path in ABILITY_ICON_CACHE:
             cached_icon = ABILITY_ICON_CACHE[icon_path]
             if cached_icon and cached_icon.get_width() > 1 and cached_icon.get_height() > 1: return cached_icon
        try:
            temp_icon = pygame.image.load(icon_path).convert_alpha()
            if temp_icon.get_width() <= 1 or temp_icon.get_height() <= 1: raise ValueError("Loaded icon image is invalid (<= 1 pixel)")
            icon_size = (30, 30)
            icon_image = pygame.transform.smoothscale(temp_icon, icon_size)
            ABILITY_ICON_CACHE[icon_path] = icon_image
            return icon_image
        except (pygame.error, ValueError, FileNotFoundError) as e: print(f"Error loading/processing ability icon {icon_path}: {e}")
        except Exception as e: print(f"Unexpected error loading ability icon {icon_path}: {e}")
        fallback_surf = pygame.Surface((30, 30), pygame.SRCALPHA); fallback_surf.fill(GRAY); pygame.draw.line(fallback_surf, RED, (0,0), (29,29), 2); pygame.draw.line(fallback_surf, RED, (0,29), (29,0), 2)
        ABILITY_ICON_CACHE[icon_path] = fallback_surf
        return fallback_surf


    def apply_vault_upgrades(self, vault_upgrades):
        speed_boost_level = vault_upgrades.get("node_speed_boost", 0)
        self.vault_speed_boost_mult = 1.0 + (speed_boost_level * 0.04)
        cooldown_level = vault_upgrades.get("cooldown_reduction", 0)
        self.vault_cooldown_reduction = 0.8 if cooldown_level >= 1 else 1.0
        radius_level = vault_upgrades.get("seed_radius", 0)
        self.vault_pickup_radius_bonus = radius_level * 5
        self.update_effective_stats({})

    def get_base_cooldown(self):
        if self.character == 1: return SEEDGUY_COOLDOWN
        elif self.character == 2: return JOAO_COOLDOWN
        elif self.character == 3: return MESKY_COOLDOWN
        elif self.character == 4: return CHOSEN_SEED_COOLDOWN
        else: return 999

    def get_ability_duration(self):
        if self.character == 1: return 0 # Dash is instant
        elif self.character == 2: return JOAO_DURATION
        elif self.character == 3: return MESKY_DURATION
        elif self.character == 4: return CHOSEN_SEED_DURATION
        else: return 0

    def update_effective_stats(self, shop_upgrades, weather="clear"):
        self.max_speed = self.base_max_speed * self.vault_speed_boost_mult
        self.acceleration = self.base_acceleration
        self.cooldown = self.base_cooldown * self.vault_cooldown_reduction

        shop_speed_level = shop_upgrades.get("speed", 0)
        self.max_speed += self.base_max_speed * (shop_speed_level * 0.05)

        weather_accel_mult = 1.0
        if weather == "rain": weather_accel_mult = 0.8
        elif weather == "snow": weather_accel_mult = 0.5

        self.acceleration = self.base_acceleration * weather_accel_mult

        self.trail_intensity_multiplier = 1.0 # Reset trail multiplier
        self.is_brightened = False # Reset brightness flag

        if self.character == 2 and self.ability_active: # Joao's speed boost
            self.max_speed *= 1.5 # Boost max speed
            self.acceleration *= 1.5 # Boost acceleration
            self.trail_intensity_multiplier = 1.5 # Make trail longer/stronger
            self.is_brightened = True # Mark for brightness change

        self.trail_length = int(self.base_trail_length * self.trail_intensity_multiplier) # Update trail length

    def update(self, keys, current_time, weather, shop_upgrades, inverse=False, wind_direction=None, player_ref=None, dt=1/FPS):
        if dt <= 0: return
        self.ability_activated_this_frame = False # Reset flag at start of update

        if keys[pygame.K_SPACE] and not self.ability_active and current_time - self.last_ability >= self.cooldown:
             self.activate_ability(current_time, player_ref) # Attempt to activate
             self.ability_activated_this_frame = True # Set flag

        if self.ability_active and self.ability_duration > 0 and \
           current_time - self.ability_start_time >= self.ability_duration:
            self.ability_active = False
            self.update_effective_stats(shop_upgrades, weather) # Re-calculate stats when ability ends
            if self.character == 4:
                 # --- FIX: Use SHIELD_BREAK_INVINCIBILITY instead of self.ability_duration ---
                 # Check if invincibility was granted by ability activation
                 # We can't know for sure if it was *just* ability, but ability is the only thing setting self.ability_start_time
                 # If invincibility is ending roughly when the ability *would* have ended, remove it.
                 # Using a small epsilon for floating point comparison.
                 if abs(self.invincible_until - (self.ability_start_time + CHOSEN_SEED_DURATION)) < 0.1:
                     self.invincible_until = 0.0 # Reset only if it matches ability end time
                 # --- END FIX ---


        self.update_effective_stats(shop_upgrades, weather)

        rotate_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        rotate_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        accelerate_input = keys[pygame.K_UP] or keys[pygame.K_w]
        decelerate_input = keys[pygame.K_DOWN] or keys[pygame.K_s]

        if inverse:
             rotate_left, rotate_right = rotate_right, rotate_left
             accelerate_input, decelerate_input = decelerate_input, accelerate_input

        # --- Rotation ---
        rotation_change = 0.0
        if rotate_left: rotation_change += self.rotation_speed * dt
        if rotate_right: rotation_change -= self.rotation_speed * dt
        self.angle = (self.angle + rotation_change) % 360 # This is the MOVEMENT angle

        # --- Acceleration based on input AND current angle ---
        rad = math.radians(self.angle)
        forward_x = math.cos(rad)
        forward_y = -math.sin(rad) # Pygame Y is inverted

        target_accel = 0.0
        if accelerate_input:
            target_accel = self.acceleration
        elif decelerate_input:
            vel_mag = math.hypot(self.vel_x, self.vel_y)
            if vel_mag > 5.0: # If moving significantly, brake against velocity
                brake_x = -self.vel_x / vel_mag * self.acceleration * 1.5
                brake_y = -self.vel_y / vel_mag * self.acceleration * 1.5
                self.vel_x += brake_x * dt
                self.vel_y += brake_y * dt
            else: # If moving slowly or stopped, reverse
                 target_accel = -self.acceleration * 0.7 # Slower reverse

        # Apply forward/reverse acceleration
        self.vel_x += target_accel * forward_x * dt
        self.vel_y += target_accel * forward_y * dt

        # --- Apply Friction ---
        friction_factor = math.pow(self.friction, 60 * dt) # Scale friction by dt
        self.vel_x *= friction_factor
        self.vel_y *= friction_factor

        # --- Apply Wind ---
        if weather == "wind":
            if wind_direction is None: wind_direction = random.choice([-1, 1])
            wind_force_magnitude = self.max_speed * 0.40 # Wind strength relative to max speed
            self.vel_x += wind_force_magnitude * wind_direction * dt # Wind only affects X

        # --- Limit Speed ---
        current_speed_sq = self.vel_x**2 + self.vel_y**2
        max_speed_val = self.max_speed
        max_speed_sq = max_speed_val**2

        if current_speed_sq > max_speed_sq and max_speed_sq > 0: # Avoid division by zero if max_speed is 0
            scale_factor = math.sqrt(max_speed_sq / current_speed_sq)
            self.vel_x *= scale_factor
            self.vel_y *= scale_factor

        # --- Update Position ---
        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt

        # --- Boundary Collision ---
        effective_radius = ((self.base_width + self.base_height) / 2) * 0.4

        min_x = TRACK_LEFT + effective_radius; max_x = TRACK_RIGHT - effective_radius
        min_y = TRACK_TOP + effective_radius; max_y = TRACK_BOTTOM - effective_radius
        # --- FIX: Reduced bounce damping ---
        collision_damping = 0.3 # Reduced from 0.5
        # --- END FIX ---

        collided = False
        if self.pos_x < min_x:
            self.pos_x = min_x # Force position to boundary
            self.vel_x *= -collision_damping # Reverse and dampen X velocity
            collided = True
        elif self.pos_x > max_x:
            self.pos_x = max_x # Force position to boundary
            self.vel_x *= -collision_damping # Reverse and dampen X velocity
            collided = True

        if self.pos_y < min_y:
            self.pos_y = min_y # Force position to boundary
            self.vel_y *= -collision_damping # Reverse and dampen Y velocity
            collided = True
        elif self.pos_y > max_y:
            self.pos_y = max_y # Force position to boundary
            self.vel_y *= -collision_damping # Reverse and dampen Y velocity
            collided = True
        # --- End Boundary Collision ---

        self.speed = math.hypot(self.vel_x, self.vel_y)

        # Trail update
        self.trail.append((self.pos_x, self.pos_y))
        if len(self.trail) > self.trail_length: # Use dynamic trail length
            self.trail.pop(0)

        # --- Visual Rotation ---
        self.visual_angle = self.angle # Visual angle matches movement angle
        # --- FIX: Correct rotation value (assuming DOWN is 270 deg base, negate for CCW rotation) ---
        rotation_value = self.visual_angle - 270.0  # Negated (270.0 - self.visual_angle)
        # --- END FIX ---
        try:
             rotated_image_base = pygame.transform.rotate(self.original_image, rotation_value)
        except pygame.error as e:
             print(f"Error rotating player image: {e}")
             rotated_image_base = self.image # Use last valid image as fallback

        # --- Apply Joao Brightness ---
        if self.is_brightened:
             brighten_amount = (50, 50, 50)
             bright_image = rotated_image_base.copy()
             bright_image.fill(brighten_amount, special_flags=pygame.BLEND_RGB_ADD)
             self.image = bright_image
        else:
             self.image = rotated_image_base

        # --- Update Rect ---
        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))


        # Player bounce animation
        if PLAYER_BOUNCE_ENABLED:
            self.bounce_timer = (self.bounce_timer + PLAYER_BOUNCE_SPEED * dt) % (2 * math.pi)
            self.bounce_offset = int(math.sin(self.bounce_timer) * PLAYER_BOUNCE_AMOUNT)

        # --- Update ability effect sprites ---
        if hasattr(self, 'ability_effects'): # Check if group exists
            self.ability_effects.update(dt, self) # Pass player ref to ability effect update

    def get_draw_rect(self):
        if PLAYER_BOUNCE_ENABLED:
            draw_rect = self.rect.copy(); draw_rect.y += self.bounce_offset; return draw_rect
        else: return self.rect

    def activate_ability(self, current_time, player_ref): # Changed 'level' to 'player_ref'
        if current_time - self.last_ability < self.cooldown: return

        self.last_ability = current_time
        ability_sound_path = None
        animation_image_path = None
        effect_lifetime = ABILITY_EFFECT_DURATION
        effect_fade_start = 0.0 # Start fading immediately for short effect

        # --- Determine size factor based on character ---
        size_factor = ABILITY_ANIMATION_SIZE_FACTOR # Default
        if self.character == 3: # Mesky
            size_factor = ABILITY_ANIMATION_SIZE_FACTOR * 1.1 # 10% larger for Mesky
        elif self.character == 4: # Chosen Seed
            size_factor = ABILITY_ANIMATION_SIZE_FACTOR_CHOSEN # Use its specific larger factor

        # Character ability logic
        if self.character == 1: # SeedGuy Dash
            dash_distance = 100 # Pixels to dash forward
            rad = math.radians(self.angle)
            dash_dx = dash_distance * math.cos(rad)
            dash_dy = -dash_distance * math.sin(rad) # Pygame Y inverted

            # Calculate potential new position
            new_pos_x = self.pos_x + dash_dx
            new_pos_y = self.pos_y + dash_dy

            # Clamp to track boundaries (using radius for collision check)
            effective_radius = ((self.base_width + self.base_height) / 2) * 0.4
            min_x = TRACK_LEFT + effective_radius; max_x = TRACK_RIGHT - effective_radius
            min_y = TRACK_TOP + effective_radius; max_y = TRACK_BOTTOM - effective_radius

            self.pos_x = max(min_x, min(max_x, new_pos_x))
            self.pos_y = max(min_y, min(max_y, new_pos_y))

            # Reset velocity after dash/teleport
            self.vel_x = 0
            self.vel_y = 0

            # --- VFX: Dash Particles ---
            num_particles = 15
            particle_speed_range = (100, 250)
            particle_lifetime = 400 # ms
            particle_spawn_x = self.pos_x # Spawn at new position
            particle_spawn_y = self.pos_y
            if hasattr(player_ref, 'particle_group_ref') and player_ref.particle_group_ref is not None:
                for _ in range(num_particles):
                     angle_offset = random.uniform(-math.pi / 4, math.pi / 4)
                     p_angle = rad + math.pi + angle_offset # Opposite direction + spread
                     p_speed = random.uniform(particle_speed_range[0], particle_speed_range[1])
                     new_particle = Particle((particle_spawn_x, particle_spawn_y), color=TRAIL_COLOR_SEEDGUY, lifetime_ms=particle_lifetime, speed_range=(p_speed, p_speed))
                     new_particle.vel_x = p_speed * math.cos(p_angle) # Set initial velocity
                     new_particle.vel_y = p_speed * math.sin(p_angle)
                     player_ref.particle_group_ref.add(new_particle)
            else:
                 print("Warning: Player missing particle_group_ref in activate_ability for dash.")
            # --- End VFX ---

            ability_sound_path = XDASH_SOUND
            animation_image_path = DASH_ANIMATION_IMAGE

        elif self.character == 2: # Joao Speed Boost
            self.ability_active = True
            self.ability_start_time = current_time
            ability_sound_path = XSPEED_SOUND
            animation_image_path = SPEED_ANIMATION_IMAGE

        elif self.character == 3: # Mesky Slow Field
            self.ability_active = True
            self.ability_start_time = current_time
            ability_sound_path = XSLOW_SOUND
            animation_image_path = SLOW_ANIMATION_IMAGE

        elif self.character == 4: # Chosen Seed Immunity
             self.ability_active = True
             self.ability_start_time = current_time
             # Grant invincibility for the *duration* of the ability
             self.invincible_until = current_time + CHOSEN_SEED_DURATION # Use duration constant
             ability_sound_path = XIMMUNITY_SOUND
             animation_image_path = INVINC_ANIMATION_IMAGE

        # --- Spawn Ability Animation Effect ---
        if animation_image_path and hasattr(self, 'ability_effects'): # Check if group exists
             # --- FIX: Pass player size AND correct size_factor to AbilityEffect constructor ---
             effect = AbilityEffect(self.rect.center, animation_image_path, self.size,
                                   lifetime=effect_lifetime, fade_start_time=effect_fade_start,
                                   base_size_factor=size_factor) # Pass the determined size_factor
             # --- END FIX ---
             self.ability_effects.add(effect)
        # --- END ---

        # Play sound
        if ability_sound_path and os.path.exists(ability_sound_path):
            try:
                if pygame.mixer.get_init():
                    sound = pygame.mixer.Sound(ability_sound_path); sound.set_volume(0.7); sound.play()
            except pygame.error as e: print(f"Error playing ability sound {ability_sound_path}: {e}")


# --- Function to create shield break particles (called from main.py) ---
def create_shield_break_particles(center_pos, particle_group):
    num_particles = 25
    for _ in range(num_particles):
        # Blueish-white particles
        color = (random.randint(180, 255), random.randint(180, 255), 255)
        size_range = (4, 10)
        speed_range = (150, 300)
        lifetime = random.randint(300, 600)
        particle = Particle(center_pos, color=color, size_range=size_range, speed_range=speed_range, lifetime_ms=lifetime)
        particle_group.add(particle)
# --- END NEW ---


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, base_speed_unit, image_path=DEBT_IMAGE, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs):
        super().__init__()
        self.final_size = int(ORIGINAL_ENEMY_BASE_SIZE * size_multiplier)
        self.size = (self.final_size, self.final_size)

        self.frames = []
        effective_image_path = image_path if image_path and os.path.exists(image_path) else DEBT_IMAGE

        # Pass size_multiplier as the scale factor for load_sprite_frames
        scale_for_load = size_multiplier
        self.frames = load_sprite_frames(effective_image_path, frame_width, frame_height, scale=scale_for_load, is_enemy=is_enemy)

        self.current_frame_index = 0.0
        self.animation_speed = 6.0 # Default animation speed

        if self.frames:
            self.image = self.frames[0]
            self.rect = self.image.get_rect(center=(x, y))
        else:
            # Fallback if frame loading failed
            self.image = load_image(effective_image_path, self.size)
            self.frames = [self.image] # Treat as single frame
            self.rect = self.image.get_rect(center=(x,y))

        self.radius = self.rect.width / 2 * 0.8

        self.pos_x = float(x); self.pos_y = float(y)
        self.base_speed_pps = base_speed_unit * 60
        shop_speed_level = kwargs.get('shop_speed_level', 0)
        enemy_speed_boost = 1.0 + (shop_speed_level * SHOP_SPEED_ENEMY_BOOST_FACTOR)
        self.speed_pps = self.base_speed_pps * ENEMY_SPEED_MULTIPLIER * enemy_speed_boost

        angle = random.uniform(0, 2 * math.pi)
        self.vel_x = self.speed_pps * math.cos(angle)
        self.vel_y = self.speed_pps * math.sin(angle)

        self.homing = False
        self.bounce_factor = ENEMY_BOUNCE_FACTOR
        self.mass = 1.0

    def update(self, player=None, speed_modifier=1.0, dt=1/FPS, other_enemies=None):
        if dt <= 0: return
        is_frozen = speed_modifier <= 0.01

        # --- Animation Update (Before Movement) ---
        if self.frames and len(self.frames) > 1:
            current_anim_speed = self.animation_speed if not is_frozen else self.animation_speed * 0.1
            self.current_frame_index += current_anim_speed * dt
            frame_index_int = int(self.current_frame_index) % len(self.frames)
            new_image = self.frames[frame_index_int]
            if self.image is not new_image: # Optimization: only update if image changes
                self.image = new_image;
                current_center = self.rect.center # Store center before changing image
                self.rect = self.image.get_rect(center=current_center) # Update rect with new image, keep center
                self.radius = self.rect.width / 2 * 0.9 # Update radius if size changes


        if is_frozen:
            # Update rect position even if frozen, but don't move
            self.rect.center = (int(self.pos_x), int(self.pos_y))
            return

        current_target_speed = self.speed_pps * speed_modifier

        # --- Homing Logic (Adjust velocity target) ---
        if self.homing and player is not None:
            dx = player.pos_x - self.pos_x
            dy = player.pos_y - self.pos_y
            dist_sq = dx*dx + dy*dy
            homing_strength = 0.05 # Adjust for desired homing intensity
            if dist_sq > 1: # Avoid division by zero and extreme forces at close range
                dist = math.sqrt(dist_sq)
                target_vel_x = current_target_speed * dx / dist
                target_vel_y = current_target_speed * dy / dist
                # Interpolate towards target velocity
                lerp_factor = min(homing_strength * 60 * dt, 1.0) # Scale lerp by dt
                self.vel_x = self.vel_x * (1 - lerp_factor) + target_vel_x * lerp_factor
                self.vel_y = self.vel_y * (1 - lerp_factor) + target_vel_y * lerp_factor

        # --- Ensure speed matches target speed AFTER homing adjustment ---
        current_vel_magnitude_sq = self.vel_x**2 + self.vel_y**2
        target_speed_sq = current_target_speed**2

        # Adjust speed if significantly different or if stopped but should move
        if current_vel_magnitude_sq < 0.01 and target_speed_sq > 0.01:
             angle = random.uniform(0, 2 * math.pi)
             self.vel_x = current_target_speed * math.cos(angle)
             self.vel_y = current_target_speed * math.sin(angle)
        elif current_vel_magnitude_sq > 0.01 and abs(current_vel_magnitude_sq - target_speed_sq) > 1.0:
             scale = math.sqrt(target_speed_sq / current_vel_magnitude_sq)
             self.vel_x *= scale
             self.vel_y *= scale

        # --- Enemy-Enemy Collision (Simplified Elastic) ---
        if other_enemies:
            for other in other_enemies:
                if other is self: continue
                if not all(hasattr(other, attr) for attr in ['pos_x', 'pos_y', 'vel_x', 'vel_y', 'radius', 'mass']): continue
                dx = self.pos_x - other.pos_x; dy = self.pos_y - other.pos_y
                dist_sq = dx*dx + dy*dy; min_dist = self.radius + other.radius
                if dist_sq < min_dist*min_dist and dist_sq > 0.01:
                    dist = math.sqrt(dist_sq); overlap = min_dist - dist
                    nx = dx / dist; ny = dy / dist
                    separation_factor = 0.5
                    self.pos_x += nx * overlap * separation_factor; self.pos_y += ny * overlap * separation_factor
                    other.pos_x -= nx * overlap * separation_factor; other.pos_y -= ny * overlap * separation_factor
                    rel_vx = self.vel_x - other.vel_x; rel_vy = self.vel_y - other.vel_y
                    vel_along_normal = rel_vx * nx + rel_vy * ny
                    if vel_along_normal > 0: continue
                    # --- FIX: Reduced enemy-enemy bounce ---
                    e = 0.7 # Reduced from 0.8
                    # --- END FIX ---
                    j = -(1 + e) * vel_along_normal; j /= 2.0
                    impulse_x = j * nx; impulse_y = j * ny
                    self.vel_x += impulse_x; self.vel_y += impulse_y
                    other.vel_x -= impulse_x; other.vel_y -= impulse_y

        # --- Update Position FIRST ---
        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt

        # --- Boundary Collision AFTER updating position ---
        collided_boundary = False
        new_vel_x, new_vel_y = self.vel_x, self.vel_y
        effective_radius = self.radius # Use current radius
        min_x = TRACK_LEFT + effective_radius; max_x = TRACK_RIGHT - effective_radius
        min_y = TRACK_TOP + effective_radius; max_y = TRACK_BOTTOM - effective_radius

        if self.pos_x < min_x:
            self.pos_x = min_x # Snap to boundary
            new_vel_x = abs(self.vel_x) * self.bounce_factor # Reverse X, apply factor
            collided_boundary = True
        elif self.pos_x > max_x:
            self.pos_x = max_x # Snap to boundary
            new_vel_x = -abs(self.vel_x) * self.bounce_factor # Reverse X, apply factor
            collided_boundary = True

        if self.pos_y < min_y:
            self.pos_y = min_y # Snap to boundary
            new_vel_y = abs(self.vel_y) * self.bounce_factor # Reverse Y, apply factor
            collided_boundary = True
        elif self.pos_y > max_y:
            self.pos_y = max_y # Snap to boundary
            new_vel_y = -abs(self.vel_y) * self.bounce_factor # Reverse Y, apply factor
            collided_boundary = True

        # Only update velocity if a collision occurred
        if collided_boundary:
            self.vel_x, self.vel_y = new_vel_x, new_vel_y
        # --- End Boundary Collision ---

        # Update rect center based on final position
        self.rect.center = (int(self.pos_x), int(self.pos_y))


class EarthEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = EARTH_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=80, frame_height=64, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)
        self.animation_speed = 5.0

class FireEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = FIRE_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)
        self.animation_speed = 7.0

class WaterEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = WATER_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class FrostEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = FROST_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)
        self.animation_speed = 4.0

class UnderworldEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = UNDERWORLD_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=96, frame_height=96, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class DesertEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = DESERT_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=64, frame_height=64, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class JungleEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = JUNGLE_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class SpaceEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = SPACE_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class CyberEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = CYBER_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)

class MysticEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = MYSTIC_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)


class SuperseedEnemy(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        kwargs['image_path'] = SUPERSEED_ENEMY_IMAGE
        super().__init__(x, y, base_speed_unit, frame_width=0, frame_height=0, is_enemy=True, size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, **kwargs)
        self.flash_timer = 0.0; self.flash_interval = 0.05
        self.original_frame_images = [frame.copy() for frame in self.frames] if self.frames else []
        self.original_single_image = self.image.copy() if not self.frames and hasattr(self, 'image') else None
        self.is_flashed = False; self.animation_speed = 8.0

    def update(self, player=None, speed_modifier=1.0, dt=1/FPS, other_enemies=None):
        super().update(player, speed_modifier, dt, other_enemies)
        # Only flash if not frozen
        if speed_modifier > 0.01:
            self.flash_timer += dt
            if self.flash_timer >= self.flash_interval:
                self.flash_timer -= self.flash_interval; self.is_flashed = not self.is_flashed
                base_image_this_frame = None
                if self.original_frame_images and len(self.original_frame_images) > 1:
                    frame_idx = int(self.current_frame_index) % len(self.original_frame_images)
                    base_image_this_frame = self.original_frame_images[frame_idx]
                elif self.original_single_image: base_image_this_frame = self.original_single_image
                elif self.original_frame_images: base_image_this_frame = self.original_frame_images[0]

                if base_image_this_frame:
                    if self.is_flashed:
                        flash_image = base_image_this_frame.copy()
                        random_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        flash_image.fill(random_color, special_flags=pygame.BLEND_RGB_MULT)
                        self.image = flash_image
                    else: self.image = base_image_this_frame
        else: # If frozen, ensure we are showing the non-flashed image
             base_image_this_frame = None
             if self.original_frame_images and len(self.original_frame_images) > 1:
                 frame_idx = int(self.current_frame_index) % len(self.original_frame_images)
                 base_image_this_frame = self.original_frame_images[frame_idx]
             elif self.original_single_image: base_image_this_frame = self.original_single_image
             elif self.original_frame_images: base_image_this_frame = self.original_frame_images[0]
             if base_image_this_frame: self.image = base_image_this_frame


# --- UPDATED: David Class with Dash and Sprite Loading Fix ---
class David(Enemy):
    def __init__(self, x, y, base_speed_unit, **kwargs):
        david_boosted_speed_unit = base_speed_unit * 1.2
        # Call super().__init__ but don't rely on it for David's specific image/size yet.
        # Pass a placeholder image path or let it use the default DEBT_IMAGE initially.
        # The size multiplier here will affect the *initial* calculation before we override.
        # --- FIX: Remove explicit image_path from super call, let kwargs handle it ---
        super().__init__(x, y, david_boosted_speed_unit,
                         # image_path=DEBT_IMAGE, # <<< REMOVED THIS LINE
                         frame_width=0, frame_height=0,
                         is_enemy=True, # Let it initialize as a standard enemy first
                         size_multiplier=ENEMY_CUMULATIVE_SIZE_INCREASE, # Use standard enemy size for initial calc
                         **kwargs)
        # --- END FIX ---

        # --- FIX: Explicitly load and scale David's image AFTER super init ---
        # Calculate the desired final size for David
        target_david_size_val = int(ORIGINAL_ENEMY_BASE_SIZE * DAVID_SIZE_MULTIPLIER)
        target_david_size = (target_david_size_val, target_david_size_val)

        # Load David's specific image using load_image to the calculated size
        # Use DAVID_IMAGE constant directly here
        david_image_loaded = load_image(DAVID_IMAGE, target_david_size)

        # Override the image and frames list
        self.image = david_image_loaded
        self.frames = [self.image] # Treat as single frame

        # Recalculate rect and radius based on the correctly sized image
        current_center = (x, y) # Use initial center
        self.rect = self.image.get_rect(center=current_center)
        self.radius = self.rect.width / 2 * 0.8 # Use the same radius factor as base Enemy

        # --- Store original image for flashing ---
        self.original_image_for_flash = self.image.copy()
        # --- END FIX ---

        self.homing = True # David always homes (when not dashing)
        self.animation_speed = 0 # No animation needed for single image

        # --- Dash State ---
        self.dash_state = "NORMAL" # NORMAL, PREP_DASH, DASHING
        self.dash_state_timer = 0.0
        self.next_dash_check_time = time.time() + random.uniform(DAVID_DASH_INTERVAL_MIN, DAVID_DASH_INTERVAL_MAX)
        self.dash_target_x = 0
        self.dash_target_y = 0
        # --- End Dash State ---

    def update(self, player, speed_modifier=1.0, dt=1/FPS, other_enemies=None):
        current_time = time.time()
        is_frozen = speed_modifier <= 0.01 # Check if externally frozen

        # --- State Machine Logic ---
        if is_frozen:
            # If frozen, interrupt any dash behaviour and stay frozen
            self.dash_state = "NORMAL"
            self.dash_state_timer = 0.0
            # Call base class update with freeze modifier, ensuring no animation attempted
            # Since David now only has 1 frame, super().update won't try to animate anyway
            super().update(player, speed_modifier, dt, other_enemies)
            return # Don't process dash logic if frozen

        # --- NORMAL State ---
        if self.dash_state == "NORMAL":
            # Check if it's time to consider dashing
            if current_time >= self.next_dash_check_time:
                self.next_dash_check_time = current_time + random.uniform(DAVID_DASH_INTERVAL_MIN, DAVID_DASH_INTERVAL_MAX)
                if player:
                    dx = player.pos_x - self.pos_x
                    dy = player.pos_y - self.pos_y
                    dist_sq = dx*dx + dy*dy
                    # Check if player is within dash range
                    if dist_sq < DAVID_DASH_RANGE_SQ:
                        self.dash_state = "PREP_DASH"
                        self.dash_state_timer = 0.0
                        self.dash_target_x = player.pos_x # Store player pos at start of prep
                        self.dash_target_y = player.pos_y
                        self.vel_x, self.vel_y = 0, 0 # Stop moving during prep
                        print("David entering PREP_DASH")
                        if os.path.exists(DAVID_DASH_SOUND) and pygame.mixer.get_init(): # Play prep sound? Use dash sound for now
                            try: pygame.mixer.Sound(DAVID_DASH_SOUND).play()
                            except pygame.error as e: print(f"David dash sound error: {e}")

            # If not prepping dash, perform normal homing movement
            if self.dash_state == "NORMAL":
                self.homing = True # Ensure homing is on
                super().update(player, speed_modifier, dt, other_enemies) # Base class handles homing

        # --- PREP_DASH State ---
        elif self.dash_state == "PREP_DASH":
            self.dash_state_timer += dt

            # --- FIX: Base flash on single original image ---
            # Use the stored original image for flashing
            flash_base_image = self.original_image_for_flash
            # --- END FIX ---

            # Flash visually during prep
            flash_on = int(self.dash_state_timer * 15) % 2 == 0 # Fast flash
            if flash_on:
                 # Create a copy to apply the flash effect without modifying the original
                 flash_image = flash_base_image.copy()
                 flash_image.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_ADD) # Reddish flash
                 self.image = flash_image
            else:
                 self.image = flash_base_image # Restore original image

            # Stop movement is already done when entering state
            # Check if prep time is over
            if self.dash_state_timer >= DAVID_DASH_PREP_TIME:
                self.dash_state = "DASHING"
                self.dash_state_timer = 0.0
                # Calculate dash vector towards stored target position
                dx = self.dash_target_x - self.pos_x
                dy = self.dash_target_y - self.pos_y
                dist = math.hypot(dx, dy)
                dash_speed = self.speed_pps * DAVID_DASH_SPEED_MULTIPLIER # Use base speed * multiplier
                if dist > 1:
                    self.vel_x = (dx / dist) * dash_speed
                    self.vel_y = (dy / dist) * dash_speed
                else: # If already at target, dash randomly? Or just revert? Revert for now.
                    self.dash_state = "NORMAL"
                    self.vel_x, self.vel_y = 0, 0 # Avoid instant movement
                print("David entering DASHING")

            # Update rect position even when stopped
            self.rect.center = (int(self.pos_x), int(self.pos_y))


        # --- DASHING State ---
        elif self.dash_state == "DASHING":
            self.dash_state_timer += dt
            self.homing = False # No homing during dash

            # Move based on calculated dash velocity
            self.pos_x += self.vel_x * dt
            self.pos_y += self.vel_y * dt

            # Boundary checks (stop velocity component on hit)
            min_x = TRACK_LEFT + self.radius; max_x = TRACK_RIGHT - self.radius
            min_y = TRACK_TOP + self.radius; max_y = TRACK_BOTTOM - self.radius
            hit_boundary = False
            if self.pos_x < min_x: self.pos_x = min_x; hit_boundary = True; self.vel_x = 0 # Stop velocity component
            elif self.pos_x > max_x: self.pos_x = max_x; hit_boundary = True; self.vel_x = 0 # Stop velocity component
            if self.pos_y < min_y: self.pos_y = min_y; hit_boundary = True; self.vel_y = 0 # Stop velocity component
            elif self.pos_y > max_y: self.pos_y = max_y; hit_boundary = True; self.vel_y = 0 # Stop velocity component

            if hit_boundary:
                print("David hit boundary during dash, stopping dash.")
                self.dash_state = "NORMAL" # End dash early if boundary hit
                # Velocity will be recalculated in the next NORMAL state update

            # Check if dash duration is over
            if self.dash_state_timer >= DAVID_DASH_DURATION:
                self.dash_state = "NORMAL"
                print("David finished DASHING")
                # Velocity will be recalculated in the next NORMAL state update

            # Restore normal image after flashing stops
            self.image = self.original_image_for_flash # Restore single original image
            # Update rect position
            self.rect.center = (int(self.pos_x), int(self.pos_y))

            # Note: Enemy-enemy collision during dash is ignored for simplicity
# --- END UPDATE ---


# --- UPDATED: ShooterEnemy with Charging ---
class ShooterEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_width = int(ORIGINAL_SHOOTER_BASE_WIDTH * SHOOTER_SIZE_MULTIPLIER)
        self.base_height = int(ORIGINAL_SHOOTER_BASE_HEIGHT * SHOOTER_SIZE_MULTIPLIER)
        self.size = (self.base_width, self.base_height)

        # --- FIX: Use explicit frame dimensions for shooter.png ---
        # Assuming total width is 1760px for 10 frames -> 176px width
        shooter_frame_width = 176
        shooter_frame_height = 128
        # Calculate scale needed to reach self.size from frame dimensions
        scale_w = self.size[0] / shooter_frame_width if shooter_frame_width > 0 else 1.0
        scale_h = self.size[1] / shooter_frame_height if shooter_frame_height > 0 else 1.0
        scale_factor = (scale_w + scale_h) / 2.0
        self.frames = load_sprite_frames(SHOOTER_IMAGE, shooter_frame_width, shooter_frame_height, scale=scale_factor, is_enemy=True)
        # --- END FIX ---

        self.current_frame_index = 0.0
        self.animation_speed = 3.0

        if self.frames:
             self.original_frames = [frame.copy() for frame in self.frames] # Store originals
             self.image = self.frames[0]
        else:
             self.image = load_image(SHOOTER_IMAGE, self.size)
             self.original_frames = [self.image.copy()] if self.image else [] # Store single frame if loaded
             self.frames = [self.image] if self.image else [] # Ensure frames has at least one fallback image

        self.rect = self.image.get_rect(center=(x, y))
        self.radius = self.rect.width / 2 * 0.9
        self.pos_x = float(x); self.pos_y = float(y)

        # --- Shooting State ---
        self.state = "IDLE" # IDLE, CHARGING
        self.last_shot_time = 0.0 # Tracks when the *last successful shot* was fired
        self.shoot_interval = SHOOTER_SHOT_INTERVAL / 1000.0
        self.charge_start_time = 0.0
        # --- End Shooting State ---

    def update(self, current_time_sec, projectiles_group, player):
        is_frozen = player is None # Assume frozen if player object isn't passed

        # --- Animation ---
        if self.frames and len(self.frames) > 1:
            current_anim_speed = self.animation_speed if not is_frozen else self.animation_speed * 0.1
            dt_anim = 1.0 / FPS # Assume standard FPS for animation timing
            self.current_frame_index += current_anim_speed * dt_anim
            frame_idx = int(self.current_frame_index) % len(self.frames)
            # Ensure original_frames exists and index is valid
            if self.original_frames and frame_idx < len(self.original_frames):
                new_image_base = self.original_frames[frame_idx] # Use original frame for base
            else:
                 new_image_base = self.image # Fallback to current image

            # Apply charging visual cue if applicable
            if self.state == "CHARGING":
                 # Brighten the base frame
                 charge_image = new_image_base.copy()
                 # Pulse brightness based on charge time
                 charge_elapsed = current_time_sec - self.charge_start_time
                 pulse_factor = abs(math.sin(charge_elapsed * 15)) # Fast pulse
                 brighten_val = int(80 + 70 * pulse_factor) # Pulsating brightness
                 charge_image.fill((brighten_val, brighten_val, brighten_val), special_flags=pygame.BLEND_RGB_ADD)
                 final_image = charge_image
            else:
                 final_image = new_image_base # Use normal base frame

            if self.image is not final_image: # Update only if image changed
                self.image = final_image
                current_center = self.rect.center
                self.rect = self.image.get_rect(center=current_center)
                self.radius = self.rect.width / 2 * 0.9 # Update radius
        # --- End Animation ---

        # --- Shooting Logic ---
        if not is_frozen:
            # IDLE State: Check if ready to start charging
            if self.state == "IDLE" and current_time_sec - self.last_shot_time >= self.shoot_interval:
                 self.state = "CHARGING"
                 self.charge_start_time = current_time_sec
                 #print("Shooter CHARGING") # Optional debug
                 # Play charging sound
                 if os.path.exists(SHOOTER_CHARGE_SOUND) and pygame.mixer.get_init():
                      try: pygame.mixer.Sound(SHOOTER_CHARGE_SOUND).play()
                      except pygame.error as e: print(f"Shooter charge sound error: {e}")

            # CHARGING State: Check if charge time is over
            elif self.state == "CHARGING":
                if current_time_sec - self.charge_start_time >= SHOOTER_CHARGE_TIME:
                    # Fire projectile
                    if player: # Double-check player exists
                        projectile = Projectile(self.rect.centerx, self.rect.centery, player)
                        projectiles_group.add(projectile)
                        #print("Shooter FIRED") # Optional debug
                    self.last_shot_time = current_time_sec # Update time of last shot
                    self.state = "IDLE" # Return to idle state

        # --- Ensure rect position is updated even if not animating/shooting ---
        self.rect.center = (int(self.pos_x), int(self.pos_y))

# --- END UPDATE ---


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.size = (10, 10)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.color = (255, 255, 0); pygame.draw.circle(self.image, self.color, (self.size[0]//2, self.size[1]//2), self.size[0]//2)
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = self.rect.width / 2
        self.pos_x = float(x); self.pos_y = float(y)
        self.speed_pps = PROJECTILE_SPEED

        player_speed_pps = player.speed; rad = math.radians(player.angle)
        player_vx = player.vel_x # Use player's actual velocity
        player_vy = player.vel_y
        predicted_x = player.pos_x + player_vx * PROJECTILE_LEAD_TIME
        predicted_y = player.pos_y + player_vy * PROJECTILE_LEAD_TIME
        dx = predicted_x - self.pos_x; dy = predicted_y - self.pos_y
        dist = math.hypot(dx, dy)

        if dist > 0: self.vel_x = (dx / dist) * self.speed_pps; self.vel_y = (dy / dist) * self.speed_pps
        else: target_angle = random.uniform(0, 2 * math.pi); self.vel_x = self.speed_pps * math.cos(target_angle); self.vel_y = self.speed_pps * math.sin(target_angle)

        self.spawn_time_sec = pygame.time.get_ticks() / 1000.0
        self.lifetime_sec = 5.0

    def update(self, dt=1/FPS, speed_modifier=1.0):
        if dt <= 0: return
        current_time_sec = pygame.time.get_ticks() / 1000.0
        effective_dt = dt * speed_modifier
        self.pos_x += self.vel_x * effective_dt; self.pos_y += self.vel_y * effective_dt
        self.rect.center = (int(self.pos_x), int(self.pos_y))

        padded_track_rect = pygame.Rect(TRACK_LEFT - 50, TRACK_TOP - 50, TRACK_RIGHT - TRACK_LEFT + 100, TRACK_BOTTOM - TRACK_TOP + 100)
        if not padded_track_rect.colliderect(self.rect) or current_time_sec - self.spawn_time_sec > self.lifetime_sec: self.kill()

    def draw(self, screen): # Consider passing offset to draw method
        # screen.blit(self.image, self.rect) # Simple draw without offset
        # For offset drawing (if needed, modify or draw in main loop):
        # screen.blit(self.image, (self.rect.x + offset_x, self.rect.y + offset_y))

        # Trail drawing needs offset too if camera is used
        trail_length = 15
        if abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1:
             vel_magnitude = math.hypot(self.vel_x, self.vel_y)
             if vel_magnitude > 0:
                 start_x = self.rect.centerx - self.vel_x * (trail_length / vel_magnitude)
                 start_y = self.rect.centery - self.vel_y * (trail_length / vel_magnitude)
                 try:
                     # Apply offset to draw position
                     # pygame.draw.line(screen, self.color, (int(start_x + offset_x), int(start_y + offset_y)), (self.rect.centerx + offset_x, self.rect.centery + offset_y), 2)
                     pygame.draw.line(screen, self.color, (int(start_x), int(start_y)), self.rect.center, 2) # Draw without offset for now
                 except TypeError: pass


class CollectibleSeed(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.final_size = max(1, int(ORIGINAL_SEED_BASE_SIZE * SEED_SIZE_MULTIPLIER))
        self.size = (self.final_size, self.final_size)
        self.image = load_image(SEED_IMAGE, self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = self.rect.width / 2 * 1.1
        # Store position for potential magnet effect
        self.pos_x = float(x)
        self.pos_y = float(y)

    def update(self):
        # Seeds should NOT move on their own. Only their rect should sync with pos_x/pos_y
        # which might be changed externally by the magnet effect in main.py
        self.rect.center = (int(self.pos_x), int(self.pos_y))


# --- UPDATED: FinishLine Class for mainnet.png ---
class FinishLine(pygame.sprite.Sprite):
    def __init__(self, x, y_pos): # Accept x and y_pos
        super().__init__()
        # --- FIX: Define fixed goal size ---
        self.final_size = (100, 100) # Let's try a fixed size
        # --- END FIX ---
        # --- FIX: Load MAINNET_IMAGE with the fixed size ---
        self.image = load_image(MAINNET_IMAGE, self.final_size)
        # --- END FIX ---
        self.frames = [] # No animation frames needed

        self.current_frame_index = 0.0; self.animation_speed = 0.0 # No animation
        self.pos_x = float(x)
        self.pos_y = float(y_pos) # <<< Use the passed y_pos directly
        # --- FIX: Center the initial rect using the provided x, y_pos ---
        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))
        # --- END FIX ---
        # --- FIX: Slightly smaller radius for collision check ---
        self.radius = ((self.rect.width + self.rect.height) / 2) * 0.45  # Increased from 0.4
        # --- END FIX ---


    def update(self, dt=1/FPS):
        # --- FIX: Remove animation logic ---
        # Ensure rect position reflects pos_x/pos_y if they change (e.g., if goal moved in future)
        current_center = (int(self.pos_x), int(self.pos_y))
        if self.rect.center != current_center:
             self.rect.center = current_center
        # --- END FIX ---
# --- END UPDATE ---


# --- Base PowerUp Class (Optional Refactor) ---
class BasePowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.base_size = int(ORIGINAL_POWERUP_BASE_SIZE * POWERUP_CUMULATIVE_SIZE_INCREASE)
        self.size = (self.base_size, self.base_size)
        self.original_image = load_image(image_path, self.size)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = self.rect.width / 2 * 1.1 # Generous radius
        # --- FIX: Add pos_x/pos_y for consistency ---
        self.pos_x = float(x)
        self.pos_y = float(y)
        # --- END FIX ---

        self.pulse_timer = random.uniform(0, math.pi*2 / 3.0) # Randomize start phase
        self.pulse_speed = 3.0
        self.pulse_range = 0.1

    def update(self, dt=1/FPS):
        # --- FIX: Update rect center from pos_x/pos_y BEFORE animation scaling ---
        current_center = (int(self.pos_x), int(self.pos_y))
        # Only update if position changed (e.g., if powerups moved in future)
        if self.rect.center != current_center:
             self.rect.center = current_center
        # --- END FIX ---

        self.pulse_timer += dt
        scale_factor = 1.0 + math.sin(self.pulse_timer * self.pulse_speed) * self.pulse_range
        new_width = max(1, int(self.base_size * scale_factor))
        new_height = max(1, int(self.base_size * scale_factor))
        try:
            if self.original_image and self.original_image.get_width() > 0 and self.original_image.get_height() > 0:
                 self.image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
            else: # Fallback drawing if original image failed
                 self.image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
                 # Use a color based on type for fallback
                 fallback_color = {"freeze": CYAN, "magnet": GOLD, "shield": BLUE, "double": RED}.get(self.powerup_type, GRAY)
                 pygame.draw.circle(self.image, fallback_color, (new_width//2, new_height//2), new_width//2)
        except (ValueError, pygame.error) as e:
            print(f"Error scaling {self.__class__.__name__}: {e}. Size:({new_width},{new_height})")
            fallback_color = {"freeze": CYAN, "magnet": GOLD, "shield": BLUE, "double": RED}.get(self.powerup_type, GRAY)
            self.image = pygame.Surface((max(1,new_width), max(1,new_height)), pygame.SRCALPHA);
            pygame.draw.circle(self.image, fallback_color, (max(1,new_width)//2, max(1,new_height)//2), max(1,new_width)//2)

        # --- FIX: Update rect center AFTER scaling ---
        # This ensures the scaled image is centered correctly on its position
        self.rect = self.image.get_rect(center=current_center)
        # --- END FIX ---


# --- Existing Powerups inheriting from BasePowerUp ---
class MagnetPowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, MAGNET_IMAGE, "magnet")

class FreezePowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, FREEZE_IMAGE, "freeze")

# --- NEW Powerups inheriting from BasePowerUp ---
class ShieldPowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, SHIELD_POWERUP_IMAGE, "shield")

class DoubleSeedPowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, DOUBLE_SEED_POWERUP_IMAGE, "double")
# --- END NEW Powerups ---


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color=GOLD, size_range=(5, 15), speed_range=(50, 150), lifetime_ms=500):
        super().__init__()
        self.size = random.randint(size_range[0], size_range[1])
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # --- Cache sparkle base image if not already ---
        sparkle_cache_key = "sparkle_base"
        if sparkle_cache_key not in SPRITE_SHEET_CACHE and os.path.exists(SPARKLE_IMAGE):
            try:
                 SPRITE_SHEET_CACHE[sparkle_cache_key] = pygame.image.load(SPARKLE_IMAGE).convert_alpha()
            except Exception as e: print(f"Error loading sparkle base image: {e}")

        if sparkle_cache_key in SPRITE_SHEET_CACHE:
             try:
                 sparkle_base_orig = SPRITE_SHEET_CACHE[sparkle_cache_key]
                 # Scale the cached base image to the particle size
                 if self.size > 0:
                    sparkle_base = pygame.transform.smoothscale(sparkle_base_orig, (self.size, self.size))
                    sparkle_base.fill(color + (0,), special_flags=pygame.BLEND_RGBA_MULT) # Tint the scaled image
                    self.image.blit(sparkle_base, (0,0))
                 else: # Fallback if size is zero
                    pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
             except Exception as e:
                 print(f"Error scaling/tinting sparkle image: {e}")
                 pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        else:
             pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos_x = float(pos[0]); self.pos_y = float(pos[1])
        angle = random.uniform(0, 2 * math.pi)
        speed_pps = random.uniform(speed_range[0], speed_range[1])
        self.vel_x = speed_pps * math.cos(angle); self.vel_y = speed_pps * math.sin(angle)
        self.spawn_time_ms = pygame.time.get_ticks()
        self.lifetime_ms = lifetime_ms

    def update(self, dt=1/FPS):
        if dt <= 0: return
        current_ticks = pygame.time.get_ticks()
        elapsed_ms = current_ticks - self.spawn_time_ms
        if elapsed_ms >= self.lifetime_ms: self.kill(); return

        self.pos_x += self.vel_x * dt; self.pos_y += self.vel_y * dt
        self.rect.center = (int(self.pos_x), int(self.pos_y))

        alpha = max(0, 255 * (1 - (elapsed_ms / self.lifetime_ms)))
        try:
             # Create a copy and set alpha directly (more efficient than copying original each time)
             current_alpha = self.image.get_alpha()
             if current_alpha is None: current_alpha = 255
             if int(alpha) != current_alpha:
                 self.image.set_alpha(int(alpha))
        except pygame.error as e: pass # Ignore errors setting alpha if image is invalid/deleted
# --- END OF FILE game_objects.py ---