"""
Controller Test — Quest Craft
Run this to verify your Nintendo controllers work with Pygame.
Shows all button presses, axis values, and controller info.

Usage: python3 game/test_controller.py
Press ESC to quit.
"""
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((700, 550))
pygame.display.set_caption("Split — Controller Test")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
font_big = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 20)

# Colors matching the Split game aesthetic
BG = (26, 26, 46)
JELLO_GREEN = (125, 223, 100)
TORCH_AMBER = (232, 168, 56)
CREAM = (245, 230, 200)
DIM = (154, 142, 122)
EMBER = (196, 75, 43)
PANEL_BG = (45, 45, 68)

# Track joysticks by instance_id (supports hotplug)
joysticks = {}

DEADZONE = 0.15


def apply_deadzone(value, threshold=DEADZONE):
    if abs(value) < threshold:
        return 0.0
    return value


def draw_panel(surface, rect, label=None):
    """Draw a dark panel with amber border."""
    pygame.draw.rect(surface, PANEL_BG, rect, border_radius=4)
    pygame.draw.rect(surface, (*TORCH_AMBER[:3], 80), rect, 2, border_radius=4)
    if label:
        lbl = font_small.render(label, True, TORCH_AMBER)
        surface.blit(lbl, (rect[0] + 8, rect[1] - 16))


