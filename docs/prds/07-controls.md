# PRD 07: Controls & Controller Mapping

| Field | Value |
|-------|-------|
| **Status** | Complete |
| **Author** | Team (Ethan, Eins, Andrew, Nathan) |
| **Date** | 2026-03-08 |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [03-gameplay.md](03-gameplay.md) |

---

## Controller

**Primary:** Nintendo Switch Pro Controller (paired via Bluetooth)
**Backup:** Keyboard

---

## Button Map

### Nintendo Switch Pro Controller Layout

```
          [ZL]                    [ZR]
          [L]                     [R]

    +---+                         [X]
    |   |   [Select] [Home] [Start]  [Y]   [A]
    +---+                         [B]
   D-pad        [LS]    [RS]
              (sticks)
```

### Button Assignments

| Button | Pygame | What It Does |
|--------|--------|-------------|
| **Left Stick** | Axis 0/1 | Move left/right |
| **Right Stick** | Axis 2/3 | Slightly shift camera. Choose facing direction without moving. |
| **A** (right) | Button 1 | Jump |
| **B** (bottom) | Button 0 | Jelly Shot (basic attack, costs mass) |
| **X** (top) | Button 2 | Eat Jello Powder (heal/restore mass) |
| **Y** (left) | Button 3 | Interact (NPCs, objects, cooking pots, anything interactable) |
| **L Bumper** | Button 5 | Switch control between split jelly pieces |
| **R Bumper** | Button 6 | — (unused) |
| **ZL** | Button 7 | Split / Combine (toggle — press once to split, again to combine) |
| **ZR** | Button 8 | Perfect Dodge |
| **D-pad** | Hat 0 | — (unused) |
| **Plus (+)** | Button 10 | Pause menu |
| **Minus (-)** | Button 9 | Inventory (TODO: design inventory in Session 3) |
| **Home** | Button 11 | — (system, not used by game) |
| **Capture** | Button 4 | — (system, not used by game) |
| **L Stick Click** | Button 12 | — (unused) |
| **R Stick Click** | Button 13 | — (unused) |

### Special Moves (Button Combos)

| Move | How to Perform |
|------|---------------|
| **Ground Pound** | Jump (A) → press Down on Left Stick while airborne |
| **Perfect Dodge** | ZR — timed press to dodge through an attack |

---

## Controls Feel

**Reference:** Dead Cells — weighty, heavy, satisfying impact.

**Movement:** Weighty. Not floaty, not sluggish. When you move, you feel the mass of the Jello Cube. When you stop, there's a brief settle (jelly physics wobble). Every action has WEIGHT.

**Jumping:** Satisfying arc with weight. Not floaty — the Jello Cube has mass. Ground pound should feel like a heavy SLAM with screen shake and impact.

**Attacking:** Jelly Shot should have a punchy, weighty feel — brief recoil, visible mass leaving the body. Not a light pew-pew.

**Overall:** Everything should feel physical and tactile. The player should FEEL the jelly through the controller. Dead Cells nailed this — every swing, dodge, and stomp has satisfying weight and feedback.

---

## Keyboard Backup

| Controller | Keyboard |
|-----------|----------|
| Left Stick | Arrow keys or WASD |
| A (Jump) | Space bar |
| B (Jelly Shot) | Z key |
| X (Eat Jello) | X key |
| Y (Interact) | C key |
| L Bumper (Switch Split) | Tab |
| ZL (Split/Combine toggle) | Q |
| ZR (Perfect Dodge) | E |
| Plus (Pause) | Escape |
| Minus (Inventory) | I |

---

## Pygame Controller Notes

> Technical notes for coding (Claude will reference this)

```python
# Nintendo Switch Pro Controller button mapping in Pygame
# (Pi 5 + hid_nintendo driver — verified via evtest March 2026)
#
# Button 0  = B (bottom)       BTN_SOUTH (304)  → Jelly Shot
# Button 1  = A (right)        BTN_EAST (305)   → Jump
# Button 2  = X (top)          BTN_NORTH (307)  → Eat Jello Powder
# Button 3  = Y (left)         BTN_WEST (308)   → Interact
# Button 4  = Capture          BTN_Z (309)      → (unused)
# Button 5  = L Bumper         BTN_TL (310)     → Switch Split Control
# Button 6  = R Bumper         BTN_TR (311)     → (unused)
# Button 7  = ZL               BTN_TL2 (312)    → Split/Combine (toggle)
# Button 8  = ZR               BTN_TR2 (313)    → Perfect Dodge
# Button 9  = Minus (-)        BTN_SELECT (314) → Inventory
# Button 10 = Plus (+)         BTN_START (315)  → Pause
# Button 11 = Home             BTN_MODE (316)   → (system)
# Button 12 = L Stick Click    BTN_THUMBL (317) → (unused)
# Button 13 = R Stick Click    BTN_THUMBR (318) → (unused)
#
# Axes:
# Axis 0 = Left stick X (-1 left, 1 right)  → Movement
# Axis 1 = Left stick Y (-1 up, 1 down)     → Movement + Ground Pound (down while airborne)
# Axis 2 = Right stick X                     → Camera shift + Facing direction
# Axis 3 = Right stick Y                     → Camera shift
#
# D-pad = Hat 0 (tuple, NOT buttons) → (unused)
#   joy.get_hat(0) → (x, y) where x: -1=left, 1=right; y: 1=up, -1=down
```

> Verified on live hardware March 6, 2026. Button indices follow kernel event code order (BTN_SOUTH=304 onwards).

---

## Session 3 TODO

- [ ] Design the inventory screen (opened with Minus button)
