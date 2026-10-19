"""
Quote Board - a tiny Flask app for the Docker Swarm demo.

- Shows a random quote stored in Redis.
- Lets you add new quotes (they are shared by every replica, because they live in Redis).
- Shows WHICH container answered the request, so you can see Swarm load-balancing
  between replicas when you refresh the page.
"""
import os
import random
import socket

import redis
from flask import Flask, jsonify, redirect, render_template_string, request

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
APP_COLOR = os.getenv("APP_COLOR", "#2563eb")

db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True,
                 socket_connect_timeout=2)

HOSTNAME = socket.gethostname()  # inside a container this is the container ID

STARTER_QUOTES = [
    "Simplicity is prerequisite for reliability. - Edsger Dijkstra",
    "First, solve the problem. Then, write the code. - John Johnson",
    "It works on my machine. - Every developer, before Docker",
    "Talk is cheap. Show me the code. - Linus Torvalds",
    "Make it work, make it right, make it fast. - Kent Beck",
]

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Quote Board</title>
  <style>
    body { font-family: system-ui, sans-serif; background:#f1f5f9; margin:0; padding:40px 16px; }
    .card { max-width:640px; margin:auto; background:white; border-radius:14px;
            box-shadow:0 4px 18px rgba(0,0,0,.08); padding:32px; }
    h1 { margin-top:0; color:{{ color }}; }
    blockquote { font-size:1.4rem; margin:24px 0; padding-left:16px;
                 border-left:4px solid {{ color }}; }
    .who { background:#0f172a; color:#a5f3fc; font-family:monospace; padding:12px 16px;
           border-radius:8px; font-size:1.05rem; }
    .stats { color:#475569; margin:16px 0; }
    form { display:flex; gap:8px; margin-top:24px; }
    input { flex:1; padding:10px; border:1px solid #cbd5e1; border-radius:8px; }
    button, a.btn { background:{{ color }}; color:white; border:0; padding:10px 16px;
             border-radius:8px; cursor:pointer; text-decoration:none; }
    .err { color:#b91c1c; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Quote Board</h1>
    {% if error %}
      <p class="err">Cannot reach Redis yet: {{ error }}</p>
    {% else %}
      <blockquote>{{ quote }}</blockquote>
      <p class="stats">Quotes stored: <b>{{ total }}</b> &nbsp;|&nbsp; Total page views: <b>{{ views }}</b></p>
    {% endif %}
    <div class="who">Served by container: <b>{{ hostname }}</b></div>
    <form method="post" action="/add">
      <input name="quote" placeholder="Add your own quote..." required maxlength="200">
      <button type="submit">Add</button>
    </form>
    <p><a class="btn" href="/">Next quote / refresh</a></p>
  </div>
</body>
</html>
"""


def seed_quotes():
    """Put a few starter quotes in Redis the first time."""
    if db.llen("quotes") == 0:
        db.rpush("quotes", *STARTER_QUOTES)


@app.route("/")
def index():
    try:
        seed_quotes()
        views = db.incr("views")
        total = db.llen("quotes")
        quote = db.lindex("quotes", random.randrange(total))
        return render_template_string(PAGE, quote=quote, total=total, views=views,
                                      hostname=HOSTNAME, color=APP_COLOR, error=None)
    except redis.RedisError as exc:
        return render_template_string(PAGE, hostname=HOSTNAME, color=APP_COLOR,
                                      error=str(exc)), 503


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("quote", "").strip()
    if text:
        db.rpush("quotes", text[:200])
    return redirect("/")


@app.route("/whoami")
def whoami():
    """Small JSON endpoint - handy for a curl loop during the scaling demo."""
    return jsonify(container=HOSTNAME)


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
