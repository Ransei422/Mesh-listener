# Meshtastic Listener

A minimal web dashboard for displaying Meshtastic messages stored in a SQLite database - aiming for data persistency.
The `listner.py` not just listen for messages, but also executing auto-reply at default channel for first message from newly seen node in set time period.

Built with **FastAPI**, and designed to show messages with optional GPS coordinates

---

## Features

- Displays Meshtastic messages from `messages.db`
- Optional GPS coordinates with clickable Google Maps links
- Auto-reply with predefined text
- anti-spam feature to reply only once every X minutes
- Pagination support
- Retro hacker-style UI (lime green terminal theme)
- Lightweight (FastAPI + SQLite)

---

## Tech Stack

- Python 3.9+
- FastAPI
- SQLite
- HTML + CSS

---


## Execution

run web UI server with: `uvicorn app:app --host 0.0.0.0 --port 8000`

run message-listen with: `python listener.py`

(Best used as systemd service)
---

<img width="1008" height="762" alt="Screenshot" src="https://github.com/user-attachments/assets/967cef43-1af4-4f75-8af4-2b770816885b" />
