"""
Radio Room - a small live chat app.

Read this file top to bottom; it is the whole backend.

Messages are kept in a normal Python list, so they disappear when the app
restarts. That is on purpose - it keeps this file short enough to read in
one sitting. Swapping in a real database is a later exercise.
"""

import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

# Our "database": just a list that lives in memory.
# Each item looks like {"name": "Arun", "text": "hello", "time": "14:32"}
messages = []

# Stop the list growing forever if the app stays up for days.
MAX_MESSAGES = 200


@app.route("/")
def index():
    """The landing page: the picture, the headline, and the name box."""
    return render_template("index.html", message_count=len(messages))


@app.route("/room")
def room():
    """The chat room. The name arrives in the URL, like /room?name=Arun"""
    name = request.args.get("name", "").strip()

    # Someone opened /room directly with no name. Send them back to pick one.
    if not name:
        return redirect(url_for("index"))

    return render_template(
        "room.html",
        name=name[:20],
        hostname=os.environ.get("HOSTNAME", "your laptop"),
    )


@app.route("/api/messages")
def read_messages():
    """The browser calls this every 2 seconds to pick up new messages."""
    return jsonify(messages)


@app.route("/api/messages", methods=["POST"])
def write_message():
    """The browser calls this when you press Send."""
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()[:20]
    text = str(data.get("text", "")).strip()[:500]

    # Refuse empty messages rather than storing junk.
    if not name or not text:
        return jsonify({"error": "A name and a message are both required."}), 400

    messages.append(
        {"name": name, "text": text, "time": datetime.now().strftime("%H:%M")}
    )

    # Keep only the most recent messages.
    del messages[:-MAX_MESSAGES]

    return jsonify({"ok": True}), 201


@app.route("/health")
def health():
    """
    A health check. Monitoring tools and Kubernetes call this every few
    seconds to ask "are you still alive?". If it stops answering, the app
    gets restarted or taken out of rotation.
    """
    return {"status": "ok", "messages": len(messages)}


if __name__ == "__main__":
    # host="0.0.0.0" means "accept connections from outside this machine".
    # Inside Docker this is required, otherwise nobody can reach the app.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
