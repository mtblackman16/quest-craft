# Talking to Claude — Your AI Coding Partner

Claude is an AI that lives in your terminal. You can type to it or talk to it using Wispr Flow. Here's how to get the most out of it.

---

## Starting Claude

1. Open the terminal in VS Code (`` Ctrl + ` ``)
2. Type `claude` and press Enter
3. You're now talking to Claude!

## Using Voice (Wispr Flow)

Wispr Flow lets you talk instead of type. Just speak naturally and it types for you.

- Click the Wispr icon or use the shortcut to activate
- Talk normally — "Hey Claude, how do I make the player move right?"
- Wispr types your words into the Claude prompt

---

## Slash Commands — Quick Shortcuts

These are special commands that tell Claude to switch modes:

| Say This | What Happens |
|----------|-------------|
| `/brainstorm` | Creative brainstorming session |
| `/design-prd` | Write a design document for a game feature |
| `/review-prd` | Review a design document |
| `/start-coding` | Start coding a feature (checks PRDs first) |
| `/learn` | Learn a new programming concept |
| `/log-today` | Write your daily learning log |

---

## How to Ask Good Questions

### Be Specific

| Instead of... | Try... |
|--------------|--------|
| "It's broken" | "The player goes through walls instead of stopping" |
| "Fix it" | "The score doesn't go up when I collect a coin" |
| "Help" | "How do I make the enemy follow the player?" |
| "Make it better" | "Make the player move faster when they hold the B button" |

### Describe What You See

Claude can't see your screen, so describe what's happening:
- "When I press A, nothing happens"
- "The enemy appears in the wrong spot — it's at the top-left instead of the right side"
- "The game crashes when I collect the third coin"

### Ask "Why" to Learn

- "Why do we need `clock.tick(60)`?"
- "Why does the player fall through the floor?"
- "What does this line do?" (then paste the line)

---

## Example Conversations

### Asking for Help with a Bug
> **You:** "The player can jump infinitely. They should only jump when they're on the ground."
>
> Claude will help you add a ground check.

### Learning Something New
> **You:** `/learn`
>
> Claude: "What do you want to learn about?"
>
> **You:** "How do collisions work?"
>
> Claude will explain collision detection with examples from your game.

### Designing a Feature
> **You:** `/design-prd`
>
> Claude: "What part of the game do you want to design?"
>
> **You:** "The enemy system — I want goblins that chase the player"
>
> Claude will walk you through designing it step by step.

### Getting Unstuck
> **You:** "I don't know what to do next"
>
> Claude will check the PRDs and master plan, then suggest the next task.

---

## Tips

1. **Don't be shy** — Claude likes questions. Ask as many as you want.
2. **It's OK to not understand** — Just say "I don't get it, explain it simpler"
3. **You can change your mind** — "Actually, I want the enemy to be blue, not red"
4. **Claude remembers your project** — It knows what PRDs exist, what code you've written
5. **If Claude gets confused** — Start a new conversation and explain what you need fresh
6. **Save important decisions** — Tell Claude "Remember that we decided to use pixel art"

---

## Things Claude Can't Do

- Claude can't see your screen (describe what you see)
- Claude can't play the game (you need to test it)
- Claude can't draw pictures (but it can write code that draws things)
- Claude can't fix the Pi hardware (ask Mark)
- Claude won't write the whole game for you (it helps YOU write it)
