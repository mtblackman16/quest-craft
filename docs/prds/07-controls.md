# PRD 07: Controls & Controller Mapping

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Author** | — |
| **Date** | — |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [03-gameplay.md](03-gameplay.md) |

---

## Controller

**What controller are we using?**
- [x] Nintendo Switch Pro Controller (via Bluetooth)
- [ ] Nintendo Joy-Cons (via Bluetooth)
- [ ] Keyboard (as backup)

---

## Button Map

> Fill in what each button does in your game:

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

| Button | What It Does |
|--------|-------------|
| **Left Stick** | ___ (move player?) |
| **Right Stick** | ___ |
| **A** | ___ (jump? confirm?) |
| **B** | ___ (attack? back?) |
| **X** | ___ |
| **Y** | ___ |
| **L** | ___ |
| **R** | ___ |
| **ZL** | ___ |
| **ZR** | ___ |
| **D-pad Up** | ___ |
| **D-pad Down** | ___ |
| **D-pad Left** | ___ |
| **D-pad Right** | ___ |
| **Start (+)** | ___ (pause?) |
| **Select (-)** | ___ |

---

## Keyboard Backup

> In case the controller isn't working, what keyboard keys do the same things?

| Controller | Keyboard |
|-----------|----------|
| Left Stick | Arrow keys or WASD |
| A button | Space bar |
| B button | Z key |
| X button | X key |
| Y button | C key |
| Start | Enter |
| Select | Escape |

---

## Controls Feel

**How should moving feel?**
- [ ] Snappy and precise (stop immediately when you let go)
- [ ] Smooth and floaty (slide a little when you let go)
- [ ] Heavy and slow (like controlling a tank)

**How should jumping feel?** (if the game has jumping)
- [ ] Quick and snappy (tap = small jump, hold = big jump)
- [ ] Floaty (hang in the air a little)
- [ ] Realistic (goes up fast, comes down fast)

---

## Pygame Controller Notes

> Technical notes for coding (Claude will reference this)

```python
# Nintendo Switch Pro Controller button mapping in Pygame
# (Pi 5 + hid_nintendo driver — verified via evtest March 2026)
#
# Button 0  = B (bottom)       BTN_SOUTH (304)
# Button 1  = A (right)        BTN_EAST (305)
# Button 2  = X (top)          BTN_NORTH (307)
# Button 3  = Y (left)         BTN_WEST (308)
# Button 4  = Capture          BTN_Z (309)
# Button 5  = L Bumper         BTN_TL (310)
# Button 6  = R Bumper         BTN_TR (311)
# Button 7  = ZL               BTN_TL2 (312)
# Button 8  = ZR               BTN_TR2 (313)
# Button 9  = Minus (-)        BTN_SELECT (314)
# Button 10 = Plus (+)         BTN_START (315)
# Button 11 = Home             BTN_MODE (316)
# Button 12 = L Stick Click    BTN_THUMBL (317)
# Button 13 = R Stick Click    BTN_THUMBR (318)
#
# Axes:
# Axis 0 = Left stick X (-1 left, 1 right)
# Axis 1 = Left stick Y (-1 up, 1 down)
# Axis 2 = Right stick X
# Axis 3 = Right stick Y
#
# D-pad = Hat 0 (tuple, NOT buttons)
#   joy.get_hat(0) → (x, y) where x: -1=left, 1=right; y: 1=up, -1=down
```

> Verified on live hardware March 6, 2026. Button indices follow kernel event code order (BTN_SOUTH=304 onwards).

---

## Imagine You're Playing...

> Your friend picks up the controller for the first time...

**What's the first button they press?** ___

**Is it obvious what to do?** ___

**How would you explain the controls in 10 seconds?** ___

---

## Open Questions

- [ ] ___
- [ ] ___
