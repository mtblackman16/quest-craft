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
# Nintendo Switch Pro Controller button mapping in Pygame:
# Button 0 = B (bottom)
# Button 1 = A (right)
# Button 2 = Y (left)
# Button 3 = X (top)
# Button 4 = L
# Button 5 = R
# Button 6 = ZL
# Button 7 = ZR
# Button 8 = Select (-)
# Button 9 = Start (+)
# Button 10 = Left Stick press
# Button 11 = Right Stick press
# Button 12 = Home
# Button 13 = Capture

# Axes:
# Axis 0 = Left stick X (-1 left, 1 right)
# Axis 1 = Left stick Y (-1 up, 1 down)
# Axis 2 = Right stick X
# Axis 3 = Right stick Y
```

> Note: Button numbers may vary. We'll test and update this when we connect the controller.

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
