"""
SPLIT -- Pause Menu
Semi-transparent dark overlay, 'PAUSED' text, resume/quit selection.
Clean and minimal.
"""

import pygame

from game.engine.settings import (
    SCREEN_W,
    SCREEN_H,
    FPS,
    FONT_TITLE,
    FONT_PROMPT,
    JELLO_GREEN,
    WHITE,
    CTRL_A,
    CTRL_B,
    CTRL_PLUS,
    AXIS_LY,
    STICK_DEADZONE,
    KEY_PAUSE,
)


# ---------------------------------------------------------------------------
# run_pause_menu
# ---------------------------------------------------------------------------

MENU_OPTIONS = ["Resume", "Quit to Title"]


def run_pause_menu(screen, clock, joystick=None):
    """Run the pause menu loop.

    The current game frame should already be on *screen* when this is called;
    the menu draws a dark overlay on top.

    Returns
    -------
    str
        'resume' or 'quit'
    """
    pygame.font.init()

    font_title = pygame.font.Font(None, FONT_TITLE)
    font_prompt = pygame.font.Font(None, FONT_PROMPT)

    # Capture the current frame as a snapshot
    snapshot = screen.copy()

    # Dark overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))

    # Pre-render title
    pause_surf = font_title.render("PAUSED", True, WHITE)
    pause_w = pause_surf.get_width()

    selected = 0

    # Stick repeat
    stick_held_frames = 0
    last_stick_dir = 0

    running = True
    while running:
        clock.tick(FPS)

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

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MENU_OPTIONS)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return "resume" if selected == 0 else "quit"
                elif event.key == KEY_PAUSE:
                    # ESC also resumes
                    return "resume"

            # Controller buttons
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == CTRL_A:
                    return "resume" if selected == 0 else "quit"
                elif event.button == CTRL_PLUS:
                    # Plus button resumes
                    return "resume"
                elif event.button == CTRL_B:
                    return "resume"

            # D-pad
            if event.type == pygame.JOYHATMOTION:
                _, hat_y = event.value
                if hat_y == 1:
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif hat_y == -1:
                    selected = (selected + 1) % len(MENU_OPTIONS)

        # -- controller stick ------------------------------------------------
        if joystick:
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

        # -- draw ------------------------------------------------------------
        # Snapshot + dark overlay
        screen.blit(snapshot, (0, 0))
        screen.blit(overlay, (0, 0))

        # "PAUSED"
        screen.blit(pause_surf, (SCREEN_W // 2 - pause_w // 2, 250))

        # Menu options
        menu_y = 360
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

    return "resume"
