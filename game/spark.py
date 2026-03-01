"""
SPLIT — The Spark
A jello cube trapped in a dark castle. Your game. Your rules.
Built by Ethan (9), Eins (11), Nathan (9) & Andrew (11).
"""
import pygame
import sys
import math
import random

# ── Constants ──
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
GROUND_Y = 500

# ── Colors — Castle Interior palette ──
DEEP_STONE = (26, 26, 46)
WARM_STONE = (45, 45, 68)
TORCH_AMBER = (232, 168, 56)
TORCH_GLOW = (245, 230, 200)
JELLO_GREEN = (125, 223, 100)
JELLO_GREEN_DIM = (80, 160, 60)
JELLO_BODY = (100, 210, 80, 140)  # translucent green
EMBER = (196, 75, 43)
DARK_FLOOR = (35, 30, 50)
VINE_GREEN = (60, 100, 50)
STONE_HIGHLIGHT = (55, 55, 80)

# ── Initialize ──
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("SPLIT")
clock = pygame.time.Clock()

# Surfaces for translucency
jello_surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

# ── Fonts ──
font_title = pygame.font.Font(None, 72)
font_subtitle = pygame.font.Font(None, 28)
font_prompt = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 20)


# ═══════════════════════════════════════════════════════════
#  PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color, size=3, speed=0.5, lifetime=180, drift_x=0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size + random.uniform(-1, 1)
        self.speed = speed + random.uniform(-0.2, 0.2)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.drift_x = drift_x + random.uniform(-0.3, 0.3)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.y -= self.speed
        self.x += self.drift_x + math.sin(self.phase + pygame.time.get_ticks() * 0.002) * 0.3
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surf):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        s = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        color = (*self.color[:3], alpha)
        ps = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(ps, color, (s, s), s)
        surf.blit(ps, (int(self.x) - s, int(self.y) - s))


# ═══════════════════════════════════════════════════════════
#  COLLECTIBLE (jello powder)
# ═══════════════════════════════════════════════════════════
class Collectible:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.base_y = y
        self.color = color or random.choice([
            TORCH_AMBER, JELLO_GREEN, EMBER, (180, 120, 255), (255, 180, 60)
        ])
        self.size = 10
        self.alive = True
        self.phase = random.uniform(0, math.pi * 2)
        self.particles = []

    def update(self):
        self.y = self.base_y + math.sin(pygame.time.get_ticks() * 0.003 + self.phase) * 8
        # sparkle
        if random.random() < 0.05:
            self.particles.append(Particle(
                self.x + random.uniform(-6, 6),
                self.y + random.uniform(-6, 6),
                self.color, size=2, speed=0.3, lifetime=40
            ))
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)
        t = pygame.time.get_ticks() * 0.003 + self.phase
        s = self.size + math.sin(t * 2) * 2
        # glow
        glow = pygame.Surface((int(s * 4), int(s * 4)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color[:3], 40), (int(s * 2), int(s * 2)), int(s * 2))
        surf.blit(glow, (int(self.x - s * 2), int(self.y - s * 2)))
        # diamond shape
        points = [
            (self.x, self.y - s),
            (self.x + s * 0.7, self.y),
            (self.x, self.y + s),
            (self.x - s * 0.7, self.y),
        ]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, (255, 255, 255), points, 1)

    def check_collect(self, px, py, pw, ph):
        return (abs(self.x - (px + pw / 2)) < pw / 2 + self.size and
                abs(self.y - (py + ph / 2)) < ph / 2 + self.size)


