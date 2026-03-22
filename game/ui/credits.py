"""
SPLIT — Credits Corridor
Interactive walkable credits scene. Player walks right through a torch-lit
corridor past team pedestals, build tools, timeline, and a final thank-you
door that leads to a post-credits desert scene.
"""
import pygame
import math
from game.engine.settings import (
    SCREEN_W, SCREEN_H, FPS,
    CTRL_A, CTRL_B, CTRL_Y, CTRL_PLUS,
    AXIS_LX, STICK_DEADZONE,
    JELLO_GREEN, JELLO_GREEN_DIM, TORCH_AMBER, TORCH_GLOW, EMBER,
    WHITE, BLACK,
    FONT_TITLE, FONT_SUBTITLE, FONT_PROMPT, FONT_SMALL, FONT_NARRATOR,
    NARRATOR_LINES, GameEvent,
    PLAYER_SPEED,
)

# ── Corridor dimensions ──
CORRIDOR_W = 4000
CORRIDOR_H = 720
FLOOR_Y = CORRIDOR_H - 100

# ── Team data ──
TEAM_MEMBERS = [
    {
        'name': "ETHAN",
        'color': JELLO_GREEN,
        'quote': "I learned that games are harder to make than I thought, but way more fun.",
        'x': 300,
    },
    {
        'name': "EINS",
        'color': (80, 140, 240),  # blue
        'quote': "Designing a game with my friends was the best project ever.",
        'x': 500,
    },
    {
        'name': "ANDREW",
        'color': (180, 80, 220),  # purple
        'quote': "I drew all the characters and it was awesome seeing them move.",
        'x': 700,
    },
    {
        'name': "NATHAN",
        'color': (240, 160, 50),  # orange
        'quote': "I liked making the enemies and figuring out how to beat them.",
        'x': 900,
    },
]

# ── Built With plaques ──
PLAQUES = [
    {"text": "Claude AI -- Our engineering partner", "x": 1300},
    {"text": "Raspberry Pi 5 -- Our game computer", "x": 1500},
    {"text": "Python + Pygame -- Our tools", "x": 1700},
    {"text": "LASD Illuminate -- Our exhibition", "x": 1900},
]

# ── Timeline entries ──
TIMELINE = [
    {"label": "Session 1: Dream", "x": 2300},
    {"label": "Session 2: Design", "x": 2500},
    {"label": "Session 3: Blueprint", "x": 2700},
    {"label": "Session 4: Build", "x": 2900},
    {"label": "Session 5: Polish", "x": 3100},
]

# ── Torch positions (world x) ──
TORCH_POSITIONS = [150, 450, 750, 1050, 1350, 1650, 1950, 2250, 2550, 2850, 3150, 3500]

# ── Thank-you section ──
THANK_YOU_X = 3500
EXIT_DOOR_X = 3700


