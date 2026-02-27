# Getting Started

## What You Need
- Your laptop (Windows)
- WiFi connection to `Chumbanet`
- The Raspberry Pi turned on (ask Mark if it's not)

---

## Step 1: Install VS Code

If VS Code isn't on your laptop yet:
1. Go to https://code.visualstudio.com
2. Download the Windows version
3. Install it (just click Next, Next, Next, Finish)

## Step 2: Install the Remote SSH Extension

1. Open VS Code
2. Click the Extensions icon on the left sidebar (looks like 4 squares)
3. Search for "Remote - SSH"
4. Click **Install** on the one by Microsoft

## Step 3: Connect to the Raspberry Pi

1. Press `Ctrl + Shift + P` to open the command palette
2. Type "Remote-SSH: Connect to Host"
3. Click "+ Add New SSH Host"
4. Type: `YOUR_USERNAME@192.168.1.230` (replace YOUR_USERNAME with your name — see team-info.md)
5. Press Enter, then select the first config file option
6. Click "Connect" when it appears in the bottom-right
7. Enter your password when asked (see team-info.md)
8. Wait for VS Code to set up (this takes a minute the first time)

## Step 4: Open Quest Craft

1. Once connected, click **File > Open Folder**
2. Navigate to `/home/mark/quest-craft`
3. Click **OK**
4. You should see all the project folders in the sidebar

## Step 5: Open the Terminal

1. Press `` Ctrl + ` `` (the backtick key, above Tab)
2. You should see a terminal at the bottom of VS Code
3. You're now running commands ON THE PI, not on your laptop!

## Step 6: Meet Claude

1. In the terminal, type: `claude`
2. Press Enter
3. Claude will start up — you'll see a prompt where you can type or talk
4. Try saying or typing: "Hi Claude! What slash commands can I use?"

## Step 7: Start Your First Brainstorm

Type or say: `/brainstorm`

Claude will ask you questions about your game idea. Answer honestly — there are no wrong answers!

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

### VS Code is slow
- This is normal the first time — it's installing stuff on the Pi
- Wait a few minutes, it gets faster

### Claude won't start
- Make sure you're in the terminal (not the VS Code search bar)
- Type `claude` and press Enter
- If it asks you to log in, ask Mark to help with authentication

---

## Quick Reference

| What You Want to Do | How to Do It |
|---------------------|-------------|
| Connect to Pi | `Ctrl+Shift+P` > "Remote-SSH: Connect to Host" |
| Open terminal | `` Ctrl + ` `` |
| Start Claude | Type `claude` in terminal |
| Brainstorm | Type `/brainstorm` in Claude |
| Design a feature | Type `/design-prd` in Claude |
| Start coding | Type `/start-coding` in Claude |
| Save your work | Claude handles git for you |
