"""
SPLIT — Inventory Screen
Opens with Minus button. Shows jello powder, pills, active pill, water status.
Navigate with stick/d-pad, A to use pill, Minus/B to close.
"""
import pygame
import math
from game.engine.settings import (
    SCREEN_W, SCREEN_H, FPS, PillType, PILL_DURATIONS,
    CTRL_A, CTRL_B, CTRL_MINUS, CTRL_PLUS, CTRL_Y,
    AXIS_LY, STICK_DEADZONE,
    JELLO_GREEN, JELLO_GREEN_DIM, TORCH_AMBER, TORCH_GLOW,
    WHITE, BLACK, RED, HEALTH_GREEN,
    FONT_TITLE, FONT_SUBTITLE, FONT_PROMPT, FONT_SMALL, FONT_HUD,
)

# ── Pill display colors ──
PILL_COLORS = {
    PillType.FIRE:        (220, 80, 40),
    PillType.WATER:       (60, 140, 220),
    PillType.ICE:         (160, 220, 240),
    PillType.ELECTRICITY: (240, 230, 60),
    PillType.ATTACK_UP:   (200, 60, 200),
}

PILL_NAMES = {
    PillType.FIRE:        "Fire Pill",
    PillType.WATER:       "Water Pill",
    PillType.ICE:         "Ice Pill",
    PillType.ELECTRICITY: "Electric Pill",
    PillType.ATTACK_UP:   "Attack Up",
}


def _draw_diamond(surface, cx, cy, size, color):
    """Draw a diamond shape (jello powder icon)."""
    points = [
        (cx, cy - size),
        (cx + size, cy),
        (cx, cy + size),
        (cx - size, cy),
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 2)