# ═══════════════════════════════════════════════════════════
#  JELLO CUBE (the player)
# ═══════════════════════════════════════════════════════════
class JelloCube:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 40
        self.h = 40
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.speed = 4.5
        self.jump_power = -12
        self.gravity = 0.6
        self.squish = 0  # squish factor for landing
        self.squish_v = 0
        self.trail = []
        self.facing = 1  # 1 = right, -1 = left
        self.jiggle_phase = 0

    def update(self, keys, platforms):
        # Horizontal movement
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing = 1

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            self.squish = -0.3

        # Gravity
        self.vy += self.gravity
        if self.vy > 15:
            self.vy = 15

        # Move
        self.x += self.vx
        self.y += self.vy

        # Platform collisions
        self.on_ground = False
        for px, py, pw, ph in platforms:
            if (self.x + self.w > px and self.x < px + pw and
                    self.y + self.h > py and self.y + self.h < py + ph + 8 and
                    self.vy >= 0):
                self.y = py - self.h
                if self.vy > 4:
                    self.squish = 0.4
                self.vy = 0
                self.on_ground = True

        # Ground collision
        if self.y + self.h > GROUND_Y:
            if self.vy > 4:
                self.squish = 0.4
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.on_ground = True

        # Walls
        if self.x < 0:
            self.x = 0
        if self.x + self.w > SCREEN_W:
            self.x = SCREEN_W - self.w

        # Squish spring animation
        self.squish_v += (-self.squish) * 0.3
        self.squish_v *= 0.7
        self.squish += self.squish_v

        # Jiggle
        self.jiggle_phase += 0.15 if abs(self.vx) > 0 else 0.05

        # Trail
        if abs(self.vx) > 0 or not self.on_ground:
            self.trail.append((self.x + self.w // 2, self.y + self.h, pygame.time.get_ticks()))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def draw(self, surf):
        # Trail glow
        now = pygame.time.get_ticks()
        for tx, ty, t in self.trail:
            age = (now - t) / 400.0
            if age < 1:
                alpha = int(60 * (1 - age))
                s = int(6 * (1 - age))
                ts = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], alpha), (s, s), s)
                surf.blit(ts, (tx - s, ty - s))

        # Calculate squished dimensions
        sq = self.squish
        draw_w = int(self.w * (1 + sq * 0.5))
        draw_h = int(self.h * (1 - sq * 0.5))
        draw_x = int(self.x + (self.w - draw_w) / 2)
        draw_y = int(self.y + (self.h - draw_h))

        # Jiggle offset
        jiggle_x = math.sin(self.jiggle_phase) * 2 if abs(self.vx) > 0 else 0

        # Shadow
        shadow_surf = pygame.Surface((draw_w + 10, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (0, 0, draw_w + 10, 8))
        surf.blit(shadow_surf, (draw_x - 5 + jiggle_x, GROUND_Y - 3))

        # Glow underneath
        glow = pygame.Surface((draw_w + 30, draw_h + 30), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 25),
                            (0, 0, draw_w + 30, draw_h + 30))
        surf.blit(glow, (draw_x - 15 + jiggle_x, draw_y - 15))

        # Body (translucent jello)
        body = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        # Outer body
        pygame.draw.rect(body, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 140),
                         (0, 0, draw_w, draw_h), border_radius=6)
        # Inner highlight
        pygame.draw.rect(body, (180, 240, 160, 60),
                         (4, 4, draw_w - 8, draw_h // 2 - 4), border_radius=4)
        # Edge
        pygame.draw.rect(body, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 200),
                         (0, 0, draw_w, draw_h), 2, border_radius=6)
        surf.blit(body, (draw_x + jiggle_x, draw_y))

        # Eyes
        eye_y = draw_y + draw_h * 0.35
        eye_spread = draw_w * 0.22
        cx = draw_x + draw_w / 2 + jiggle_x
        for ex_offset in [-eye_spread, eye_spread]:
            ex = cx + ex_offset
            # White
            pygame.draw.circle(surf, (255, 255, 255), (int(ex), int(eye_y)), 5)
            # Pupil — looks in movement direction
            px = ex + self.facing * 2
            py = eye_y + (1 if not self.on_ground and self.vy > 0 else 0)
            pygame.draw.circle(surf, (20, 20, 40), (int(px), int(py)), 3)


# ═══════════════════════════════════════════════════════════
#  WORLD DRAWING
# ═══════════════════════════════════════════════════════════
def draw_castle_bg(surf, scroll_offset=0):
    """Draw a dark castle dungeon background."""
    # Sky / ceiling gradient
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H
        r = int(DEEP_STONE[0] + (WARM_STONE[0] - DEEP_STONE[0]) * ratio * 0.5)
        g = int(DEEP_STONE[1] + (WARM_STONE[1] - DEEP_STONE[1]) * ratio * 0.5)
        b = int(DEEP_STONE[2] + (WARM_STONE[2] - DEEP_STONE[2]) * ratio * 0.5)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))

    # Stone wall pattern
    t = pygame.time.get_ticks()
    for row in range(0, GROUND_Y, 40):
        offset = 20 if (row // 40) % 2 == 0 else 0
        for col in range(-40 + offset, SCREEN_W + 40, 80):
            brick_color = (
                WARM_STONE[0] + random.randint(-2, 2),
                WARM_STONE[1] + random.randint(-2, 2),
                WARM_STONE[2] + random.randint(-2, 2),
            )
            pygame.draw.rect(surf, brick_color, (col, row, 78, 38))
            pygame.draw.rect(surf, DEEP_STONE, (col, row, 78, 38), 1)

    # Torches on walls
    torches = [150, 400, 650]
    for tx in torches:
        # Bracket
        pygame.draw.rect(surf, (100, 80, 60), (tx - 3, 180, 6, 30))
        # Flame flicker
        flame_h = 12 + math.sin(t * 0.008 + tx) * 4
        flame_w = 8 + math.sin(t * 0.01 + tx * 0.5) * 3
        # Glow on wall
        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow, (TORCH_AMBER[0], TORCH_AMBER[1], TORCH_AMBER[2], 20), (60, 60), 60)
        surf.blit(glow, (tx - 60, 140))
        # Flame
        points = [
            (tx - flame_w / 2, 180),
            (tx, 180 - flame_h),
            (tx + flame_w / 2, 180),
        ]
        pygame.draw.polygon(surf, TORCH_AMBER, points)
        inner = [
            (tx - flame_w / 4, 180),
            (tx, 180 - flame_h * 0.6),
            (tx + flame_w / 4, 180),
        ]
        pygame.draw.polygon(surf, (255, 220, 120), inner)

    # Vines
    vine_positions = [50, 280, 520, 720]
    for vx in vine_positions:
        for vy in range(0, 200, 12):
            voffset = math.sin(vy * 0.1 + t * 0.001) * 3
            pygame.draw.circle(surf, VINE_GREEN, (int(vx + voffset), vy), 3)
            if random.random() < 0.3:
                leaf_x = int(vx + voffset + random.choice([-6, 6]))
                pygame.draw.circle(surf, (50, 120, 40), (leaf_x, vy), 2)

    # Ground / floor
    pygame.draw.rect(surf, DARK_FLOOR, (0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y))
    pygame.draw.line(surf, STONE_HIGHLIGHT, (0, GROUND_Y), (SCREEN_W, GROUND_Y), 2)
    # Floor tiles
    for fx in range(0, SCREEN_W, 60):
        pygame.draw.line(surf, (30, 25, 45), (fx, GROUND_Y), (fx, SCREEN_H), 1)


