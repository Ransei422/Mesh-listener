import math
import sqlite3
from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI()
PAGE_SIZE = 5


def get_total_messages():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages")
    total = c.fetchone()[0]
    conn.close()
    return total


def get_messages(offset, limit):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, sender, message, latitude, longitude
        FROM messages
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall()
    conn.close()
    return rows


@app.get("/", response_class=HTMLResponse)
def dashboard(page: int = Query(1, ge=1)):
    total_messages = get_total_messages()
    total_pages = max(1, math.ceil(total_messages / PAGE_SIZE))

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * PAGE_SIZE
    messages = get_messages(offset, PAGE_SIZE)

    html = f"""
    <html>
    <head>
        <title>Meshtastic Terminal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Google Hack Font -->
        <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">

        <style>
            body {{
                background-color: #000000;
                color: #00ff41;
                font-family: 'Share Tech Mono', monospace;
                margin: 0;
                padding: 20px;
                text-shadow: 0 0 5px #00ff41;
            }}

            h1 {{
                text-align: center;
                margin-bottom: 30px;
                font-size: 28px;
                letter-spacing: 2px;
                border-bottom: 1px solid #00ff41;
                padding-bottom: 10px;
            }}

            .container {{
                max-width: 900px;
                margin: auto;
            }}

            .message {{
                border: 1px solid #00ff41;
                padding: 15px;
                margin-bottom: 15px;
                background: rgba(0, 255, 65, 0.05);
                box-shadow: 0 0 10px #00ff41;
                border-radius: 10px;
            }}

            .meta {{
                font-size: 0.8em;
                color: #00cc33;
                margin-bottom: 8px;
            }}

            .text {{
                font-size: 1.05em;
                margin-bottom: 8px;
                word-wrap: break-word;
                color: #DD4814;
                text-shadow: 0 0 5px #DD4814; 
            }}

            .gps {{
                font-size: 0.8em;
                color: #00ffcc;
            }}

            .gps a {{
                color: #00ffcc;
                text-decoration: none;
            }}

            .gps a:hover {{
                text-decoration: underline;
            }}

            .pagination {{
                text-align: center;
                margin-top: 30px;
            }}

            .btn {{
                display: inline-block;
                padding: 8px 14px;
                margin: 5px;
                border: 1px solid #00ff41;
                color: #00ff41;
                text-decoration: none;
                background: black;
                box-shadow: 0 0 8px #00ff41;
            }}

            .btn:hover {{
                background: #00ff41;
                color: black;
                text-shadow: none;
            }}

            .disabled {{
                opacity: 0.4;
                pointer-events: none;
            }}

            /* Subtle scanline effect */
            body::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: repeating-linear-gradient(
                    0deg,
                    rgba(0, 255, 65, 0.03),
                    rgba(0, 255, 65, 0.03) 1px,
                    transparent 1px,
                    transparent 3px
                );
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📡 MESHTASTIC LISTENER</h1>
    """

    for timestamp, sender, message, lat, lon in messages:
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        gps_html = ""
        if lat is not None and lon is not None:
            gps_html = f"""
            <div class="gps">
                [GPS] <a href="https://maps.google.com/?q={lat},{lon}" target="_blank">
                {lat:.5f}, {lon:.5f}
                </a>
            </div>
            """

        html += f"""
            <div class="message">
                <div class="meta">
                    [{formatted_time}] :: NODE {sender}
                </div>
                <div class="text">
                    > {message}
                </div>
                {gps_html}
            </div>
        """

    html += '<div class="pagination">'

    if page > 1:
        html += f'<a class="btn" href="/?page={page-1}"><< PREV</a>'
    else:
        html += '<span class="btn disabled"><< PREV</span>'

    html += f'<span class="btn disabled">PAGE {page}/{total_pages}</span>'

    if page < total_pages:
        html += f'<a class="btn" href="/?page={page+1}">NEXT >></a>'
    else:
        html += '<span class="btn disabled">NEXT >></span>'

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html