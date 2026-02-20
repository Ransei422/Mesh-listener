import time
import sqlite3
from datetime import datetime

import meshtastic.serial_interface
from pubsub import pub


# ---- CONFIG ----
AUTO_REPLY_TEXT = "You found my auto-reply mesh node!"
AUTO_REPLY_INTERVAL_MINUTES = 5
DEFAULT_CHANNEL_INDEX = 0
NODE_PATH = "/dev/ttyACM0"


# ---- Database setup ----
conn = sqlite3.connect("messages.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    sender TEXT,
    message TEXT,
    latitude REAL,
    longitude REAL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS node_positions (
    node_id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    last_updated TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS auto_reply_cooldown (
    node_id INTEGER PRIMARY KEY,
    last_reply TEXT
)
""")

conn.commit()


# ---- Connect to Meshtastic node ----
interface = meshtastic.serial_interface.SerialInterface(devPath=NODE_PATH)
my_node_id = interface.myInfo.my_node_num


# ---- Cooldown helper function ----
def can_send_auto_reply(sender_num):
    now = datetime.now()

    c.execute("""
        SELECT last_reply FROM auto_reply_cooldown
        WHERE node_id=?
    """, (sender_num,))
    row = c.fetchone()

    if row:
        last_reply_time = datetime.fromisoformat(row[0])
        seconds_passed = (now - last_reply_time).total_seconds()

        if seconds_passed < AUTO_REPLY_INTERVAL_MINUTES * 60:
            return False

    c.execute("""
        INSERT OR REPLACE INTO auto_reply_cooldown (node_id, last_reply)
        VALUES (?, ?)
    """, (sender_num, now.isoformat()))
    conn.commit()

    return True


def on_receive(packet, interface):
    try:
        timestamp = datetime.now().isoformat()

        # POSITION PACKET
        if packet.get("decoded") and "position" in packet["decoded"]:
            pos = packet["decoded"]["position"]
            sender_num = packet.get("from")

            lat = pos.get("latitude")
            lon = pos.get("longitude")

            if lat and lon:
                c.execute("""
                    INSERT OR REPLACE INTO node_positions
                    (node_id, latitude, longitude, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (sender_num, lat, lon, timestamp))
                conn.commit()

                print(f"Updated position for {sender_num}: {lat}, {lon}")

        # TEXT MESSAGE
        if packet.get("decoded") and "text" in packet["decoded"]:
            sender = packet.get("fromId", "unknown")
            sender_num = packet.get("from")
            message = packet["decoded"]["text"]
            channel_index = packet.get("channel", 0)

            c.execute("""
                SELECT latitude, longitude
                FROM node_positions
                WHERE node_id=?
            """, (sender_num,))
            pos = c.fetchone()

            lat = pos[0] if pos else None
            lon = pos[1] if pos else None

            c.execute("""
                INSERT INTO messages
                (timestamp, sender, message, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, sender, message, lat, lon))
            conn.commit()

            print(f"[{timestamp}] {sender}: {message}")

            # SQLITE-BASED AUTO REPLY
            if (
                sender_num != my_node_id and
                channel_index == DEFAULT_CHANNEL_INDEX
            ):
                if can_send_auto_reply(sender_num):
                    interface.sendText(
                        AUTO_REPLY_TEXT,
                        channelIndex=DEFAULT_CHANNEL_INDEX
                    )
                    print("Auto-replied to", sender)
                else:
                    print("Auto-reply skipped (cooldown active)")

    except Exception as e:
        print("Error:", e)


pub.subscribe(on_receive, "meshtastic.receive")

print("Listening for Meshtastic messages...")

while True:
    time.sleep(1)