running = True
last_event = "Press buttons on your controller..."
last_event_color = DIM

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Controller hotplug
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            last_event = f"CONNECTED: {joy.get_name()}"
            last_event_color = JELLO_GREEN

        if event.type == pygame.JOYDEVICEREMOVED:
            if event.instance_id in joysticks:
                name = joysticks[event.instance_id].get_name()
                del joysticks[event.instance_id]
                last_event = f"DISCONNECTED: {name}"
                last_event_color = EMBER

        if event.type == pygame.JOYBUTTONDOWN:
            last_event = f"Button {event.button} PRESSED"
            last_event_color = TORCH_AMBER

        if event.type == pygame.JOYBUTTONUP:
            last_event = f"Button {event.button} released"
            last_event_color = DIM

    # Draw
    screen.fill(BG)

    # Title
    title = font_big.render("Split — Controller Test", True, JELLO_GREEN)
    screen.blit(title, (20, 12))

    # Last event
    draw_panel(screen, (20, 50, 660, 36))
    ev_text = font.render(last_event, True, last_event_color)
    screen.blit(ev_text, (30, 57))

    y = 110
    if not joysticks:
        draw_panel(screen, (20, y, 660, 80), "Status")
        no_ctrl = font.render(
            "No controllers detected.", True, CREAM
        )
        screen.blit(no_ctrl, (30, y + 10))
        hint1 = font_small.render(
            "Press the SYNC button on your Pro Controller (top, near USB-C)",
            True,
            DIM,
        )
        hint2 = font_small.render(
            "Or connect via USB-C cable for instant connection",
            True,
            DIM,
        )
        screen.blit(hint1, (30, y + 35))
        screen.blit(hint2, (30, y + 55))
    else:
        for jid, joy in joysticks.items():
            # Controller name
            draw_panel(screen, (20, y, 660, 30), f"Controller {jid}")
            name_text = font.render(joy.get_name(), True, JELLO_GREEN)
            screen.blit(name_text, (30, y + 5))
            y += 45

            # Axes panel
            num_axes = joy.get_numaxes()
            axes_height = max(30, num_axes * 22 + 10)
            draw_panel(screen, (20, y, 320, axes_height), "Axes")
            for a in range(num_axes):
                val = apply_deadzone(joy.get_axis(a))
                # Draw bar
                bar_center_x = 210
                bar_w = int(abs(val) * 80)
                if val >= 0:
                    bar_rect = (bar_center_x, y + 5 + a * 22, bar_w, 14)
                    bar_color = JELLO_GREEN
                else:
                    bar_rect = (bar_center_x - bar_w, y + 5 + a * 22, bar_w, 14)
                    bar_color = EMBER
                pygame.draw.rect(screen, bar_color, bar_rect, border_radius=2)
                # Label
                ax_label = font_small.render(
                    f"Axis {a}: {val:+.2f}", True, CREAM
                )
                screen.blit(ax_label, (30, y + 5 + a * 22))

            # Buttons panel
            num_buttons = joy.get_numbuttons()
            buttons_height = axes_height
            draw_panel(screen, (360, y, 320, buttons_height), "Buttons")
            pressed = []
            for b in range(num_buttons):
                if joy.get_button(b):
                    pressed.append(str(b))

            if pressed:
                btn_str = "Pressed: " + ", ".join(pressed)
                btn_color = TORCH_AMBER
            else:
                btn_str = "(none pressed)"
                btn_color = DIM

            bt = font.render(btn_str, True, btn_color)
            screen.blit(bt, (370, y + 10))

            # Show Pro Controller button names if applicable
            # Actual mapping from Pi 5 + hid_nintendo (14 buttons, 4 axes, 1 hat):
            # Verified mapping: Pi 5 + hid_nintendo + SDL2 (evtest ground truth)
            PRO_NAMES = {
                0: "B",        # BTN_SOUTH (304)
                1: "A",        # BTN_EAST (305)
                2: "X",        # BTN_NORTH (307)
                3: "Y",        # BTN_WEST (308)
                4: "Capture",  # BTN_Z (309)
                5: "L Bump",   # BTN_TL (310)
                6: "R Bump",   # BTN_TR (311)
                7: "ZL",       # BTN_TL2 (312)
                8: "ZR",       # BTN_TR2 (313)
                9: "Minus",    # BTN_SELECT (314)
                10: "Plus",    # BTN_START (315)
                11: "Home",    # BTN_MODE (316)
                12: "L Click", # BTN_THUMBL (317)
                13: "R Click", # BTN_THUMBR (318)
            }
            if pressed:
                names = [
                    f"{p}={PRO_NAMES.get(int(p), '?')}" for p in pressed
                ]
                name_str = "  ".join(names)
                name_text = font_small.render(name_str, True, CREAM)
                screen.blit(name_text, (370, y + 35))

            # Hat (D-pad) display
            num_hats = joy.get_numhats()
            if num_hats > 0:
                hat = joy.get_hat(0)
                hat_names = []
                if hat[1] == 1: hat_names.append("Up")
                if hat[1] == -1: hat_names.append("Down")
                if hat[0] == -1: hat_names.append("Left")
                if hat[0] == 1: hat_names.append("Right")
                hat_str = "D-pad: " + ("+".join(hat_names) if hat_names else "(center)")
                hat_color = TORCH_AMBER if hat_names else DIM
                ht = font_small.render(hat_str, True, hat_color)
                screen.blit(ht, (370, y + 55))

            y += axes_height + 25

    # Keyboard section at bottom
    draw_panel(screen, (20, 480, 660, 50), "Keyboard (always works)")
    keys = pygame.key.get_pressed()
    kb_parts = []
    key_map = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
        pygame.K_SPACE: "SPACE",
        pygame.K_z: "Z",
        pygame.K_a: "A",
        pygame.K_d: "D",
        pygame.K_w: "W",
        pygame.K_s: "S",
        pygame.K_j: "J",
        pygame.K_k: "K",
        pygame.K_e: "E",
        pygame.K_l: "L",
    }
    for key, name in key_map.items():
        if keys[key]:
            kb_parts.append(name)

    if kb_parts:
        kb_str = "Pressed: " + " + ".join(kb_parts)
        kb_color = TORCH_AMBER
    else:
        kb_str = "(press arrow keys, SPACE, Z, J, K, E, L to test)"
        kb_color = DIM

    kb_text = font.render(kb_str, True, kb_color)
    screen.blit(kb_text, (30, 495))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
