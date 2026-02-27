# Coding 101 — Python for Game Builders

You've never coded before? No problem. This guide teaches you the basics using examples from YOUR game.

---

## What is Code?

Code is instructions for the computer. Just like a recipe tells you how to make a cake, code tells the computer how to run your game.

Python is the language we write those instructions in. It looks like English (mostly).

---

## Variables — Labeled Boxes

A **variable** stores a value. Think of it like a labeled box.

```python
player_name = "Hero"
player_health = 100
player_speed = 5
is_alive = True
```

- `player_name` is a box labeled "player_name" with "Hero" inside
- `player_health` is a box with the number 100 inside
- `is_alive` is a box that's either True or False

**Try it:** Change `player_health` to 200. What does that mean for your game?

---

## Math — The Computer Can Calculate

```python
score = 0
score = score + 10    # score is now 10
score = score + 25    # score is now 35

player_x = 100
player_x = player_x + 5  # player moved 5 pixels to the right
```

**Try it:** If the player starts at x=100 and moves 5 pixels every frame, where are they after 10 frames?

---

## If Statements — Making Decisions

```python
if player_health <= 0:
    print("Game Over!")

if score >= 100:
    print("You win!")
```

The code inside the `if` only runs when the condition is true.

```python
if button_pressed == "A":
    player_jump()
elif button_pressed == "B":
    player_attack()
else:
    player_idle()
```

- `if` — check the first condition
- `elif` — check another condition (short for "else if")
- `else` — if nothing else matched, do this

**Try it:** Write an if statement that checks if the player has more than 50 health.

---

## Loops — Repeat Things

### The Game Loop

Every game has a loop that runs over and over (60 times per second):

```python
running = True
while running:
    # 1. Check what buttons are pressed
    # 2. Move things
    # 3. Draw everything on screen
    # 4. Wait a tiny bit (1/60th of a second)
```

### For Loops — Do Something a Set Number of Times

```python
# Create 5 enemies
for i in range(5):
    print(f"Creating enemy number {i}")
```

**Try it:** Change `range(5)` to `range(10)`. How many enemies get created?

---

## Lists — Collections of Things

```python
enemies = ["goblin", "dragon", "slime"]
power_ups = ["health", "speed", "shield"]

# Get the first enemy
first_enemy = enemies[0]  # "goblin" (counting starts at 0!)

# Add a new enemy
enemies.append("skeleton")

# How many enemies?
num_enemies = len(enemies)  # 4
```

**Try it:** Create a list of 3 power-ups for your game.

---

## Functions — Reusable Recipes

```python
def jump(player):
    player.y = player.y - 50
    print("Jump!")

def take_damage(player, amount):
    player.health = player.health - amount
    if player.health <= 0:
        print("Game Over!")
```

Functions let you write code once and use it over and over:

```python
jump(player)       # player jumps
jump(player)       # player jumps again
take_damage(player, 10)  # player takes 10 damage
```

**Try it:** Write a function called `heal` that adds health to the player.

---

## Pygame Basics

Pygame is the library that draws your game on screen.

```python
import pygame

# Start Pygame
pygame.init()

# Create a window (800 pixels wide, 600 tall)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

# Colors are (Red, Green, Blue) from 0-255
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# The game loop
clock = pygame.time.Clock()
running = True

while running:
    # Check for events (like closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with black
    screen.fill(BLACK)

    # Draw a red rectangle (our player for now)
    pygame.draw.rect(screen, RED, (100, 100, 50, 50))

    # Show what we drew
    pygame.display.flip()

    # 60 frames per second
    clock.tick(60)

pygame.quit()
```

**Try it:** Change the color from RED to BLUE. Change the rectangle position.

---

## Coordinates — Where Things Are on Screen

```
(0,0) ------> x increases
  |
  |
  v
  y increases
```

- **(0, 0)** is the **top-left** corner
- **x** goes right (bigger = further right)
- **y** goes DOWN (bigger = further down — this is different from math class!)
- A screen that's 800x600 means x goes from 0 to 799, y goes from 0 to 599

---

## What's Next?

You know enough to start! Use `/learn` in Claude Code to learn more as you need it. The best way to learn is by building your game.