def draw_platforms(surf, platforms):
    """Draw floating stone platforms."""
    for px, py, pw, ph in platforms:
        # Main platform
        pygame.draw.rect(surf, WARM_STONE, (px, py, pw, ph))
        pygame.draw.rect(surf, STONE_HIGHLIGHT, (px, py, pw, 3))
        pygame.draw.rect(surf, DEEP_STONE, (px, py, pw, ph), 1)
        # Moss on top
        for mx in range(px + 5, px + pw - 5, 8):
            if random.random() < 0.4:
                pygame.draw.circle(surf, VINE_GREEN, (mx, py - 1), 2)


# ═══════════════════════════════════════════════════════════
#  TITLE SCREEN
# ═══════════════════════════════════════════════════════════
def title_screen():
    particles = []
    alpha = 0  # fade in

    while True:
        dt = clock.tick(FPS)
        t = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and alpha >= 250:
                    return  # start game

        # Fade in
        if alpha < 255:
            alpha = min(255, alpha + 3)

        # Spawn dungeon dust particles
        if random.random() < 0.15:
            particles.append(Particle(
                random.uniform(0, SCREEN_W),
                random.uniform(SCREEN_H * 0.3, SCREEN_H),
                TORCH_AMBER, size=2, speed=0.4, lifetime=200,
                drift_x=random.uniform(-0.2, 0.2)
            ))
        if random.random() < 0.05:
            particles.append(Particle(
                random.uniform(0, SCREEN_W),
                SCREEN_H + 10,
                JELLO_GREEN, size=3, speed=0.6, lifetime=160,
                drift_x=random.uniform(-0.5, 0.5)
            ))

        particles = [p for p in particles if p.update()]

        # ── Draw ──
        screen.fill(DEEP_STONE)

        # Vignette gradient
        for y in range(SCREEN_H):
            dist_from_center = abs(y - SCREEN_H * 0.4) / SCREEN_H
            darkness = int(min(30, dist_from_center * 50))
            pygame.draw.line(screen, (
                max(0, DEEP_STONE[0] - darkness),
                max(0, DEEP_STONE[1] - darkness),
                max(0, DEEP_STONE[2] - darkness)
            ), (0, y), (SCREEN_W, y))

        # Torch glow at top center
        glow = pygame.Surface((400, 300), pygame.SRCALPHA)
        glow_intensity = 30 + int(math.sin(t * 0.003) * 8)
        pygame.draw.ellipse(glow, (TORCH_AMBER[0], TORCH_AMBER[1], TORCH_AMBER[2], glow_intensity),
                            (0, 0, 400, 300))
        screen.blit(glow, (SCREEN_W // 2 - 200, 30))

        # Particles behind title
        for p in particles:
            p.draw(screen)

        # Title: "SPLIT"
        title_text = "S P L I T"
        # Letter-by-letter with glow
        letter_spacing = 60
        total_w = (len("SPLIT") - 1) * letter_spacing
        start_x = SCREEN_W // 2 - total_w // 2

        for i, letter in enumerate("SPLIT"):
            # Each letter bobs independently
            letter_y = 160 + math.sin(t * 0.003 + i * 0.8) * 6
            letter_alpha = min(255, alpha)

            # Green glow behind letter
            glow_s = pygame.Surface((60, 60), pygame.SRCALPHA)
            glow_a = int(40 + math.sin(t * 0.005 + i) * 15)
            pygame.draw.circle(glow_s, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], glow_a), (30, 30), 30)
            screen.blit(glow_s, (start_x + i * letter_spacing - 10, letter_y - 10))

            # The letter
            rendered = font_title.render(letter, True, JELLO_GREEN)
            letter_rect = rendered.get_rect(center=(start_x + i * letter_spacing + 10, letter_y + 20))
            screen.blit(rendered, letter_rect)

        # Subtitle
        sub = font_subtitle.render("A  J E L L O  C U B E  A D V E N T U R E", True, TORCH_GLOW)
        sub_rect = sub.get_rect(center=(SCREEN_W // 2, 240))
        screen.blit(sub, sub_rect)

        # Animated jello cube preview
        preview_y = 340 + math.sin(t * 0.004) * 10
        preview_squish = math.sin(t * 0.006) * 0.1
        pw = int(60 * (1 + preview_squish * 0.5))
        ph = int(60 * (1 - preview_squish * 0.5))
        px = SCREEN_W // 2 - pw // 2
        py = int(preview_y) - ph // 2

        # Glow
        glow = pygame.Surface((pw + 40, ph + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 30), (0, 0, pw + 40, ph + 40))
        screen.blit(glow, (px - 20, py - 20))

        # Body
        body_s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(body_s, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 160), (0, 0, pw, ph),
                         border_radius=8)
        pygame.draw.rect(body_s, (180, 240, 160, 70), (5, 5, pw - 10, ph // 2 - 5), border_radius=5)
        pygame.draw.rect(body_s, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 220), (0, 0, pw, ph), 2,
                         border_radius=8)
        screen.blit(body_s, (px, py))

        # Eyes
        eye_y = py + ph * 0.35
        for eye_off in [-10, 10]:
            pygame.draw.circle(screen, (255, 255, 255), (SCREEN_W // 2 + eye_off, int(eye_y)), 6)
            pupil_x = SCREEN_W // 2 + eye_off + int(math.sin(t * 0.002) * 2)
            pygame.draw.circle(screen, (20, 20, 40), (pupil_x, int(eye_y)), 3)

        # "Press SPACE to play" prompt
        if alpha >= 250:
            prompt_alpha = int(128 + math.sin(t * 0.005) * 127)
            prompt = font_prompt.render("Press SPACE to play", True, TORCH_GLOW)
            prompt.set_alpha(prompt_alpha)
            prompt_rect = prompt.get_rect(center=(SCREEN_W // 2, 480))
            screen.blit(prompt, prompt_rect)

        # Controls hint
        controls = font_small.render("Arrow keys to move  |  SPACE to jump  |  ESC to quit", True, (120, 110, 90))
        cr = controls.get_rect(center=(SCREEN_W // 2, 550))
        screen.blit(controls, cr)

        # Fade overlay
        if alpha < 255:
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(255 - alpha)
            screen.blit(fade, (0, 0))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════
#  GAMEPLAY SCENE
# ═══════════════════════════════════════════════════════════
def gameplay():
    player = JelloCube(100, GROUND_Y - 50)

    # Platforms
    platforms = [
        (180, 400, 120, 16),
        (380, 330, 140, 16),
        (560, 400, 100, 16),
        (280, 240, 100, 16),
        (500, 180, 130, 16),
    ]

    # Collectibles — jello powder scattered around
    collectibles = [
        Collectible(240, 370, JELLO_GREEN),
        Collectible(450, 300, TORCH_AMBER),
        Collectible(610, 370, (180, 120, 255)),
        Collectible(330, 210, EMBER),
        Collectible(565, 150, (255, 180, 60)),
        Collectible(700, GROUND_Y - 30, JELLO_GREEN),
        Collectible(50, GROUND_Y - 30, (180, 120, 255)),
    ]

    particles = []
    score = 0
    fade_in = 0

    # Optional: controller support
    joystick = None
    if pygame.joystick.get_count() > 0:
        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        except Exception:
            joystick = None

    while True:
        clock.tick(FPS)
        t = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # back to title

        # Controller hot-plug
        if joystick is None and pygame.joystick.get_count() > 0:
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
            except Exception:
                joystick = None

        keys = pygame.key.get_pressed()

        # Controller input overlay
        if joystick:
            try:
                axis_x = joystick.get_axis(0)
                if axis_x < -0.3:
                    keys_dict = dict(enumerate(keys))
                    # We'll handle this via a mutable list
                elif axis_x > 0.3:
                    pass
            except Exception:
                joystick = None

        player.update(keys, platforms)

        # Check collectibles
        for c in collectibles:
            if c.alive:
                c.update()
                if c.check_collect(player.x, player.y, player.w, player.h):
                    c.alive = False
                    score += 1
                    # Burst particles
                    for _ in range(15):
                        particles.append(Particle(
                            c.x + random.uniform(-5, 5),
                            c.y + random.uniform(-5, 5),
                            c.color, size=4, speed=random.uniform(1, 3),
                            lifetime=60,
                            drift_x=random.uniform(-2, 2)
                        ))

        # Ambient particles
        if random.random() < 0.05:
            particles.append(Particle(
                random.uniform(0, SCREEN_W),
                random.uniform(100, GROUND_Y),
                TORCH_AMBER, size=1.5, speed=0.3, lifetime=120
            ))

        particles = [p for p in particles if p.update()]

        # Fade in
        if fade_in < 255:
            fade_in = min(255, fade_in + 5)

        # ── Draw ──
        draw_castle_bg(screen)
        draw_platforms(screen, platforms)

        # Collectibles
        for c in collectibles:
            if c.alive:
                c.draw(screen)

        # Particles
        for p in particles:
            p.draw(screen)

        # Player
        player.draw(screen)

        # Score
        if score > 0:
            score_text = font_prompt.render(f"Jello Powder: {score}", True, TORCH_AMBER)
            screen.blit(score_text, (20, 20))

        # All collected message
        alive_count = sum(1 for c in collectibles if c.alive)
        if alive_count == 0:
            msg = font_subtitle.render("All jello powder collected!", True, JELLO_GREEN)
            msg_rect = msg.get_rect(center=(SCREEN_W // 2, 60))
            # Glow behind text
            glow = pygame.Surface((msg_rect.width + 40, msg_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 0, 0, 120), (0, 0, msg_rect.width + 40, msg_rect.height + 20),
                             border_radius=8)
            screen.blit(glow, (msg_rect.x - 20, msg_rect.y - 10))
            screen.blit(msg, msg_rect)

        # Fade in overlay
        if fade_in < 255:
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(255 - fade_in)
            screen.blit(fade, (0, 0))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════
def main():
    while True:
        title_screen()
        gameplay()


if __name__ == "__main__":
    main()
