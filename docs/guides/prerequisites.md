# Prerequisites — What You Need Before Day 1

Hi parents and kids! Before the first session, please install these tools on your Windows laptop. It only takes about 10 minutes.

---

## Step 1: Install VS Code (Free)

**What it is:** The app where you'll write and build your game.

1. Go to https://code.visualstudio.com
2. Click the big blue "Download for Windows" button
3. Run the installer — accept all defaults
4. Open VS Code when it's done

### Install the Remote SSH Extension

This lets your laptop connect to the Raspberry Pi (the game computer).

1. In VS Code, click the square icon on the left sidebar (Extensions)
2. Search for: **Remote - SSH**
3. Click **Install** on the one by Microsoft
4. That's it!

---

## Step 2: Install Wispr Flow (Free)

**What it is:** A voice-to-text tool. Kids just TALK and it types for them. This is how they'll communicate with the AI.

1. Go to https://www.wispr.com/flow
2. Download and install
3. Follow the setup wizard
4. **Practice:** Open any text box, hold the Wispr Flow key, speak, and let go. Your words should appear as text!

---

## Step 3: That's It!

Everything else runs on the Raspberry Pi — Python, the game engine, the AI (Claude Code), and Git. Your laptop just needs VS Code to connect to the Pi.

### You DON'T Need to Install
- Python (on the Pi)
- Claude Code (on the Pi)
- Git (on the Pi)
- Pygame (on the Pi)

---

## Test Your Setup

Want to make sure everything works? Try connecting to the Pi:

1. Make sure your laptop is on the **Chumbanet** WiFi network
2. Open VS Code
3. Press `Ctrl+Shift+P` (opens the command palette)
4. Type: **Remote-SSH: Connect to Host**
5. Enter: `USERNAME@192.168.1.230` (replace USERNAME with your name — ask Mark)
6. When asked for a password, enter it (ask Mark for your password)
7. If you see files on the left side — you're connected!

**Note:** The Pi needs to be turned on for this to work. If it doesn't connect, that's okay — we'll sort it out on Day 1.

---

## Questions?

Ask Mark! He set everything up and can help troubleshoot.