def _draw_pill_icon(surface, cx, cy, pill_type, size=14):
    """Draw a small pill capsule icon."""
    color = PILL_COLORS.get(pill_type, WHITE)
    # Rounded rectangle pill shape
    rect = pygame.Rect(cx - size, cy - size // 2, size * 2, size)
    pygame.draw.ellipse(surface, color, rect)
    # Dividing line
    pygame.draw.line(surface, WHITE, (cx, cy - size // 2), (cx, cy + size // 2), 1)


def _draw_water_drop(surface, cx, cy, size, has_water):
    """Draw a water drop icon."""
    color = (60, 140, 220) if has_water else (80, 80, 80)
    # Teardrop shape using a triangle top + circle bottom
    points = [
        (cx, cy - size),
        (cx - size // 2, cy),
        (cx + size // 2, cy),
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.circle(surface, color, (cx, cy + 2), size // 2)


def run_inventory(screen, clock, player, crafting_system, joystick=None):
    """
    Inventory overlay screen.
    Shows jello powder, pills, active pill timer, and water status.
    Navigate with stick/d-pad, A to use pill, Minus/B to close.
    """
    font_title = pygame.font.Font(None, FONT_TITLE)
    font_sub = pygame.font.Font(None, FONT_SUBTITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)
    font_small = pygame.font.Font(None, FONT_SMALL)

    # Build list of pill types for navigation
    pill_types = list(PillType)
    # Total selectable items: pills only (index 0..len-1)
    num_items = len(pill_types)
    selected = 0

    # Overlay surface
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    # Input repeat / cooldown
    nav_cooldown = 0
    NAV_DELAY = 12  # frames between stick repeats

    # Capture the current screen as background
    background = screen.copy()

    # Info message shown at bottom
    info_text = ""
    info_timer = 0

    running = True
    while running:
        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % num_items
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % num_items
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Try to use selected pill
                    pill = pill_types[selected]
                    count = crafting_system.pill_inventory.get(pill, 0)
                    if count > 0:
                        crafting_system.use_pill(pill)
                        info_text = f"Swallowed {PILL_NAMES[pill]}!"
                        info_timer = 120
                    else:
                        info_text = "You don't have any of those."
                        info_timer = 90

            if event.type == pygame.JOYBUTTONDOWN and joystick:
                if event.button == CTRL_MINUS or event.button == CTRL_B:
                    running = False
                elif event.button == CTRL_A:
                    pill = pill_types[selected]
                    count = crafting_system.pill_inventory.get(pill, 0)
                    if count > 0:
                        crafting_system.use_pill(pill)
                        info_text = f"Swallowed {PILL_NAMES[pill]}!"
                        info_timer = 120
                    else:
                        info_text = "You don't have any of those."
                        info_timer = 90

            # D-pad navigation
            if event.type == pygame.JOYHATMOTION and joystick:
                hat_x, hat_y = event.value
                if hat_y == 1:   # up
                    selected = (selected - 1) % num_items
                elif hat_y == -1:  # down
                    selected = (selected + 1) % num_items

        # ── Stick navigation with cooldown ──
        if joystick and nav_cooldown <= 0:
            ly = joystick.get_axis(AXIS_LY)
            if ly < -STICK_DEADZONE:
                selected = (selected - 1) % num_items
                nav_cooldown = NAV_DELAY
            elif ly > STICK_DEADZONE:
                selected = (selected + 1) % num_items
                nav_cooldown = NAV_DELAY

        if nav_cooldown > 0:
            nav_cooldown -= 1

        if info_timer > 0:
            info_timer -= 1

        # ── Draw ──
        # Blit frozen background
        screen.blit(background, (0, 0))

        # Semi-transparent dark overlay
        overlay.fill((0, 0, 0, 0))
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, SCREEN_W, SCREEN_H))
        screen.blit(overlay, (0, 0))

        # Title
        title_surf = font_title.render("INVENTORY", True, TORCH_AMBER)
        title_rect = title_surf.get_rect(midtop=(SCREEN_W // 2, 30))
        screen.blit(title_surf, title_rect)

        # ── Jello Powder (top-left area) ──
        section_y = 120
        powder_label = font_sub.render("Jello Powder", True, JELLO_GREEN)
        screen.blit(powder_label, (100, section_y))
        _draw_diamond(screen, 70, section_y + 12, 10, JELLO_GREEN)
        powder_count = getattr(player, 'jello_powder_count', 0)
        count_surf = font_sub.render(f"x {powder_count}", True, WHITE)
        screen.blit(count_surf, (260, section_y))

        # ── Water Status (top-right area) ──
        has_water = getattr(player, 'has_water', False)
        water_label = font_sub.render("Water:", True, WHITE)
        screen.blit(water_label, (SCREEN_W - 350, section_y))
        _draw_water_drop(screen, SCREEN_W - 200, section_y + 12, 12, has_water)
        status_text = "Yes" if has_water else "No"
        status_color = (60, 180, 240) if has_water else (120, 120, 120)
        status_surf = font_sub.render(status_text, True, status_color)
        screen.blit(status_surf, (SCREEN_W - 180, section_y))

        # ── Active Pill Display ──
        active_y = 180
        active_pill = getattr(crafting_system, 'active_pill', None)
        if active_pill is not None:
            ap_color = PILL_COLORS.get(active_pill, WHITE)
            ap_name = PILL_NAMES.get(active_pill, str(active_pill))
            active_label = font_sub.render(f"Active: {ap_name}", True, ap_color)
            screen.blit(active_label, (100, active_y))

            # Remaining time bar
            remaining = getattr(crafting_system, 'active_pill_remaining', 0)
            duration_key = active_pill.value
            total = PILL_DURATIONS.get(duration_key, 1)
            ratio = max(0.0, min(1.0, remaining / total)) if total > 0 else 0

            bar_x = 100
            bar_y = active_y + 32
            bar_w = 400
            bar_h = 16
            # Background
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            # Fill
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(screen, ap_color, (bar_x, bar_y, fill_w, bar_h))
            # Border
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)

            # Time text
            remaining_sec = remaining / 60 if remaining > 0 else 0
            time_surf = font_small.render(f"{remaining_sec:.1f}s", True, WHITE)
            screen.blit(time_surf, (bar_x + bar_w + 10, bar_y - 2))
        else:
            no_active = font_small.render("No active pill", True, (120, 120, 120))
            screen.blit(no_active, (100, active_y + 4))

        # ── Pill Grid (2 columns) ──
        grid_top = 260
        col_w = 400
        row_h = 60
        cols = 2

        for i, pill in enumerate(pill_types):
            col = i % cols
            row = i // cols

            x = 100 + col * col_w
            y = grid_top + row * row_h

            # Highlight selected
            if i == selected:
                highlight_rect = pygame.Rect(x - 10, y - 6, col_w - 20, row_h - 8)
                pygame.draw.rect(screen, JELLO_GREEN, highlight_rect, 2, border_radius=6)
                # Subtle green fill
                hl_surf = pygame.Surface((col_w - 20, row_h - 8), pygame.SRCALPHA)
                hl_surf.fill((125, 223, 100, 30))
                screen.blit(hl_surf, (x - 10, y - 6))

            # Pill icon
            _draw_pill_icon(screen, x + 16, y + 16, pill)

            # Pill name
            name = PILL_NAMES[pill]
            name_color = PILL_COLORS[pill] if i == selected else WHITE
            name_surf = font_prompt.render(name, True, name_color)
            screen.blit(name_surf, (x + 40, y + 4))

            # Count
            count = crafting_system.pill_inventory.get(pill, 0)
            count_color = WHITE if count > 0 else (80, 80, 80)
            count_surf = font_prompt.render(f"x{count}", True, count_color)
            screen.blit(count_surf, (x + 220, y + 4))

        # ── Info text at bottom ──
        if info_timer > 0 and info_text:
            alpha = min(255, info_timer * 4)
            info_surf = font_sub.render(info_text, True, TORCH_GLOW)
            info_rect = info_surf.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H - 80))
            screen.blit(info_surf, info_rect)

        # ── Controls hint ──
        hint = font_small.render("[A] Use Pill    [Minus/B] Close", True, (160, 160, 160))
        hint_rect = hint.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H - 30))
        screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(FPS)
