import pygame
import random
import math, os
import time # Added for the pause in minigame 3
from settings import *
# --- Import specific classes needed ---
# --- FIX: Add EarthEnemy to the import list ---
# <<< CHANGE: Import circle_collision function from game_objects >>>
from game_objects import (CollectibleSeed, David, FinishLine, Player, Enemy, EarthEnemy,
                          ShooterEnemy, Projectile, Particle, AbilityEffect) # Added Particle, AbilityEffect, EarthEnemy, circle_collision
# <<< END CHANGE >>>

# --- Import UI elements needed for HUD and pause ---
from ui import draw_ability_icon, play_click_sound, pause_menu, FONT_LG, FONT_SM, FONT_MD, draw_shield_aura # Added draw_shield_aura

# Global sprite group for ability effects within minigames
minigame_ability_effects = pygame.sprite.Group()

# Minigame 1 remains unchanged as its collision logic is specific to seeds
def minigame_1(screen, selected_character=1): # Accept selected character
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = MINIGAME1_DURATION
    seed_count = random.randint(MINIGAME1_SEED_RANGE[0], MINIGAME1_SEED_RANGE[1])
    seeds = pygame.sprite.Group()
    # --- Player starts near the top-center now, facing down ---
    player_start_x = SCREEN_WIDTH // 2
    player_start_y = TRACK_TOP + 50 # Start near the top
    player = Player(player_start_x, player_start_y, character=selected_character)
    player.angle = 270 # Explicitly set start angle downwards
    player.visual_angle = 270
    player.apply_vault_upgrades({}) # Apply base vault upgrades if any are relevant (e.g., pickup radius)
    player.last_ability = -float('inf') # Ensure ability is ready at start
    player.ability_active = False # Ensure ability is not active at start
    # --- NEW: Reset ability VFX group for this minigame ---
    minigame_ability_effects.empty()
    player.ability_effects = minigame_ability_effects # Assign the group to the player instance
    # --- END NEW ---
    # --- Add particle group reference ---
    particles = pygame.sprite.Group()
    player.particle_group_ref = particles

    # Load background
    bg_minigame = None
    # Use the path defined in settings.py
    if MINIGAME1_BACKGROUND and os.path.exists(MINIGAME1_BACKGROUND):
        try:
            bg_minigame = pygame.image.load(MINIGAME1_BACKGROUND).convert()
            bg_minigame = pygame.transform.scale(bg_minigame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading Minigame 1 background: {e}")


    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    for _ in range(seed_count):
        while True:
            # --- FIX: Ensure seeds spawn within track bounds ---
            sx = random.randint(TRACK_LEFT + int(player.radius), TRACK_RIGHT - int(player.radius))
            sy = random.randint(TRACK_TOP + int(player.radius), TRACK_BOTTOM - int(player.radius))
            # Ensure seeds don't spawn too close to the player's *actual* start
            if math.hypot(sx - player.pos_x, sy - player.pos_y) > 100:
                seed = CollectibleSeed(sx, sy)
                seeds.add(seed)
                all_sprites.add(seed)
                break

    collected_seeds = 0
    running = True
    paused = False # Pause state
    # --- REMOVED Camera/Shake variables ---

    while running and pygame.time.get_ticks() - start_time < duration:
        dt = clock.tick_busy_loop(FPS) / 1000.0
        dt = min(dt, 0.05)
        current_time_sec = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, 0 # Return loss on quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                     play_click_sound() # Added click sound
                     return False, 0 # Return loss on escape
                if event.key == pygame.K_p: # Pause handling
                    paused = not paused
                    play_click_sound()
                # --- Prevent checkpoint key (C) in minigame ---

        if paused:
            # --- Draw static background during pause ---
            if bg_minigame: screen.blit(bg_minigame, (0,0))
            else: screen.fill(BLACK)
            # --- Draw seeds and player at absolute positions ---
            for seed in seeds:
                screen.blit(seed.image, seed.rect) # Draw at rect position
            player_draw_rect = player.get_draw_rect()
            screen.blit(player.image, player_draw_rect) # Draw at rect position
            # --- End static draw ---

            pause_result = pause_menu(screen) # Show pause menu overlay
            if pause_result == "resume":
                paused = False
            elif pause_result == "menu":
                return "menu", 0 # Allow returning to main menu from pause
            continue # Skip rest of the loop if paused

        # --- Only update game state if not paused ---
        # --- Pass player instance to update for particles AND dt ---
        player.update(pygame.key.get_pressed(), current_time_sec, "clear", shop_upgrades={}, inverse=False,
                      wind_direction=None, player_ref=player, dt=dt)  # <<< Ensure dt is passed
        # --- REMOVED Ability activation shake check ---



        player_pickup_radius = player.radius + player.vault_pickup_radius_bonus

        # --- Collision function (remains the same) ---
        def collide_circle_precise_seed_local(player_sprite, seed_sprite):
            px = getattr(player_sprite, 'pos_x', player_sprite.rect.centerx)
            py = getattr(player_sprite, 'pos_y', player_sprite.rect.centery)
            player_base_radius = getattr(player_sprite, 'radius', player_sprite.rect.width / 2 * 0.8)
            player_vault_bonus = getattr(player_sprite, 'vault_pickup_radius_bonus', 0)
            player_effective_radius = player_base_radius + player_vault_bonus
            sx = getattr(seed_sprite, 'pos_x', seed_sprite.rect.centerx)
            sy = getattr(seed_sprite, 'pos_y', seed_sprite.rect.centery)
            seed_radius = getattr(seed_sprite, 'radius', seed_sprite.rect.width / 2 * 1.1)
            if px is None or py is None or sx is None or sy is None: return False
            dx = px - sx
            dy = py - sy
            distance_sq = dx*dx + dy*dy
            radius_sum = player_effective_radius + seed_radius
            return distance_sq < (radius_sum * radius_sum)

        collected_list = pygame.sprite.spritecollide(player, seeds, True, collide_circle_precise_seed_local)

        if collected_list:
            collected_seeds += len(collected_list)
            for seed_sprite in collected_list:
                 particle_count = 5
                 for _ in range(particle_count): particles.add(Particle(seed_sprite.rect.center))
            if os.path.exists(COLLECT_SOUND) and pygame.mixer.get_init():
                try: pygame.mixer.Sound(COLLECT_SOUND).play()
                except pygame.error as e: print(f"Minigame collect sound error: {e}")

        # --- Update ability effects & particles ---
        minigame_ability_effects.update(dt, player) # Pass player ref to ability effect update
        particles.update(dt)

        # --- Drawing (No Camera Offset) ---
        if bg_minigame: screen.blit(bg_minigame, (0,0))
        else: screen.fill(BLACK)

        # Draw game elements at their absolute rect positions
        for seed in seeds: screen.blit(seed.image, seed.rect)
        for p in particles: screen.blit(p.image, p.rect)

        # Player Trail Drawing (Use absolute positions)
        player_trail_color = PLAYER_TRAIL_COLORS.get(player.character, TRAIL_COLOR_DEFAULT)
        for i, pos in enumerate(player.trail):
            alpha = int(255 * (i / player.trail_length) * 0.5 * player.trail_intensity_multiplier)
            alpha = max(0, min(255, alpha))
            trail_surf = pygame.Surface((player.trail_segment_size, player.trail_segment_size), pygame.SRCALPHA)
            draw_color = (*player_trail_color, alpha)
            pygame.draw.circle(trail_surf, draw_color, (player.trail_segment_size//2, player.trail_segment_size//2), player.trail_segment_size//2)
            draw_pos_x = pos[0] - player.trail_segment_size//2
            draw_pos_y = pos[1] - player.trail_segment_size//2
            screen.blit(trail_surf, (draw_pos_x, draw_pos_y))

        # Player Drawing (Use absolute position from get_draw_rect)
        player_draw_rect = player.get_draw_rect()
        screen.blit(player.image, player_draw_rect)

        # Draw Ability Effects (Use absolute rect positions)
        for effect in minigame_ability_effects: screen.blit(effect.image, effect.rect)

        # --- UI Elements (No offset needed) ---
        time_left = max(0, (duration - (pygame.time.get_ticks() - start_time)) / 1000)

        title_text = FONT_SM.render("Seed Harvest Frenzy", True, GOLD)
        title_rect_base = title_text.get_rect(centerx=SCREEN_WIDTH // 2, top=60)
        screen.blit(title_text, title_rect_base)

        timer_text = FONT_MD.render(f"Time: {time_left:.1f}s | Seeds: {collected_seeds}", True, WHITE)
        timer_rect_base = timer_text.get_rect(centerx=SCREEN_WIDTH // 2, top=title_rect_base.bottom + 5)
        screen.blit(timer_text, timer_rect_base)

        # Draw ability icon HUD (already draws relative to screen)
        draw_ability_icon(screen, player, current_time_sec)
        # --- End Drawing ---

        pygame.mouse.set_visible(True)
        pygame.display.flip()

    return True, collected_seeds


# <<< CHANGE: Add collision_func parameter >>>
def minigame_2(screen, selected_character=1, collision_func=None):
    if collision_func is None:
        print("ERROR: Minigame 2 requires a collision function!")
        return False # Cannot run without collision logic

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = MINIGAME2_DURATION
    # --- Player starts near the top-center now, facing down ---
    player_start_x = SCREEN_WIDTH // 2
    player_start_y = TRACK_TOP + 50 # Start near the top
    player = Player(player_start_x, player_start_y, character=selected_character)
    player.angle = 270 # Explicitly set start angle downwards
    player.visual_angle = 270
    player.apply_vault_upgrades({}) # Apply base vault upgrades
    player.last_ability = -float('inf') # Ensure ability is ready at start
    player.ability_active = False # Ensure ability is not active at start
    # --- NEW: Reset ability VFX group for this minigame ---
    minigame_ability_effects.empty()
    player.ability_effects = minigame_ability_effects # Assign the group to the player instance
    # --- Add particle group reference ---
    particles = pygame.sprite.Group()
    player.particle_group_ref = particles
    # --- END NEW ---

    enemies = pygame.sprite.Group()

    bg_david = None
    if os.path.exists(DAVID_MINIGAME_BACKGROUND):
        try:
            bg_david = pygame.image.load(DAVID_MINIGAME_BACKGROUND).convert()
            bg_david = pygame.transform.scale(bg_david, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading David minigame background: {e}")

    spawn_timer = 0
    enemies_spawned = 0
    max_enemies = MINIGAME2_ENEMY_COUNT
    spawn_interval = MINIGAME2_SPAWN_RATE / 1000.0
    min_dist = MINIGAME2_MIN_SPAWN_DIST

    running = True
    paused = False # Pause state
    # --- REMOVED Camera/Shake variables ---

    while running and pygame.time.get_ticks() - start_time < duration:
        dt = clock.tick_busy_loop(FPS) / 1000.0
        dt = min(dt, 0.05)
        current_ticks = pygame.time.get_ticks()
        current_time_sec = current_ticks / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Return loss on quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                     play_click_sound()
                     return False # Return loss on escape
                if event.key == pygame.K_p: # Pause handling
                    paused = not paused
                    play_click_sound()
                # --- Prevent checkpoint key (C) in minigame ---

        if paused:
            # --- Draw static background during pause ---
            if bg_david: screen.blit(bg_david, (0,0))
            else: screen.fill(BLACK)
            # --- Draw enemies and player at absolute positions ---
            for enemy in enemies:
                screen.blit(enemy.image, enemy.rect) # Draw at rect position
            player_draw_rect = player.get_draw_rect()
            screen.blit(player.image, player_draw_rect) # Draw at rect position
            # --- End static draw ---

            pause_result = pause_menu(screen)
            if pause_result == "resume":
                paused = False
            elif pause_result == "menu":
                return "menu" # Allow returning to main menu from pause
            continue # Skip rest of the loop if paused

        # --- Only update game state if not paused ---
        spawn_timer += dt
        if enemies_spawned < max_enemies and spawn_timer >= spawn_interval:
            spawn_timer -= spawn_interval
            attempts = 0
            while attempts < 50:
                 # --- Spawn within track bounds ---
                 padding = 30
                 ex = random.randint(TRACK_LEFT + padding, TRACK_RIGHT - padding)
                 ey = random.randint(TRACK_TOP + padding, TRACK_BOTTOM - padding)
                 # --- END FIX ---
                 if math.hypot(ex - player.pos_x, ey - player.pos_y) >= min_dist:
                     base_arbitrary_speed_mg2 = 1.5 * 1.2
                     # --- FIX: Pass shop_speed_level=0 ---
                     enemy = David(ex, ey, base_arbitrary_speed_mg2, image_path=DAVID_IMAGE, shop_speed_level=0)
                     # --- END FIX ---
                     enemies.add(enemy)
                     enemies_spawned += 1
                     break
                 attempts += 1

        # --- Pass player_ref AND dt ---
        player.update(pygame.key.get_pressed(), current_time_sec, "clear", shop_upgrades={}, inverse=False,
                      wind_direction=None, player_ref=player, dt=dt)  # <<< Ensure dt is passed
        # --- REMOVED Ability activation shake check ---

        # --- FIX: Correct speed modifier for Mesky ---
        effective_speed_modifier_for_updates = 1.0
        if player.character == 3 and player.ability_active:
            effective_speed_modifier_for_updates = 0.5 # Apply 50% slow
        # --- END FIX ---

        all_enemies = enemies.sprites()
        for i, enemy in enumerate(all_enemies):
            other_enemies_list_for_collision = all_enemies[i+1:]
            # <<< CHANGE: Pass player ref to David's update >>>
            enemy.update(player, speed_modifier=effective_speed_modifier_for_updates, dt=dt, other_enemies=other_enemies_list_for_collision)
            # <<< END CHANGE >>>

        # --- Update ability effects & particles ---
        minigame_ability_effects.update(dt, player) # Pass player ref
        particles.update(dt)

        # <<< REMOVED local collide_circle_mg2 function >>>

        # --- Collision check ---
        # --- FIX: Remove invincibility check for this specific minigame ---
        # The goal is pure survival, invincibility shouldn't prevent loss here.
        # <<< CHANGE: Use passed-in collision_func >>>
        if pygame.sprite.spritecollideany(player, enemies, collision_func):
             if os.path.exists(DEAD_SOUND) and pygame.mixer.get_init():
                 try:
                     pygame.mixer.Sound(DEAD_SOUND).play()
                 except pygame.error as e:
                     print(f"Minigame dead sound error: {e}")
             return False  # Return loss on hit
        # <<< END CHANGE >>>
        # --- END FIX ---
        # --- End Collision Check ---

        # --- Drawing (No Camera Offset) ---
        if bg_david: screen.blit(bg_david, (0,0))
        else: screen.fill(BLACK)

        # Draw game elements at absolute rect positions
        for enemy in enemies: screen.blit(enemy.image, enemy.rect)
        for p in particles: screen.blit(p.image, p.rect)

        # Player Trail Drawing
        player_trail_color = PLAYER_TRAIL_COLORS.get(player.character, TRAIL_COLOR_DEFAULT)
        for i, pos in enumerate(player.trail):
            alpha = int(255 * (i / player.trail_length) * 0.5 * player.trail_intensity_multiplier)
            alpha = max(0, min(255, alpha))
            trail_surf = pygame.Surface((player.trail_segment_size, player.trail_segment_size), pygame.SRCALPHA)
            draw_color = (*player_trail_color, alpha)
            pygame.draw.circle(trail_surf, draw_color, (player.trail_segment_size//2, player.trail_segment_size//2), player.trail_segment_size//2)
            draw_pos_x = pos[0] - player.trail_segment_size//2
            draw_pos_y = pos[1] - player.trail_segment_size//2
            screen.blit(trail_surf, (draw_pos_x, draw_pos_y))


        # Player Drawing
        player_draw_rect = player.get_draw_rect()
        screen.blit(player.image, player_draw_rect)

        # --- Draw Shield Aura (No Offset) ---
        # Mesky's visual aura is drawn here if ability active
        # Also draws temp shields and permanent shields
        draw_shield_aura(screen, player, current_time_sec)
        # --- End Shield Aura ---

        # Draw Ability Effects
        for effect in minigame_ability_effects: screen.blit(effect.image, effect.rect)

        # --- UI Elements (No offset needed) ---
        time_left = max(0, (duration - (current_ticks - start_time)) / 1000)
        timer_text = FONT_MD.render(f"Survive: {time_left:.1f}s", True, WHITE)
        timer_rect_base = timer_text.get_rect(centerx=SCREEN_WIDTH // 2, top=60)
        screen.blit(timer_text, timer_rect_base)

        reward_text = FONT_SM.render("Reward: 1 SUPR", True, GOLD) # Changed currency
        reward_rect_base = reward_text.get_rect(centerx=SCREEN_WIDTH // 2, top=timer_rect_base.bottom + 10)
        screen.blit(reward_text, reward_rect_base)

        # Draw ability icon HUD
        draw_ability_icon(screen, player, current_time_sec)
        # --- End Drawing ---

        pygame.mouse.set_visible(True)
        pygame.display.flip()

    return True # Return win if time runs out


# <<< CHANGE: Add collision_func parameter >>>
def minigame_3(screen, selected_character=1, collision_func=None):
    if collision_func is None:
        print("ERROR: Minigame 3 requires a collision function!")
        return False # Cannot run without collision logic

    clock = pygame.time.Clock()
    # --- Player starts near the top-center now, facing down ---
    player_start_x = SCREEN_WIDTH // 2
    player_start_y = TRACK_TOP + 50 # Start near the top
    player = Player(player_start_x, player_start_y, character=selected_character)
    player.angle = 270 # Explicitly set start angle downwards
    player.visual_angle = 270
    player.apply_vault_upgrades({}) # Apply base vault upgrades
    player.last_ability = -float('inf') # Ensure ability is ready at start
    player.ability_active = False # Ensure ability is not active at start
    # --- NEW: Reset ability VFX group for this minigame ---
    minigame_ability_effects.empty()
    player.ability_effects = minigame_ability_effects # Assign the group to the player instance
    # --- Add particle group reference ---
    particles = pygame.sprite.Group()
    player.particle_group_ref = particles
    # --- END NEW ---

    bg_minigame = None
    if MINIGAME3_BACKGROUND and os.path.exists(MINIGAME3_BACKGROUND):
        try:
            bg_minigame = pygame.image.load(MINIGAME3_BACKGROUND).convert()
            bg_minigame = pygame.transform.scale(bg_minigame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Error loading Minigame 3 background: {e}")

    goal_x = random.randint(TRACK_LEFT + 100, TRACK_RIGHT - 100)
    # --- FIX: Finish line Y position needs to be near the *bottom* ---
    goal_y_offset = 50
    finish_goal = FinishLine(goal_x, TRACK_BOTTOM - goal_y_offset) # Position from bottom
    # --- END FIX ---

    enemies = pygame.sprite.Group()
    shooters = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    num_shooters = MINIGAME3_SHOOTER_COUNT
    num_enemies = MINIGAME3_ENEMY_COUNT

    # Position shooters more towards the middle vertically
    shooter_y_spacing = (TRACK_BOTTOM - TRACK_TOP - 400) / (num_shooters + 1) if num_shooters > 0 else 0
    for i in range(num_shooters):
         sx_options = [TRACK_LEFT + 50, TRACK_RIGHT - 50]
         sx = random.choice(sx_options)
         sy = TRACK_TOP + 200 + (i + 1) * shooter_y_spacing # Start lower
         shooter = ShooterEnemy(sx, sy)
         shooters.add(shooter)

    for _ in range(num_enemies):
         attempts = 0
         while attempts < 50:
             padding = int(player.radius + 10)
             ex = random.randint(TRACK_LEFT + padding, TRACK_RIGHT - padding)
             # Spawn enemies between player start and goal
             min_enemy_y = TRACK_TOP + 100 # Below player start
             max_enemy_y = TRACK_BOTTOM - 150 # Above goal
             if max_enemy_y <= min_enemy_y: ey = min_enemy_y
             else: ey = random.randint(min_enemy_y, max_enemy_y)

             valid_pos = True
             if math.hypot(ex - player.pos_x, ey - player.pos_y) < MIN_ENEMY_SPAWN_DIST_FROM_PLAYER / 2: valid_pos = False
             if valid_pos and math.hypot(ex - finish_goal.rect.centerx, ey - finish_goal.rect.centery) < 100: valid_pos = False
             if valid_pos:
                 for existing_enemy in enemies:
                      enemy_center_x = getattr(existing_enemy, 'pos_x', existing_enemy.rect.centerx)
                      enemy_center_y = getattr(existing_enemy, 'pos_y', existing_enemy.rect.centery)
                      if math.hypot(ex - enemy_center_x, ey - enemy_center_y) < 50: valid_pos = False; break

             if valid_pos:
                 base_arbitrary_speed = 1.5
                 # --- FIX: Instantiate EarthEnemy instead of generic Enemy ---
                 enemy = EarthEnemy(ex, ey, base_arbitrary_speed, shop_speed_level=0)  # Use EarthEnemy class
                 # --- END FIX ---
                 enemies.add(enemy)
                 break
             attempts += 1
         if attempts >= 50: print("Warning (Minigame 3): Could not find ideal spawn position for an enemy after 50 attempts.")

    # Explanation pause
    explanation_duration = 3.0
    explanation_start_time = time.time()
    explanation_paused = True

    while explanation_paused:
        current_time = time.time()
        if current_time - explanation_start_time >= explanation_duration: explanation_paused = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False # Return loss on quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: play_click_sound(); return False # Return loss on escape
                if event.key == pygame.K_k: play_click_sound(); explanation_paused = False

        # Draw the static background game state
        if bg_minigame: screen.blit(bg_minigame, (0,0))
        else: screen.fill(BLACK)

        for enemy in enemies: screen.blit(enemy.image, enemy.rect)
        for shooter in shooters: screen.blit(shooter.image, shooter.rect)
        screen.blit(finish_goal.image, finish_goal.rect)
        screen.blit(player.image, player.get_draw_rect())

        # Draw overlay and explanation text
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_font = FONT_LG; info_font = FONT_SM
        title_surf = title_font.render("Inverse Gauntlet!", True, RED)
        info1_surf = info_font.render("CONTROLS ARE REVERSED!", True, WHITE)
        info2_surf = info_font.render("Reach the Exit Portal!", True, WHITE)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 - 50)
        info1_rect = info1_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=title_rect.bottom + 10)
        info2_rect = info2_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=info1_rect.bottom + 5)
        screen.blit(title_surf, title_rect); screen.blit(info1_surf, info1_rect); screen.blit(info2_surf, info2_rect)

        skip_surf = FONT_SM.render("Press K to Start", True, GOLD)
        skip_rect = skip_surf.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 50)
        screen.blit(skip_surf, skip_rect)

        pygame.mouse.set_visible(True); pygame.display.flip(); clock.tick(FPS)
    # --- End of explanation pause ---

    running = True
    paused = False # Pause state
    # --- REMOVED Camera/Shake variables ---

    while running:
        dt = clock.tick_busy_loop(FPS) / 1000.0
        dt = min(dt, 0.05)
        current_ticks = pygame.time.get_ticks()
        current_time_sec = current_ticks / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False # Return loss on quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: play_click_sound(); return False # Return loss on escape
                if event.key == pygame.K_p: # Pause handling
                    paused = not paused
                    play_click_sound()
                # --- Prevent checkpoint key (C) in minigame ---

        if paused:
            # --- Draw static background during pause ---
            if bg_minigame: screen.blit(bg_minigame, (0,0))
            else: screen.fill(BLACK)
            # --- Draw elements at absolute positions ---
            for enemy in enemies: screen.blit(enemy.image, enemy.rect)
            for shooter in shooters: screen.blit(shooter.image, shooter.rect)
            screen.blit(finish_goal.image, finish_goal.rect)
            for proj in projectiles: screen.blit(proj.image, proj.rect)
            player_draw_rect = player.get_draw_rect()
            screen.blit(player.image, player_draw_rect)
            # --- End static draw ---

            pause_result = pause_menu(screen)
            if pause_result == "resume":
                paused = False
            elif pause_result == "menu":
                return "menu" # Allow returning to main menu from pause
            continue # Skip rest of the loop if paused

        # --- Only update game state if not paused ---
        # --- Pass player_ref AND dt ---
        player.update(pygame.key.get_pressed(), current_time_sec, "clear", shop_upgrades={}, inverse=True,
                      wind_direction=None, player_ref=player, dt=dt)  # <<< Ensure dt is passed
        # --- REMOVED Ability activation shake check ---

        # --- FIX: Correct speed modifier for Mesky ---
        effective_speed_modifier_for_updates = 1.0
        if player.character == 3 and player.ability_active:
            effective_speed_modifier_for_updates = 0.5 # Apply 50% slow
        # --- END FIX ---


        shooters.update(current_time_sec, projectiles, player)
        all_enemies = enemies.sprites()
        for i, enemy in enumerate(all_enemies):
            other_enemies_list_for_collision = all_enemies[i+1:]
            # <<< CHANGE: Pass None for player ref to avoid homing >>>
            enemy.update(player=None, speed_modifier=effective_speed_modifier_for_updates, dt=dt, other_enemies=other_enemies_list_for_collision)
            # <<< END CHANGE >>>


        projectiles.update(dt=dt, speed_modifier=1.0) # Projectiles not slowed by Mesky
        finish_goal.update(dt=dt)
        # --- Update ability effects & particles ---
        minigame_ability_effects.update(dt, player) # Pass player ref
        particles.update(dt)

        # <<< REMOVED local collide_circle_mg3_player function >>>

        # --- Collision checks (only if not invincible) ---
        if current_time_sec >= player.invincible_until:
            # <<< CHANGE: Use passed-in collision_func >>>
            if pygame.sprite.spritecollideany(player, enemies, collision_func):
                if os.path.exists(DEAD_SOUND) and pygame.mixer.get_init():
                    try: pygame.mixer.Sound(DEAD_SOUND).play()
                    except pygame.error as e: print(f"Minigame dead sound error: {e}")
                return False # Return loss

            collided_projectile = pygame.sprite.spritecollideany(player, projectiles, collision_func)
            if collided_projectile:
                 if os.path.exists(DEAD_SOUND) and pygame.mixer.get_init():
                     try: pygame.mixer.Sound(DEAD_SOUND).play()
                     except pygame.error as e: print(f"Minigame dead sound error: {e}")
                 collided_projectile.kill() # Remove the projectile
                 return False # Return loss
            # <<< END CHANGE >>>
        # --- End Collision Checks ---

        # --- Win condition ---
        # <<< CHANGE: Use passed-in collision_func for goal collision >>>
        if collision_func(player, finish_goal):
        # <<< END CHANGE >>>
            # Optionally play win sound
            return True # Return win
        # --- End of game updates ---

        # --- Drawing (No Camera Offset) ---
        if bg_minigame: screen.blit(bg_minigame, (0,0))
        else: screen.fill(BLACK)

        # Draw game elements at absolute rect positions
        for enemy in enemies: screen.blit(enemy.image, enemy.rect)
        for shooter in shooters: screen.blit(shooter.image, shooter.rect)
        screen.blit(finish_goal.image, finish_goal.rect)
        for proj in projectiles:
             screen.blit(proj.image, proj.rect)
             # Trail drawing (absolute coords)
             trail_length_proj = 15
             if abs(proj.vel_x) > 0.1 or abs(proj.vel_y) > 0.1:
                vel_mag_proj = math.hypot(proj.vel_x, proj.vel_y)
                if vel_mag_proj > 0:
                    start_x_p = proj.rect.centerx - proj.vel_x * (trail_length_proj / vel_mag_proj)
                    start_y_p = proj.rect.centery - proj.vel_y * (trail_length_proj / vel_mag_proj)
                    try: pygame.draw.line(screen, proj.color, (int(start_x_p), int(start_y_p)), proj.rect.center, 2)
                    except TypeError: pass
        for p in particles: screen.blit(p.image, p.rect)

        # Player Trail Drawing
        player_trail_color = PLAYER_TRAIL_COLORS.get(player.character, TRAIL_COLOR_DEFAULT)
        for i, pos in enumerate(player.trail):
            alpha = int(255 * (i / player.trail_length) * 0.5 * player.trail_intensity_multiplier)
            alpha = max(0, min(255, alpha))
            trail_surf = pygame.Surface((player.trail_segment_size, player.trail_segment_size), pygame.SRCALPHA)
            draw_color = (*player_trail_color, alpha)
            pygame.draw.circle(trail_surf, draw_color, (player.trail_segment_size//2, player.trail_segment_size//2), player.trail_segment_size//2)
            draw_pos_x = pos[0] - player.trail_segment_size//2
            draw_pos_y = pos[1] - player.trail_segment_size//2
            screen.blit(trail_surf, (draw_pos_x, draw_pos_y))


        # Player Drawing
        player_draw_rect = player.get_draw_rect()
        screen.blit(player.image, player_draw_rect)

        # --- Draw Shield Aura (No Offset) ---
        # Also draws temp shields and permanent shields
        draw_shield_aura(screen, player, current_time_sec)
        # --- End Shield Aura ---

        # --- Draw Ability Effects ---
        for effect in minigame_ability_effects: screen.blit(effect.image, effect.rect)

        # --- UI Elements (No offset needed) ---
        title_text = FONT_MD.render("Inverse Gauntlet - Reach the Portal!", True, RED)
        title_rect_base = title_text.get_rect(centerx=SCREEN_WIDTH // 2, top=60) # Moved title down
        screen.blit(title_text, title_rect_base)

        # Draw ability icon HUD
        draw_ability_icon(screen, player, current_time_sec)
        # --- End Drawing ---

        pygame.mouse.set_visible(True)
        pygame.display.flip()

    # Should not be reached if collision/win logic is correct
    print("Warning: Minigame 3 loop exited unexpectedly.")
    return False