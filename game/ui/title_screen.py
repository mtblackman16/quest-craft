"""
SPLIT -- Title Screen
Dark dungeon aesthetic with animated jello cube, difficulty selection,
particles, torch glow, Konami code, controller hot-plug, attract mode timer.
"""

import math
import random

import pygame

from game.engine.settings import (
    SCREEN_W,
    SCREEN_H,
    FPS,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_PROMPT,
    FONT_SMALL,
    JELLO_GREEN,
    JELLO_GREEN_DIM,
    TORCH_AMBER,
    TORCH_GLOW,
    WHITE,
    BLACK,
    Difficulty,
    CTRL_A,
    CTRL_B,
    CTRL_PLUS,
    AXIS_LX,
    AXIS_LY,
    STICK_DEADZONE,
)
from game.engine.sprites import load_sprite


# ---------------------------------------------------------------------------
# Konami sequence
# ---------------------------------------------------------------------------

_KONAMI = [
    pygame.K_UP, pygame.K_UP,
    pygame.K_DOWN, pygame.K_DOWN,
    pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_b, pygame.K_a,
]


# ---------------------------------------------------------------------------
# Dust / jello particle
# ---------------------------------------------------------------------------

class _Mote:
    __slots__ = ("x", "y", "vx", "vy", "size", "color", "alpha", "life", "max_life")

    def __init__(self, x, y, color, size, life, vx=0.0, vy=-0.4):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alpha = 255
        self.life = life
        self.max_life = life


# ---------------------------------------------------------------------------
# Title helpers
# ---------------------------------------------------------------------------

def _make_gradient(w, h, top_color, bot_color):
    """Create a vertical gradient surface."""
    surf = pygame.Surface((w, h))
    for row in range(h):
        t = row / max(h - 1, 1)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, row), (w - 1, row))
    return surf


