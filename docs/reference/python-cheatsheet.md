# Python + Pygame Cheatsheet

Quick reference for patterns you'll use in the game. Keep this open while coding!

---

## Game Template (Starting Point)

```python
import pygame
import sys

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Our Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game state
    # (move things, check collisions, etc.)

    # Draw
    screen.fill(BLACK)
    # (draw sprites, text, etc.)
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)

pygame.quit()
sys.exit()
```

---

## Drawing Things

```python
# Rectangle
pygame.draw.rect(screen, RED, (x, y, width, height))

# Circle
pygame.draw.circle(screen, BLUE, (center_x, center_y), radius)

# Line
pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), thickness)
```

---

## Loading & Drawing Images

```python
# Load once (before the game loop)
player_img = pygame.image.load("assets/images/player/hero.png").convert_alpha()

# Resize if needed
player_img = pygame.transform.scale(player_img, (64, 64))

# Draw every frame (inside the game loop)
screen.blit(player_img, (player_x, player_y))
```

---

## Keyboard Input

```python
keys = pygame.key.get_pressed()

if keys[pygame.K_LEFT]:
    player_x -= speed
if keys[pygame.K_RIGHT]:
    player_x += speed
if keys[pygame.K_UP]:
    player_y -= speed
if keys[pygame.K_DOWN]:
    player_y += speed
if keys[pygame.K_SPACE]:
    player_jump()
```

---

## Controller Input

```python
# Set up (do once, before game loop)
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Read stick (in game loop)
axis_x = joystick.get_axis(0)  # -1 (left) to 1 (right)
axis_y = joystick.get_axis(1)  # -1 (up) to 1 (down)

# Dead zone (ignore tiny stick movements)
if abs(axis_x) > 0.2:
    player_x += axis_x * speed

# Read buttons
if joystick.get_button(1):  # A button
    player_jump()
if joystick.get_button(0):  # B button
    player_attack()
```

---

## Collision Detection

```python
# Using rectangles
player_rect = pygame.Rect(player_x, player_y, 50, 50)
enemy_rect = pygame.Rect(enemy_x, enemy_y, 50, 50)

if player_rect.colliderect(enemy_rect):
    print("Hit!")
    player_health -= 1
```

---

## Sound Effects

```python
# Load sounds (do once)
jump_sound = pygame.mixer.Sound("assets/sounds/effects/jump.wav")
coin_sound = pygame.mixer.Sound("assets/sounds/effects/coin.wav")

# Play a sound
jump_sound.play()

# Background music
pygame.mixer.music.load("assets/sounds/music/level1.ogg")
pygame.mixer.music.play(-1)  # -1 = loop forever
pygame.mixer.music.set_volume(0.5)  # 0.0 to 1.0
```

---

## Displaying Text

```python
# Set up font (do once)
font = pygame.font.Font(None, 36)  # None = default font, 36 = size

# Render text (in game loop)
score_text = font.render(f"Score: {score}", True, WHITE)
screen.blit(score_text, (10, 10))
```

---

## Game States

```python
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

game_state = STATE_MENU

while running:
    if game_state == STATE_MENU:
        # Draw menu, check for Start button
        if start_pressed:
            game_state = STATE_PLAYING

    elif game_state == STATE_PLAYING:
        # Run the game
        if player_health <= 0:
            game_state = STATE_GAME_OVER

    elif game_state == STATE_GAME_OVER:
        # Show game over screen
        if retry_pressed:
            game_state = STATE_PLAYING
            reset_game()
```

---

## Keeping Player On Screen

```python
# Don't let player leave the screen
if player_x < 0:
    player_x = 0
if player_x > 800 - player_width:
    player_x = 800 - player_width
if player_y < 0:
    player_y = 0
if player_y > 600 - player_height:
    player_y = 600 - player_height
```

---

## Simple Gravity

```python
gravity = 0.5
velocity_y = 0
on_ground = False

# In game loop:
velocity_y += gravity  # accelerate downward
player_y += velocity_y  # apply velocity

# Check if on ground
if player_y >= ground_y:
    player_y = ground_y
    velocity_y = 0
    on_ground = True

# Jump (only if on ground)
if jump_pressed and on_ground:
    velocity_y = -12  # negative = up
    on_ground = False
```

---

## Timer

```python
# Get time since last frame (in seconds)
dt = clock.tick(60) / 1000.0

# Use dt for smooth movement
player_x += speed * dt

# Countdown timer
time_left = 60  # seconds
time_left -= dt
if time_left <= 0:
    game_over()
```
