# Meshtastic Listener

A minimal web dashboard for permanently saving and displaying Meshtastic messages using SQLite database.
The `listner.py`  also send a predefined hello message at default channel when see a new message from somebody.


This project assume you have set and working meshastic node connected to PC via USB cable.


It is built with **FastAPI**, and designed to show messages with optional GPS coordinates
---

## Features

- Displays Meshtastic messages from `messages.db` (SQLite)
- Optional GPS coordinates with clickable Google Maps links
- Auto-reply with predefined text
- anti-spam feature to reply only once every X minutes
- Pagination support
- Retro hacker-style UI (lime green terminal theme)
- Lightweight (FastAPI + SQLite)

---

## Tech

- Python 3.9+
- FastAPI
- SQLite
- HTML + CSS

---
## Config

Please change these variables inside `listner.py` to match your needs:

```
AUTO_REPLY_TEXT = "You found my auto-reply mesh node!"
AUTO_REPLY_INTERVAL_MINUTES = 5 // Cooldown to auto-reply to same node will take x > 5min.
DEFAULT_CHANNEL_INDEX = 0 // Using default channel set for the node
NODE_PATH = "/dev/ttyACM0" // Path to the connected meshtasic device
```
---
## Execution

run web UI server with: `uvicorn app:app --host 0.0.0.0 --port 8000`

run message-listen with: `python listener.py`


↑ Works best when set as systemd service.
---

<img width="1008" height="762" alt="Screenshot" src="https://github.com/user-attachments/assets/967cef43-1af4-4f75-8af4-2b770816885b" />
