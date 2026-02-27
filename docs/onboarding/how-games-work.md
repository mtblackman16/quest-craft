# How Games Work — The Principles Behind Great Games

You don't need to know how to code to build a game with AI. But understanding HOW games work makes you a better designer. Here are the ideas that every game designer knows.

---

## The Game Loop

Every game in history runs on the same simple loop:

```
While the game is running:
  1. Check what buttons the player pressed
  2. Update everything (move player, move enemies, check collisions)
  3. Draw everything on screen
  4. Wait a tiny bit (1/60th of a second)
  5. Do it all again
```

This happens **60 times every second**. It's like a flip book — each "page" is slightly different, creating the illusion of movement.

---

## The Core Loop

Every great game has a **core loop** — the thing you do over and over:

- **Mario:** Jump → Land → Jump again (with obstacles getting harder)
- **Zelda:** Explore → Find item → Use item to reach new area
- **Minecraft:** Gather → Build → Explore → Gather more

Your game has a core loop too. Ask yourself: "What does the player do 90% of the time?" That's your core loop. Make THAT feel amazing.

---

## Coordinates and the Screen

The game screen is a grid of tiny dots called **pixels**.

```
(0,0) ────────────────────── (800,0)
  │                              │
  │         THE SCREEN           │
  │                              │
  │    Player might be at        │
  │    (200, 300)                │
  │                              │
(0,600) ──────────────────── (800,600)
```

- **(0, 0)** is the top-left corner
- **X** goes right (bigger = more right)
- **Y** goes DOWN (bigger = more down) — this is the opposite of math class!
- A typical game window is 800 x 600 pixels

---

## Movement = Changing Position

Moving a character is just adding or subtracting from their position:

- **Move right:** add to X (x + 5)
- **Move left:** subtract from X (x - 5)
- **Move down:** add to Y (y + 5)
- **Move up:** subtract from Y (y - 5)

The number you add is the **speed**. Bigger number = faster movement.

---

## Gravity = Adding Speed Downward

Gravity is surprisingly simple:

```
Every frame:
  1. Add a little bit to the falling speed
  2. Add the falling speed to the player's Y position
```

This makes the player fall slowly at first, then faster and faster — just like real life!

**Jumping** = setting the falling speed to a negative number (going UP). Gravity gradually pulls them back down.

---

## Collision = Rectangles Touching

Almost every game uses **rectangle collision** (called AABB collision). Every character and object has an invisible rectangle around it. If two rectangles overlap, it's a "collision."

```
  ┌─────┐
  │Player│    ┌──────┐
  │     ─┼────┼─Enemy│  ← These overlap! COLLISION!
  └─────┘    └──────┘
```

What happens on collision depends on your game design:
- Player touches enemy = take damage
- Player touches coin = score goes up, coin disappears
- Player touches wall = stop moving

---

## Game States

Games have different "states" or modes:

```
TITLE SCREEN → PLAYING → GAME OVER
      ↑                      │
      └──────────────────────┘
           (press restart)
```

At any moment, the game is in ONE state. Each state draws different things and responds to buttons differently.

---

## Difficulty Curves

Great games get harder gradually:

```
Fun ↑
    │         ╱──── Sweet spot: challenging but fair
    │       ╱
    │     ╱
    │   ╱
    │ ╱
    └──────────────────────→ Time
  Easy                     Hard
```

- **Level 1:** Easy. The player learns how to play.
- **Level 2:** A little harder. One new thing is introduced.
- **Level 3:** Combines what they learned. More challenge.
- **Boss:** Everything at once. The ultimate test.

If Level 1 is too hard, players quit. If it's always easy, players get bored.

---

## Juice — The Secret Ingredient

"Juice" is the game design word for all the tiny details that make a game FEEL good:

- **Screen shake** when you get hit
- **Particles** when you collect a coin
- **A flash** when you land an attack
- **Sound effects** for every action
- **A slight pause** when you hit an enemy (called "hit stop")
- **The character squishing** slightly when they land a jump

Without juice: "I collected a coin." → boring
With juice: coin sparkles, score pops up big, a satisfying "ding!" plays → AWESOME!

---

## Player Feedback

The player should ALWAYS know:
- **What just happened** (visual + sound feedback)
- **How much health they have** (health bar, hearts, etc.)
- **What they can do** (clear button prompts)
- **Where to go** (visual cues, level design)

If a player ever says "wait, what happened?" — that's a design problem to fix.

---

## Fun Fact: All Games Are Rectangles

Even the most realistic 3D games use the same basic ideas:
- Characters have hitboxes (rectangles in 3D are just cubes)
- Movement is still position + speed
- Gravity still works the same way
- Collision detection still checks if shapes overlap

The only difference is more complexity. The fundamentals never change.

---

## Want to Learn More?

Use `/learn [topic]` in Claude to see any of these concepts in action. Claude will build a tiny demo and explain how it works.