def _make_vignette(w, h, strength=180):
    """Create a radial vignette overlay."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    max_dist = math.sqrt(cx * cx + cy * cy)
    # Draw rings from outside in
    for r in range(int(max_dist), 0, -4):
        t = r / max_dist
        alpha = int(strength * (t * t))
        alpha = min(alpha, 255)
        pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r)
    return surf


def _draw_jello_cube(surf, cx, cy, frame, squish_phase):
    """Draw an animated jello cube with squish, bob, and eyes."""
    # Bob up and down
    bob = math.sin(frame * 0.04) * 4
    cy_off = int(cy + bob)

    # Squish: width and height oscillate
    base_w = 48
    base_h = 48
    squish = math.sin(squish_phase) * 0.08
    w = int(base_w * (1.0 + squish))
    h = int(base_h * (1.0 - squish))

    # Body
    body_rect = pygame.Rect(cx - w // 2, cy_off - h // 2, w, h)
    body_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_surf.fill((100, 210, 80, 140))
    # Rounded corners
    pygame.draw.rect(body_surf, (125, 223, 100, 180), (0, 0, w, h), border_radius=8)
    surf.blit(body_surf, body_rect.topleft)

    # Outline
    pygame.draw.rect(surf, JELLO_GREEN, body_rect, 2, border_radius=8)

    # Eyes — look around slowly
    look_x = math.sin(frame * 0.02) * 3
    look_y = math.cos(frame * 0.015) * 2
    eye_y = cy_off - 4
    # Left eye
    le_x = cx - 8 + int(look_x)
    pygame.draw.circle(surf, WHITE, (le_x, eye_y), 5)
    pygame.draw.circle(surf, BLACK, (le_x + int(look_x * 0.5), eye_y + int(look_y * 0.5)), 2)
    # Right eye
    re_x = cx + 8 + int(look_x)
    pygame.draw.circle(surf, WHITE, (re_x, eye_y), 5)
    pygame.draw.circle(surf, BLACK, (re_x + int(look_x * 0.5), eye_y + int(look_y * 0.5)), 2)


# ---------------------------------------------------------------------------
# run_title_screen
# ---------------------------------------------------------------------------

DIFFICULTY_OPTIONS = [
    (Difficulty.EASY, "Easy", "Generous checkpoints"),
    (Difficulty.NORMAL, "Normal", "The intended experience"),
    (Difficulty.HARD, "Hard", "No checkpoints. +25% damage."),
    (Difficulty.EARTHQUAKE, "Earthquake Mode", "Timed. Nothing respawns. Good luck."),
    ("credits", "Credits", "Meet the team behind SPLIT"),
]

FADE_IN_FRAMES = 80
ATTRACT_TIMEOUT = 120 * FPS  # 120 seconds


def run_title_screen(screen, clock, joystick=None):
    """Run the title screen loop.

    Returns
    -------
    Difficulty or None
        The selected difficulty, or None if the player quit / attract timeout.
    """
    pygame.font.init()

    font_title = pygame.font.Font(None, FONT_TITLE)
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)
    font_small = pygame.font.Font(None, FONT_SMALL)

    # Pre-render background
    bg = _make_gradient(SCREEN_W, SCREEN_H, (18, 18, 36), (10, 10, 20))
    vignette = _make_vignette(SCREEN_W, SCREEN_H, 180)

    # Title letters
    title_text = "SPLIT"
    title_letters = []
    for i, ch in enumerate(title_text):
        rendered = font_title.render(ch, True, WHITE)
        glow = font_title.render(ch, True, JELLO_GREEN)
        title_letters.append({
            "char": ch,
            "surf": rendered,
            "glow": glow,
            "phase": i * 0.7,  # offset for bob
        })

    # Compute total title width for centering
    total_w = sum(l["surf"].get_width() for l in title_letters) + 6 * (len(title_letters) - 1)

    # Subtitle
    subtitle_surf = font_sub.render("A JELLO CUBE ADVENTURE", True, TORCH_AMBER)

    # Hints
    hint_kb = font_small.render("Arrow Keys / Space to select", True, (140, 140, 140))
    hint_ctrl = font_small.render("D-Pad / A to select", True, (140, 140, 140))

    # State
    selected = 1  # default to Normal
    frame = 0
    fade_alpha = 255  # starts opaque black, fades to 0
    idle_timer = 0
    konami_idx = 0
    konami_activated = False
    show_menu = False  # show after fade-in completes

    # Particles
    motes: list[_Mote] = []

    # Stick repeat helpers
    stick_held_frames = 0
    last_stick_dir = 0  # -1 up, 1 down, 0 neutral

    running = True
    while running:
        dt = clock.tick(FPS)
        frame += 1
        idle_timer += 1

        # Attract mode timeout
        if idle_timer >= ATTRACT_TIMEOUT:
            return None

        # Show menu after fade-in
        if frame >= FADE_IN_FRAMES:
            show_menu = True

        # -- events ----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            # Controller hot-plug
            if event.type == pygame.JOYDEVICEADDED:
                try:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                except pygame.error:
                    pass

            if event.type == pygame.JOYDEVICEREMOVED:
                joystick = None

            # Keyboard
            if event.type == pygame.KEYDOWN:
                idle_timer = 0
                key = event.key

                # Konami code tracking
                if key == _KONAMI[konami_idx]:
                    konami_idx += 1
                    if konami_idx >= len(_KONAMI):
                        konami_activated = True
                        konami_idx = 0
                else:
                    # Reset if wrong key but allow restarting
                    if key == _KONAMI[0]:
                        konami_idx = 1
                    else:
                        konami_idx = 0

                if show_menu:
                    if key == pygame.K_UP:
                        selected = (selected - 1) % len(DIFFICULTY_OPTIONS)
                    elif key == pygame.K_DOWN:
                        selected = (selected + 1) % len(DIFFICULTY_OPTIONS)
                    elif key in (pygame.K_SPACE, pygame.K_RETURN):
                        return DIFFICULTY_OPTIONS[selected][0]
                    elif key == pygame.K_ESCAPE:
                        return None

            # Controller buttons
            if event.type == pygame.JOYBUTTONDOWN and show_menu:
                idle_timer = 0
                if event.button == CTRL_A:
                    return DIFFICULTY_OPTIONS[selected][0]

            # Controller d-pad
            if event.type == pygame.JOYHATMOTION and show_menu:
                idle_timer = 0
                _, hat_y = event.value
                if hat_y == 1:  # up
                    selected = (selected - 1) % len(DIFFICULTY_OPTIONS)
                elif hat_y == -1:  # down
                    selected = (selected + 1) % len(DIFFICULTY_OPTIONS)

        # -- controller stick (with repeat) ----------------------------------
        if joystick and show_menu:
            try:
                ly = joystick.get_axis(AXIS_LY)
            except (pygame.error, IndexError):
                ly = 0.0

            if ly < -STICK_DEADZONE:
                stick_dir = -1
            elif ly > STICK_DEADZONE:
                stick_dir = 1
            else:
                stick_dir = 0

            if stick_dir != 0:
                if stick_dir != last_stick_dir:
                    # New direction
                    selected = (selected + stick_dir) % len(DIFFICULTY_OPTIONS)
                    stick_held_frames = 0
                    idle_timer = 0
                else:
                    stick_held_frames += 1
                    if stick_held_frames > 20 and stick_held_frames % 8 == 0:
                        selected = (selected + stick_dir) % len(DIFFICULTY_OPTIONS)
                        idle_timer = 0
            else:
                stick_held_frames = 0
            last_stick_dir = stick_dir

        # -- spawn particles (reduced count for Pi 5 performance) ------------
        # Dust motes (amber, float upward) — every 8 frames instead of 4
        if frame % 8 == 0:
            mx = random.uniform(0, SCREEN_W)
            my = random.uniform(SCREEN_H * 0.3, SCREEN_H)
            motes.append(_Mote(
                mx, my,
                color=TORCH_AMBER,
                size=random.randint(1, 2),
                life=random.randint(60, 120),
                vx=random.uniform(-0.2, 0.2),
                vy=random.uniform(-0.6, -0.2),
            ))
        # Green jello particles from bottom — every 12 frames instead of 6
        if frame % 12 == 0:
            mx = random.uniform(SCREEN_W * 0.3, SCREEN_W * 0.7)
            motes.append(_Mote(
                mx, SCREEN_H + 5,
                color=JELLO_GREEN,
                size=random.randint(2, 3),
                life=random.randint(80, 140),
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-1.0, -0.4),
            ))

        # Update motes
        alive_motes = []
        for m in motes:
            m.life -= 1
            if m.life <= 0:
                continue
            m.x += m.vx
            m.y += m.vy
            m.alpha = int(255 * (m.life / m.max_life))
            alive_motes.append(m)
        motes = alive_motes

        # -- draw ------------------------------------------------------------
        screen.blit(bg, (0, 0))

        # Torch glow at top-center
        glow_radius = int(120 + math.sin(frame * 0.05) * 15)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_alpha = int(30 + math.sin(frame * 0.07) * 10)
        pygame.draw.circle(
            glow_surf, (*TORCH_AMBER, glow_alpha),
            (glow_radius, glow_radius), glow_radius
        )
        screen.blit(glow_surf, (SCREEN_W // 2 - glow_radius, 20 - glow_radius // 2))

        # Particles (simple circles, no per-particle surface allocation)
        for m in motes:
            if m.alpha <= 0 or m.size <= 0:
                continue
            pygame.draw.circle(screen, m.color[:3],
                               (int(m.x), int(m.y)), m.size)

        # Vignette
        screen.blit(vignette, (0, 0))

        # Title letters — letter-by-letter bob
        title_y = 140
        cursor_x = SCREEN_W // 2 - total_w // 2
        for ltr in title_letters:
            bob = math.sin(frame * 0.05 + ltr["phase"]) * 5
            ly = int(title_y + bob)
            # Green glow behind
            gw = ltr["glow"]
            gw_faded = gw.copy()
            gw_faded.set_alpha(80)
            screen.blit(gw_faded, (cursor_x - 2, ly - 2))
            screen.blit(gw_faded, (cursor_x + 2, ly + 2))
            # Letter
            screen.blit(ltr["surf"], (cursor_x, ly))
            cursor_x += ltr["surf"].get_width() + 6

        # Subtitle
        sw = subtitle_surf.get_width()
        screen.blit(subtitle_surf, (SCREEN_W // 2 - sw // 2, 220))

        # Jello cube preview — use Andrew's 3/4 view if available
        _title_sprite = load_sprite('player/jello-cube-three-quarter.png', 120, 120)
        if _title_sprite:
            # Squish animation applied to sprite
            squish = math.sin(frame * 0.06) * 0.08
            sw = int(120 * (1.0 + squish))
            sh = int(120 * (1.0 - squish))
            bob = math.sin(frame * 0.04) * 4
            scaled = pygame.transform.scale(_title_sprite, (sw, sh))
            screen.blit(scaled, (SCREEN_W // 2 - sw // 2, int(310 - sh // 2 + bob)))
        else:
            _draw_jello_cube(screen, SCREEN_W // 2, 310, frame, frame * 0.06)

        # Difficulty menu
        if show_menu:
            menu_y = 400
            for i, (diff, label, desc) in enumerate(DIFFICULTY_OPTIONS):
                is_sel = (i == selected)
                color = JELLO_GREEN if is_sel else (100, 100, 100)
                label_surf = font_prompt.render(label, True, color)
                lw = label_surf.get_width()
                lx = SCREEN_W // 2 - lw // 2
                screen.blit(label_surf, (lx, menu_y))

                if is_sel:
                    # Draw arrow indicator
                    arrow = font_prompt.render(">", True, JELLO_GREEN)
                    screen.blit(arrow, (lx - 20, menu_y))
                    # Description
                    desc_surf = font_small.render(desc, True, (180, 180, 180))
                    dw = desc_surf.get_width()
                    screen.blit(desc_surf, (SCREEN_W // 2 - dw // 2, menu_y + 28))

                menu_y += 48

            # Controls hints at bottom
            hkw = hint_kb.get_width()
            hcw = hint_ctrl.get_width()
            screen.blit(hint_kb, (SCREEN_W // 2 - hkw // 2, SCREEN_H - 60))
            screen.blit(hint_ctrl, (SCREEN_W // 2 - hcw // 2, SCREEN_H - 36))

        # Konami activation flash
        if konami_activated:
            flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash_a = max(0, 200 - frame * 4)
            if flash_a > 0:
                flash.fill((255, 255, 255, flash_a))
                screen.blit(flash, (0, 0))
            # Secret counter in corner
            sec_txt = font_small.render("Secrets: 1/?", True, TORCH_AMBER)
            screen.blit(sec_txt, (SCREEN_W - sec_txt.get_width() - 12, SCREEN_H - 30))

        # Fade-in overlay (opaque black fading out)
        if frame < FADE_IN_FRAMES:
            fade_alpha = int(255 * (1.0 - frame / FADE_IN_FRAMES))
            fade_surf = pygame.Surface((SCREEN_W, SCREEN_H))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(fade_alpha)
            screen.blit(fade_surf, (0, 0))

        pygame.display.flip()

    return None
