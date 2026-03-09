"""
SPLIT -- Death Screen
Dark red-tinted background, green jello splatter particles, 'You Dissolved'
text, run counter, retry/quit selection.
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
    WHITE,
    BLACK,
    RED,
    CTRL_A,
    CTRL_B,
    CTRL_PLUS,
    AXIS_LY,
    STICK_DEADZONE,
)


# ---------------------------------------------------------------------------
# Splatter particle
# ---------------------------------------------------------------------------

class _Splatter:
    __slots__ = ("x", "y", "vx", "vy", "size", "life", "max_life", "color")

    def __init__(self, x, y):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.0, 7.0)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(3, 6)
        self.life = random.randint(40, 70)
        self.max_life = self.life
        # Vary green shades
        g = random.randint(180, 230)
        self.color = (random.randint(80, 130), g, random.randint(60, 110))


# ---------------------------------------------------------------------------
# run_death_screen
# ---------------------------------------------------------------------------

MENU_OPTIONS = ["Try Again", "Quit to Title"]
INPUT_DELAY = 30  # frames before accepting input


def run_death_screen(screen, clock, run_count, joystick=None):
    """Run the death screen loop.

    Returns
    -------
    str
        'retry' or 'quit'
    """
    pygame.font.init()

    font_title = pygame.font.Font(None, FONT_TITLE)
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)
    font_small = pygame.font.Font(None, FONT_SMALL)

    # Pre-render background: dark red tint
    bg = pygame.Surface((SCREEN_W, SCREEN_H))
    bg.fill((25, 8, 8))
    # Subtle red gradient overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    for row in range(SCREEN_H):
        t = row / max(SCREEN_H - 1, 1)
        alpha = int(30 * (1.0 - t))
        pygame.draw.line(overlay, (120, 20, 20, alpha), (0, row), (SCREEN_W - 1, row))
    bg.blit(overlay, (0, 0))

    # Spawn splatter particles from center
    cx = SCREEN_W // 2
    cy = SCREEN_H // 2
    particles = [_Splatter(cx, cy) for _ in range(40)]

    # State
    selected = 0
    frame = 0
    text_alpha = 0

    # Stick repeat
    stick_held_frames = 0
    last_stick_dir = 0

    running = True
    while running:
        clock.tick(FPS)
        frame += 1

        # Text fade-in
        if frame <= 30:
            text_alpha = int(255 * (frame / 30))
        else:
            text_alpha = 255

        can_accept_input = (frame > INPUT_DELAY)

        # -- events ----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # Controller hot-plug
            if event.type == pygame.JOYDEVICEADDED:
                try:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                except pygame.error:
                    pass

            if event.type == pygame.JOYDEVICEREMOVED:
                joystick = None

            if not can_accept_input:
                continue

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MENU_OPTIONS)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return "retry" if selected == 0 else "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

            # Controller buttons
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == CTRL_A:
                    return "retry" if selected == 0 else "quit"
                elif event.button == CTRL_B:
                    return "quit"

            # D-pad
            if event.type == pygame.JOYHATMOTION:
                _, hat_y = event.value
                if hat_y == 1:
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif hat_y == -1:
                    selected = (selected + 1) % len(MENU_OPTIONS)

        # -- controller stick ------------------------------------------------
        if joystick and can_accept_input:
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
                    selected = (selected + stick_dir) % len(MENU_OPTIONS)
                    stick_held_frames = 0
                else:
                    stick_held_frames += 1
                    if stick_held_frames > 20 and stick_held_frames % 8 == 0:
                        selected = (selected + stick_dir) % len(MENU_OPTIONS)
            else:
                stick_held_frames = 0
            last_stick_dir = stick_dir

        # -- update particles ------------------------------------------------
        alive = []
        for p in particles:
            p.life -= 1
            if p.life <= 0:
                continue
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.08  # slight gravity
            p.vx *= 0.97
            p.vy *= 0.97
            alive.append(p)
        particles = alive

        # -- draw ------------------------------------------------------------
        screen.blit(bg, (0, 0))

        # Particles
        for p in particles:
            t = p.life / p.max_life
            alpha = int(255 * t)
            if alpha <= 0:
                continue
            ps = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*p.color, alpha), (p.size, p.size), p.size)
            screen.blit(ps, (int(p.x) - p.size, int(p.y) - p.size))

        # "You Dissolved" text
        title_surf = font_title.render("You Dissolved", True, RED)
        if text_alpha < 255:
            title_surf.set_alpha(text_alpha)
        tw = title_surf.get_width()
        screen.blit(title_surf, (SCREEN_W // 2 - tw // 2, 200))

        # Run counter
        if text_alpha >= 255:
            run_surf = font_sub.render(f"Run #{run_count}", True, (180, 180, 180))
            rw = run_surf.get_width()
            screen.blit(run_surf, (SCREEN_W // 2 - rw // 2, 275))

        # Menu options
        if can_accept_input:
            menu_y = 380
            for i, label in enumerate(MENU_OPTIONS):
                is_sel = (i == selected)
                color = JELLO_GREEN if is_sel else (100, 100, 100)
                label_surf = font_prompt.render(label, True, color)
                lw = label_surf.get_width()
                lx = SCREEN_W // 2 - lw // 2
                screen.blit(label_surf, (lx, menu_y))
                if is_sel:
                    arrow = font_prompt.render(">", True, JELLO_GREEN)
                    screen.blit(arrow, (lx - 22, menu_y))
                menu_y += 48

        pygame.display.flip()

    return "quit"
