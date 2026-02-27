# Getting Started

## What You Need
- Your laptop (Windows) with VS Code + Remote SSH extension installed
- Wispr Flow installed (for voice)
- WiFi connection to `Chumbanet`
- The Raspberry Pi turned on (ask Mark if it's not)

If you haven't installed these yet, see `docs/guides/prerequisites.md`.

---

## Step 1: Connect to the Raspberry Pi

1. Open VS Code
2. Press `Ctrl + Shift + P` to open the command palette
3. Type "Remote-SSH: Connect to Host"
4. Enter: `YOUR_USERNAME@192.168.1.230` (replace YOUR_USERNAME with your name — see team-info.md)
5. Enter your password when asked (see team-info.md)
6. Wait for VS Code to set up (first time takes a minute)

## Step 2: Open Quest Craft

1. Once connected, click **File > Open Folder**
2. Navigate to `/home/mark/quest-craft`
3. Click **OK**
4. You should see all the project folders in the sidebar

## Step 3: Open the Terminal

1. Press `` Ctrl + ` `` (the backtick key, above Tab)
2. You should see a terminal at the bottom of VS Code
3. You're now running commands ON THE PI, not on your laptop!

## Step 4: Meet Claude

1. In the terminal, type: `claude`
2. Press Enter
3. Claude will start up — you'll see a prompt

## Step 5: Test Wispr Flow

1. Make sure Wispr Flow is running (check your system tray)
2. Put your cursor in the Claude terminal
3. Hold the Wispr Flow key
4. Say: "Hi Claude! What can we do today?"
5. Let go of the key — your words appear as text
6. Press Enter — Claude responds!

## Step 6: Start Your First Session

Say or type: `/dream`

Claude will ask you questions about your game idea. Just talk! There are no wrong answers.

---

## Quick Reference

| What You Want to Do | How to Do It |
|---------------------|-------------|
| Connect to Pi | `Ctrl+Shift+P` > "Remote-SSH: Connect to Host" |
| Open terminal | `` Ctrl + ` `` |
| Start Claude | Type `claude` in terminal |
| Dream up the game | `/dream` |
| Design a topic | `/design characters` (or world, gameplay, etc.) |
| Create build plan | `/blueprint` |
| Build the game | `/build` |
| Report a bug | `/playtest` |
| Daily reflection | `/showcase` |
| Learn something | `/learn gravity` (or any concept) |

---

## Troubleshooting

### "Connection refused" or can't connect
- Make sure the Pi is turned on (green light on)
- Make sure you're on the `Chumbanet` WiFi
- Check your username is spelled right (lowercase)
- Ask Mark for help

### "Permission denied"
- Check your password is correct (see team-info.md)
- Make sure you're using the right username

### Claude won't start
- Make sure you're in the terminal (not the VS Code search bar)
- Type `claude` and press Enter
- If it asks to log in, ask Mark for help

### Wispr Flow isn't working
- Check it's running (look for the icon in your system tray)
- Make sure your cursor is in the Claude terminal
- Try holding the key longer and speaking clearly
