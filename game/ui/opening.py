"""
SPLIT — Opening Cinematic
Played once before first gameplay. ~9 seconds of simple shape-based animation.
Skip at any time with A button or Space.
"""
import pygame
import math
import random
from game.engine.settings import (
    SCREEN_W, SCREEN_H, FPS,
    CTRL_A, CTRL_PLUS,
    JELLO_GREEN, JELLO_GREEN_DIM, TORCH_AMBER, TORCH_GLOW,
    WHITE, BLACK,
    FONT_SUBTITLE, FONT_PROMPT, FONT_SMALL,
    FLOOR_PALETTES,
)


def _should_skip(joystick):
    """Check for skip input (A/Space/Plus) in current event queue."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return True
        if event.type == pygame.JOYBUTTONDOWN and joystick:
            if event.button == CTRL_A or event.button == CTRL_PLUS:
                return True
    return False


def _lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * max(0.0, min(1.0, t))


def _fade_alpha(frame, fade_start, fade_end):
    """Return alpha 0-255 for a fade-in from fade_start to fade_end frames."""
    if frame < fade_start:
        return 0
    if frame >= fade_end:
        return 255
    t = (frame - fade_start) / max(1, fade_end - fade_start)
    return int(255 * t)


def run_opening(screen, clock, joystick=None):
    """
    Cinematic opening sequence. ~9 seconds total.
    All visuals use pygame drawing primitives (no images).
    Press A or Space to skip at any time.
    """
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)
    font_small = pygame.font.Font(None, FONT_SMALL)

    # Pre-generate pipe wall lines (random horizontal segments)
    pipe_lines = []
    for i in range(40):
        y_offset = i * 25
        width = random.randint(SCREEN_W // 3, SCREEN_W - 100)
        x_start = (SCREEN_W - width) // 2
        pipe_lines.append((x_start, y_offset, width))

    # Floor 1 palette for storage room
    deep_stone, warm_stone, floor_color, accent = FLOOR_PALETTES[1]

    # Total frames for the cinematic
    TOTAL_FRAMES = 540

    frame = 0
    while frame < TOTAL_FRAMES:
        # ── Skip check ──
        if _should_skip(joystick):
            return

        screen.fill(BLACK)

        # ================================================================
        # PHASE 1: Frames 0-119 — Black screen, text fades in
        # "the sound of falling through water"
        # ================================================================
        if frame < 120:
            alpha = _fade_alpha(frame, 20, 80)
            if alpha > 0:
                text_surf = font_prompt.render(
                    "the sound of falling through water", True, WHITE
                )
                text_surf.set_alpha(alpha)
                text_rect = text_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                screen.blit(text_surf, text_rect)

            # Subtle particle effect: small blue dots drifting down
            if frame > 30:
                for _ in range(2):
                    px = random.randint(SCREEN_W // 2 - 80, SCREEN_W // 2 + 80)
                    py = random.randint(0, SCREEN_H)
                    pa = random.randint(30, 100)
                    dot_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                    dot_surf.fill((100, 160, 220, pa))
                    screen.blit(dot_surf, (px, py))

        # ================================================================
        # PHASE 2: Frames 120-239 — Pipe interior parallax
        # ================================================================
        elif frame < 240:
            local_f = frame - 120
            scroll_speed = 8

            # Dark blue-gray gradient background
            for y in range(SCREEN_H):
                t = y / SCREEN_H
                r = int(_lerp(15, 35, t))
                g = int(_lerp(20, 45, t))
                b = int(_lerp(40, 70, t))
                pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))

            # Scrolling pipe wall lines
            for x_start, y_base, width in pipe_lines:
                y = (y_base + local_f * scroll_speed) % (SCREEN_H + 200) - 100
                # Left wall line
                pygame.draw.line(
                    screen, (50, 55, 75),
                    (x_start, y), (x_start + 30, y), 2
                )
                # Right wall line
                pygame.draw.line(
                    screen, (50, 55, 75),
                    (x_start + width - 30, y), (x_start + width, y), 2
                )
                # Pipe rivets
                if random.random() < 0.3:
                    pygame.draw.circle(
                        screen, (60, 65, 85),
                        (x_start + 5, int(y)), 3
                    )

            # Green blob (jello) tumbling in center
            blob_x = SCREEN_W // 2 + int(math.sin(local_f * 0.08) * 20)
            blob_y = SCREEN_H // 2 + int(math.sin(local_f * 0.12) * 10)
            blob_size = 18 + int(math.sin(local_f * 0.15) * 4)
            # Rotation effect via squish
            squish_x = blob_size + int(math.sin(local_f * 0.2) * 6)
            squish_y = blob_size - int(math.sin(local_f * 0.2) * 4)
            blob_rect = pygame.Rect(
                blob_x - squish_x, blob_y - squish_y,
                squish_x * 2, squish_y * 2
            )
            pygame.draw.ellipse(screen, JELLO_GREEN, blob_rect)
            pygame.draw.ellipse(screen, JELLO_GREEN_DIM, blob_rect, 2)

            # Small trailing particles
            for i in range(5):
                trail_y = blob_y - 10 - i * 12
                trail_alpha = max(0, 150 - i * 30)
                trail_size = max(2, 6 - i)
                trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    trail_surf, (125, 223, 100, trail_alpha),
                    (trail_size, trail_size), trail_size
                )
                screen.blit(
                    trail_surf,
                    (blob_x - trail_size + int(math.sin((local_f + i * 5) * 0.1) * 8),
                     trail_y - trail_size)
                )

        # ================================================================
        # PHASE 3: Frames 240-359 — Landing in storage room
        # ================================================================
        elif frame < 360:
            local_f = frame - 240

            # Impact flash at the very start
            if local_f < 8:
                flash_alpha = max(0, 255 - local_f * 32)
                screen.fill(WHITE)
                flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                flash_surf.fill((0, 0, 0, 255 - flash_alpha))
                screen.blit(flash_surf, (0, 0))
            else:
                # Dark room background (Floor 1 colors)
                screen.fill(deep_stone)

                # Stone floor
                floor_y = SCREEN_H - 120
                pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_W, 120))
                # Floor line
                pygame.draw.line(
                    screen, warm_stone,
                    (0, floor_y), (SCREEN_W, floor_y), 2
                )

                # Dim stone wall details
                for bx in range(0, SCREEN_W, 64):
                    for by in range(0, floor_y, 48):
                        pygame.draw.rect(
                            screen, warm_stone,
                            (bx, by, 62, 46), 1
                        )

                # Green blob settling on ground
                settle_t = min(1.0, local_f / 30.0)
                blob_y_start = SCREEN_H // 2 - 60
                blob_y_end = floor_y - 24
                blob_y = int(_lerp(blob_y_start, blob_y_end, settle_t))
                blob_x = SCREEN_W // 2

                # Squash on landing
                if settle_t < 1.0:
                    squash = 1.0 + (1.0 - settle_t) * 0.5
                    blob_w = int(20 * squash)
                    blob_h = int(20 / squash)
                else:
                    # Gentle breathing once settled
                    breath = math.sin((local_f - 30) * 0.05) * 2
                    blob_w = 20 + int(breath)
                    blob_h = 20 - int(breath)

                blob_rect = pygame.Rect(
                    blob_x - blob_w, blob_y - blob_h,
                    blob_w * 2, blob_h * 2
                )
                pygame.draw.ellipse(screen, JELLO_GREEN, blob_rect)
                pygame.draw.ellipse(screen, JELLO_GREEN_DIM, blob_rect, 2)

        # ================================================================
        # PHASE 4: Frames 360-419 — Shadow moves behind grate
        # ================================================================
        elif frame < 420:
            local_f = frame - 360

            # Same dark room
            screen.fill(deep_stone)
            floor_y = SCREEN_H - 120
            pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_W, 120))
            pygame.draw.line(screen, warm_stone, (0, floor_y), (SCREEN_W, floor_y), 2)

            # Stone wall
            for bx in range(0, SCREEN_W, 64):
                for by in range(0, floor_y, 48):
                    pygame.draw.rect(screen, warm_stone, (bx, by, 62, 46), 1)

            # Grate on the back wall (top area)
            grate_y = 80
            grate_h = 100
            grate_x = 200
            grate_w = SCREEN_W - 400
            # Grate bars
            for gx in range(grate_x, grate_x + grate_w, 20):
                pygame.draw.line(
                    screen, (60, 60, 80),
                    (gx, grate_y), (gx, grate_y + grate_h), 3
                )
            pygame.draw.rect(
                screen, (70, 70, 90),
                (grate_x, grate_y, grate_w, grate_h), 3
            )

            # Shadow silhouette moving behind grate
            shadow_x = int(_lerp(grate_x - 40, grate_x + grate_w + 40, local_f / 60.0))
            shadow_surf = pygame.Surface((80, grate_h - 10), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 120))
            screen.blit(shadow_surf, (shadow_x, grate_y + 5))

            # Amber key glow behind the figure
            key_glow_x = shadow_x + 40
            key_glow_y = grate_y + grate_h // 2
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (232, 168, 56, 100), (15, 15), 15)
            screen.blit(glow_surf, (key_glow_x - 15, key_glow_y - 15))
            pygame.draw.circle(screen, TORCH_AMBER, (key_glow_x, key_glow_y), 4)

            # Jello blob on the floor, still
            blob_x = SCREEN_W // 2
            blob_y = floor_y - 24
            blob_rect = pygame.Rect(blob_x - 20, blob_y - 18, 40, 36)
            pygame.draw.ellipse(screen, JELLO_GREEN, blob_rect)
            pygame.draw.ellipse(screen, JELLO_GREEN_DIM, blob_rect, 2)

        # ================================================================
        # PHASE 5: Frames 420-479 — Key slides under door
        # ================================================================
        elif frame < 480:
            local_f = frame - 420

            # Same dark room
            screen.fill(deep_stone)
            floor_y = SCREEN_H - 120
            pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_W, 120))
            pygame.draw.line(screen, warm_stone, (0, floor_y), (SCREEN_W, floor_y), 2)

            # Stone wall
            for bx in range(0, SCREEN_W, 64):
                for by in range(0, floor_y, 48):
                    pygame.draw.rect(screen, warm_stone, (bx, by, 62, 46), 1)

            # Door on the right side
            door_x = SCREEN_W - 200
            door_y = floor_y - 180
            door_w = 90
            door_h = 180
            pygame.draw.rect(screen, (50, 40, 35), (door_x, door_y, door_w, door_h))
            pygame.draw.rect(screen, (80, 70, 55), (door_x, door_y, door_w, door_h), 3)

            # Door glow effect (pulsing after key arrives)
            if local_f > 40:
                glow_alpha = int(80 + 40 * math.sin((local_f - 40) * 0.3))
                glow_surf = pygame.Surface((door_w + 20, door_h + 20), pygame.SRCALPHA)
                glow_surf.fill((232, 168, 56, glow_alpha))
                screen.blit(glow_surf, (door_x - 10, door_y - 10))
                # Redraw door on top
                pygame.draw.rect(screen, (50, 40, 35), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(screen, TORCH_AMBER, (door_x, door_y, door_w, door_h), 3)

            # Key sliding from left to door bottom
            key_t = min(1.0, local_f / 35.0)
            key_x = int(_lerp(50, door_x + door_w // 2 - 10, key_t))
            key_y = floor_y - 6
            # Small amber key rectangle
            pygame.draw.rect(screen, TORCH_AMBER, (key_x, key_y, 20, 6))
            pygame.draw.rect(screen, TORCH_GLOW, (key_x + 14, key_y - 3, 6, 12))
            # Key glow
            glow_surf = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (232, 168, 56, 60), (0, 0, 40, 20))
            screen.blit(glow_surf, (key_x - 10, key_y - 7))

            # Jello blob watching
            blob_x = SCREEN_W // 2
            blob_y = floor_y - 24
            blob_rect = pygame.Rect(blob_x - 20, blob_y - 18, 40, 36)
            pygame.draw.ellipse(screen, JELLO_GREEN, blob_rect)
            pygame.draw.ellipse(screen, JELLO_GREEN_DIM, blob_rect, 2)

        # ================================================================
        # PHASE 6: Frames 480-539 — Eyes open
        # ================================================================
        elif frame < 540:
            local_f = frame - 480

            # Same dark room
            screen.fill(deep_stone)
            floor_y = SCREEN_H - 120
            pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_W, 120))
            pygame.draw.line(screen, warm_stone, (0, floor_y), (SCREEN_W, floor_y), 2)

            # Stone wall
            for bx in range(0, SCREEN_W, 64):
                for by in range(0, floor_y, 48):
                    pygame.draw.rect(screen, warm_stone, (bx, by, 62, 46), 1)

            # Door (already glowing)
            door_x = SCREEN_W - 200
            door_y = floor_y - 180
            door_w = 90
            door_h = 180
            glow_alpha = int(60 + 30 * math.sin(local_f * 0.2))
            glow_surf = pygame.Surface((door_w + 20, door_h + 20), pygame.SRCALPHA)
            glow_surf.fill((232, 168, 56, glow_alpha))
            screen.blit(glow_surf, (door_x - 10, door_y - 10))
            pygame.draw.rect(screen, (50, 40, 35), (door_x, door_y, door_w, door_h))
            pygame.draw.rect(screen, TORCH_AMBER, (door_x, door_y, door_w, door_h), 2)

            # Jello blob
            blob_x = SCREEN_W // 2
            blob_y = floor_y - 24
            blob_rect = pygame.Rect(blob_x - 20, blob_y - 18, 40, 36)
            pygame.draw.ellipse(screen, JELLO_GREEN, blob_rect)
            pygame.draw.ellipse(screen, JELLO_GREEN_DIM, blob_rect, 2)

            # Eyes opening animation
            eye_open_t = min(1.0, local_f / 20.0)
            eye_y = blob_y - 6
            left_eye_x = blob_x - 7
            right_eye_x = blob_x + 7
            eye_radius = int(5 * eye_open_t)

            if eye_radius > 0:
                # White of eyes
                pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_radius)
                pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_radius)

                # Pupils (appear slightly after whites)
                if local_f > 10:
                    pupil_t = min(1.0, (local_f - 10) / 15.0)
                    pupil_r = int(3 * pupil_t)
                    if pupil_r > 0:
                        pygame.draw.circle(
                            screen, BLACK,
                            (left_eye_x + 1, eye_y), pupil_r
                        )
                        pygame.draw.circle(
                            screen, BLACK,
                            (right_eye_x + 1, eye_y), pupil_r
                        )

            # Fade to black at the very end
            if local_f > 45:
                fade_t = (local_f - 45) / 15.0
                fade_alpha = int(255 * min(1.0, fade_t))
                fade_surf = pygame.Surface((SCREEN_W, SCREEN_H))
                fade_surf.fill(BLACK)
                fade_surf.set_alpha(fade_alpha)
                screen.blit(fade_surf, (0, 0))

        # ── Skip hint (always visible, subtle) ──
        if frame > 30:
            skip_surf = font_small.render("[A] Skip", True, (80, 80, 80))
            screen.blit(skip_surf, (SCREEN_W - 120, SCREEN_H - 30))

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1