def _lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def _draw_torch(screen, x, y, frame):
    """Draw an animated wall torch at screen coordinates."""
    # Torch bracket
    pygame.draw.rect(screen, (100, 80, 60), (x - 4, y, 8, 20))
    # Flame (flickering)
    flicker = math.sin(frame * 0.15 + x * 0.1) * 3
    flame_h = int(18 + flicker)
    flame_w = int(10 + math.sin(frame * 0.2 + x) * 2)
    # Glow
    glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    glow_alpha = int(40 + 15 * math.sin(frame * 0.1 + x * 0.05))
    pygame.draw.circle(glow_surf, (245, 230, 200, glow_alpha), (40, 40), 40)
    screen.blit(glow_surf, (x - 40, y - 50))
    # Outer flame
    pygame.draw.ellipse(
        screen, TORCH_AMBER,
        (x - flame_w // 2, y - flame_h, flame_w, flame_h)
    )
    # Inner flame
    inner_h = flame_h * 2 // 3
    inner_w = flame_w * 2 // 3
    pygame.draw.ellipse(
        screen, TORCH_GLOW,
        (x - inner_w // 2, y - inner_h, inner_w, inner_h)
    )


def _draw_pedestal(screen, x, y, color, name, font):
    """Draw a colored stone pedestal with a jello cube on top."""
    # Pedestal base
    base_w = 60
    base_h = 50
    pygame.draw.rect(screen, (80, 75, 70), (x - base_w // 2, y - base_h, base_w, base_h))
    pygame.draw.rect(screen, (100, 95, 88), (x - base_w // 2, y - base_h, base_w, base_h), 2)
    # Top slab
    pygame.draw.rect(screen, (110, 105, 95), (x - base_w // 2 - 5, y - base_h - 6, base_w + 10, 8))

    # Jello cube on top
    cube_size = 22
    cube_y = y - base_h - 6 - cube_size
    pygame.draw.rect(screen, color, (x - cube_size // 2, cube_y, cube_size, cube_size))
    # Highlight
    hl_color = tuple(min(255, c + 60) for c in color[:3])
    pygame.draw.line(screen, hl_color, (x - cube_size // 2, cube_y), (x + cube_size // 2, cube_y), 2)
    pygame.draw.line(screen, hl_color, (x - cube_size // 2, cube_y), (x - cube_size // 2, cube_y + cube_size), 1)
    # Outline
    pygame.draw.rect(screen, WHITE, (x - cube_size // 2, cube_y, cube_size, cube_size), 1)

    # Name below pedestal
    name_surf = font.render(name, True, color)
    name_rect = name_surf.get_rect(midtop=(x, y + 6))
    screen.blit(name_surf, name_rect)


def _draw_speech_bubble(screen, x, y, text, font, alpha=255):
    """Draw a speech bubble with wrapped text above a position."""
    # Word wrap
    words = text.split()
    lines = []
    current_line = ""
    max_width = 280
    for word in words:
        test = current_line + (" " if current_line else "") + word
        if font.size(test)[0] > max_width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)

    line_h = font.get_linesize()
    bubble_h = line_h * len(lines) + 20
    bubble_w = max_width + 20
    bubble_x = x - bubble_w // 2
    bubble_y = y - bubble_h - 20

    # Bubble background
    bubble_surf = pygame.Surface((bubble_w, bubble_h + 12), pygame.SRCALPHA)
    pygame.draw.rect(
        bubble_surf, (20, 20, 30, min(255, alpha)),
        (0, 0, bubble_w, bubble_h), border_radius=8
    )
    pygame.draw.rect(
        bubble_surf, (200, 200, 200, min(255, alpha)),
        (0, 0, bubble_w, bubble_h), 2, border_radius=8
    )
    # Triangle pointer
    pygame.draw.polygon(
        bubble_surf, (20, 20, 30, min(255, alpha)),
        [(bubble_w // 2 - 8, bubble_h), (bubble_w // 2 + 8, bubble_h), (bubble_w // 2, bubble_h + 10)]
    )

    # Text
    for i, line in enumerate(lines):
        line_surf = font.render(line, True, WHITE)
        line_surf.set_alpha(alpha)
        bubble_surf.blit(line_surf, (10, 10 + i * line_h))

    screen.blit(bubble_surf, (bubble_x, bubble_y))


def _draw_plaque(screen, x, y, text, font):
    """Draw a wall plaque (rectangle with text)."""
    text_surf = font.render(text, True, TORCH_GLOW)
    tw, th = text_surf.get_size()
    plaque_w = tw + 30
    plaque_h = th + 20
    plaque_rect = pygame.Rect(x - plaque_w // 2, y - plaque_h // 2, plaque_w, plaque_h)
    pygame.draw.rect(screen, (50, 45, 40), plaque_rect)
    pygame.draw.rect(screen, TORCH_AMBER, plaque_rect, 2)
    screen.blit(text_surf, (x - tw // 2, y - th // 2))


def _draw_timeline_frame(screen, x, y, label, font):
    """Draw a framed timeline painting."""
    text_surf = font.render(label, True, WHITE)
    tw, th = text_surf.get_size()
    frame_w = tw + 40
    frame_h = th + 60
    # Painting background
    pygame.draw.rect(
        screen, (30, 28, 35),
        (x - frame_w // 2, y - frame_h // 2, frame_w, frame_h)
    )
    # Amber frame border (double border for depth)
    pygame.draw.rect(
        screen, TORCH_AMBER,
        (x - frame_w // 2, y - frame_h // 2, frame_w, frame_h), 3
    )
    pygame.draw.rect(
        screen, EMBER,
        (x - frame_w // 2 + 5, y - frame_h // 2 + 5, frame_w - 10, frame_h - 10), 1
    )
    # Text centered
    screen.blit(text_surf, (x - tw // 2, y - th // 2))


def _draw_credits_player(screen, x, y, frame):
    """Draw the jello player character for credits walking."""
    # Body bob
    bob = math.sin(frame * 0.12) * 2
    body_rect = pygame.Rect(x - 16, y - 30 + int(bob), 32, 30)
    pygame.draw.ellipse(screen, JELLO_GREEN, body_rect)
    pygame.draw.ellipse(screen, JELLO_GREEN_DIM, body_rect, 2)

    # Eyes
    eye_y = y - 22 + int(bob)
    pygame.draw.circle(screen, WHITE, (x - 5, eye_y), 4)
    pygame.draw.circle(screen, WHITE, (x + 5, eye_y), 4)
    pygame.draw.circle(screen, BLACK, (x - 4, eye_y), 2)
    pygame.draw.circle(screen, BLACK, (x + 6, eye_y), 2)


def _run_post_credits(screen, clock, joystick=None):
    """
    Post-credits desert scene. 5 seconds.
    Desert, jello silhouette, 'HARD MODE UNLOCKED', castle on horizon.
    """
    font_title = pygame.font.Font(None, FONT_TITLE)
    font_narrator = pygame.font.Font(None, FONT_NARRATOR)
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    try:
        font_mono = pygame.font.SysFont("monospace", FONT_NARRATOR)
    except Exception:
        font_mono = pygame.font.Font(None, FONT_NARRATOR)

    narrator_line = NARRATOR_LINES.get(
        GameEvent.POST_CREDITS,
        "This was always their game. I just opened the door."
    )

    total_frames = 5 * FPS  # 5 seconds
    frame = 0

    while frame < total_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            # No skip for post-credits -- let it play out
            # But allow A/Space to exit early
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return
            if event.type == pygame.JOYBUTTONDOWN and joystick:
                if event.button == CTRL_A or event.button == CTRL_PLUS:
                    return

        screen.fill(BLACK)

        # ── Sky gradient (top half: blue sky) ──
        sky_top = (60, 120, 200)
        sky_bottom = (180, 200, 220)
        horizon_y = SCREEN_H // 2 + 40
        for y in range(horizon_y):
            t = y / horizon_y
            r = int(_lerp(sky_top[0], sky_bottom[0], t))
            g = int(_lerp(sky_top[1], sky_bottom[1], t))
            b = int(_lerp(sky_top[2], sky_bottom[2], t))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))

        # ── Sand gradient (bottom half) ──
        sand_top = (210, 190, 140)
        sand_bottom = (180, 160, 110)
        for y in range(horizon_y, SCREEN_H):
            t = (y - horizon_y) / (SCREEN_H - horizon_y)
            r = int(_lerp(sand_top[0], sand_bottom[0], t))
            g = int(_lerp(sand_top[1], sand_bottom[1], t))
            b = int(_lerp(sand_top[2], sand_bottom[2], t))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))

        # ── Castle silhouette on horizon (right side) ──
        castle_alpha_t = min(1.0, frame / 90.0)
        castle_color = (40, 40, 60)
        # Main tower
        cx = SCREEN_W - 300
        cy = horizon_y
        # Towers
        towers = [
            (cx - 60, cy - 80, 30, 80),
            (cx - 20, cy - 120, 40, 120),
            (cx + 30, cy - 90, 30, 90),
            (cx + 70, cy - 70, 25, 70),
        ]
        # Castle wall
        pygame.draw.rect(screen, castle_color, (cx - 80, cy - 40, 180, 40))
        for tx, ty, tw, th in towers:
            pygame.draw.rect(screen, castle_color, (tx, ty, tw, th))
            # Crenellations
            for bx in range(tx, tx + tw, 8):
                pygame.draw.rect(screen, castle_color, (bx, ty - 6, 5, 6))

        # ── Jello silhouette at center ──
        jello_x = SCREEN_W // 2
        jello_y = horizon_y + 20
        jello_color = (30, 30, 40)
        pygame.draw.ellipse(
            screen, jello_color,
            (jello_x - 20, jello_y - 24, 40, 30)
        )

        # ── "HARD MODE UNLOCKED." text fading in ──
        if frame > 60:
            text_alpha = min(255, (frame - 60) * 4)
            hm_surf = font_title.render("HARD MODE UNLOCKED.", True, WHITE)
            hm_surf.set_alpha(text_alpha)
            hm_rect = hm_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 120))
            screen.blit(hm_surf, hm_rect)

        # ── Narrator line at top center (monospace) ──
        if frame > 120:
            nar_alpha = min(255, (frame - 120) * 3)
            nar_surf = font_mono.render(narrator_line, True, (200, 200, 200))
            nar_surf.set_alpha(nar_alpha)
            nar_rect = nar_surf.get_rect(midtop=(SCREEN_W // 2, 40))
            screen.blit(nar_surf, nar_rect)

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1


def run_credits(screen, clock, joystick=None):
    """
    Interactive walkable credits corridor.
    Walk left/right through sections: Team, Built With, Timeline, Thank You.
    Y/C to interact with pedestals. A/Space/Plus to skip.
    """
    font_title = pygame.font.Font(None, FONT_TITLE)
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)
    font_small = pygame.font.Font(None, FONT_SMALL)

    # Player state
    player_x = 100.0
    player_speed = PLAYER_SPEED * 1.2  # slightly faster for credits walking

    # Camera
    camera_x = 0.0

    # Speech bubble state: {member_index: frames_remaining}
    active_bubbles = {}
    BUBBLE_DURATION = 4 * FPS  # 4 seconds

    # Exit door interaction
    exiting = False
    exit_fade = 0

    frame = 0
    running = True

    while running:
        # ── Events ──
        move_dir = 0
        interact_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                # Skip entire credits
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    _run_post_credits(screen, clock, joystick)
                    return
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_c:
                    interact_pressed = True

            if event.type == pygame.JOYBUTTONDOWN and joystick:
                if event.button == CTRL_A or event.button == CTRL_PLUS:
                    _run_post_credits(screen, clock, joystick)
                    return
                if event.button == CTRL_B:
                    return
                if event.button == CTRL_Y:
                    interact_pressed = True

        # ── Continuous input (held keys / stick) ──
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_RIGHT]:
            move_dir += 1

        if joystick:
            lx = joystick.get_axis(AXIS_LX)
            if lx < -STICK_DEADZONE:
                move_dir = -1
            elif lx > STICK_DEADZONE:
                move_dir = 1

        # ── Update player position ──
        if not exiting:
            player_x += move_dir * player_speed
            player_x = max(30, min(CORRIDOR_W - 30, player_x))

        # ── Camera follows player ──
        target_camera = player_x - SCREEN_W // 2
        target_camera = max(0, min(CORRIDOR_W - SCREEN_W, target_camera))
        camera_x += (target_camera - camera_x) * 0.1  # smooth follow

        # ── Interact with pedestals ──
        if interact_pressed and not exiting:
            for i, member in enumerate(TEAM_MEMBERS):
                dist = abs(player_x - member['x'])
                if dist < 60:
                    active_bubbles[i] = BUBBLE_DURATION

        # ── Update bubble timers ──
        expired = []
        for idx in active_bubbles:
            active_bubbles[idx] -= 1
            if active_bubbles[idx] <= 0:
                expired.append(idx)
        for idx in expired:
            del active_bubbles[idx]

        # ── Check exit door ──
        if not exiting and abs(player_x - EXIT_DOOR_X) < 50:
            # Auto-trigger exit when walking into the door
            if move_dir > 0 and player_x > EXIT_DOOR_X - 30:
                exiting = True

        if exiting:
            exit_fade += 4
            if exit_fade >= 255:
                _run_post_credits(screen, clock, joystick)
                return

        # ── Draw ──
        screen.fill(BLACK)

        cam = int(camera_x)

        # ── Background: dark corridor ──
        # Wall gradient
        for y in range(FLOOR_Y):
            t = y / FLOOR_Y
            r = int(_lerp(18, 30, t))
            g = int(_lerp(16, 28, t))
            b = int(_lerp(22, 38, t))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))

        # Floor
        pygame.draw.rect(screen, (40, 36, 32), (0, FLOOR_Y, SCREEN_W, SCREEN_H - FLOOR_Y))
        pygame.draw.line(screen, (60, 55, 48), (0, FLOOR_Y), (SCREEN_W, FLOOR_Y), 2)

        # Floor stone pattern
        for fx in range(0, CORRIDOR_W, 48):
            sx = fx - cam
            if -48 < sx < SCREEN_W + 48:
                pygame.draw.rect(
                    screen, (50, 45, 40),
                    (sx, FLOOR_Y + 2, 46, SCREEN_H - FLOOR_Y - 2), 1
                )

        # Wall stone pattern
        for wx in range(0, CORRIDOR_W, 64):
            sx = wx - cam
            if -64 < sx < SCREEN_W + 64:
                for wy in range(0, FLOOR_Y, 48):
                    pygame.draw.rect(
                        screen, (35, 32, 42),
                        (sx, wy, 62, 46), 1
                    )

        # ── Torches ──
        for tx in TORCH_POSITIONS:
            sx = tx - cam
            if -50 < sx < SCREEN_W + 50:
                _draw_torch(screen, sx, 160, frame)

        # ── Section 1: Team Pedestals ──
        for i, member in enumerate(TEAM_MEMBERS):
            sx = member['x'] - cam
            if -150 < sx < SCREEN_W + 150:
                _draw_pedestal(screen, sx, FLOOR_Y, member['color'], member['name'], font_sub)

                # Interaction hint when player is nearby
                dist = abs(player_x - member['x'])
                if dist < 60 and i not in active_bubbles:
                    hint_surf = font_small.render("[Y] Read", True, (150, 150, 150))
                    hint_rect = hint_surf.get_rect(midtop=(sx, FLOOR_Y + 30))
                    screen.blit(hint_surf, hint_rect)

                # Speech bubble
                if i in active_bubbles:
                    remaining = active_bubbles[i]
                    # Fade out in last 30 frames
                    if remaining < 30:
                        alpha = int(255 * remaining / 30)
                    else:
                        alpha = 255
                    _draw_speech_bubble(
                        screen, sx, FLOOR_Y - 100,
                        member['quote'], font_small, alpha
                    )

        # ── Section 2: Built With plaques ──
        for plaque in PLAQUES:
            sx = plaque['x'] - cam
            if -200 < sx < SCREEN_W + 200:
                _draw_plaque(screen, sx, 250, plaque['text'], font_small)

        # ── Section 3: Timeline ──
        for entry in TIMELINE:
            sx = entry['x'] - cam
            if -150 < sx < SCREEN_W + 150:
                _draw_timeline_frame(screen, sx, 280, entry['label'], font_prompt)

        # ── Section 4: Thank You ──
        thank_sx = THANK_YOU_X - cam
        if -300 < thank_sx < SCREEN_W + 300:
            ty_surf = font_title.render("THANK YOU FOR PLAYING", True, WHITE)
            ty_rect = ty_surf.get_rect(center=(thank_sx, 200))
            screen.blit(ty_surf, ty_rect)

        # ── Exit door ──
        door_sx = EXIT_DOOR_X - cam
        if -100 < door_sx < SCREEN_W + 100:
            door_w = 60
            door_h = 120
            door_rect = pygame.Rect(door_sx - door_w // 2, FLOOR_Y - door_h, door_w, door_h)

            # Glow
            glow_pulse = int(40 + 20 * math.sin(frame * 0.08))
            glow_surf = pygame.Surface((door_w + 40, door_h + 40), pygame.SRCALPHA)
            glow_surf.fill((255, 255, 255, glow_pulse))
            screen.blit(glow_surf, (door_sx - door_w // 2 - 20, FLOOR_Y - door_h - 20))

            # Door (bright white)
            pygame.draw.rect(screen, WHITE, door_rect)
            pygame.draw.rect(screen, (200, 200, 220), door_rect, 2)

        # ── Player ──
        player_sx = int(player_x - camera_x)
        _draw_credits_player(screen, player_sx, FLOOR_Y, frame)

        # ── Controls hint (bottom) ──
        controls = font_small.render(
            "[Left/Right] Walk    [Y/C] Interact    [A/Space] Skip",
            True, (100, 100, 100)
        )
        controls_rect = controls.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H - 10))
        screen.blit(controls, controls_rect)

        # ── Exit fade overlay ──
        if exiting and exit_fade > 0:
            fade_surf = pygame.Surface((SCREEN_W, SCREEN_H))
            fade_surf.fill(WHITE)
            fade_surf.set_alpha(min(255, exit_fade))
            screen.blit(fade_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1
