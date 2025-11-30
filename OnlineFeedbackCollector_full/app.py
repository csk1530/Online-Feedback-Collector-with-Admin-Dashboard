import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import (
    Flask, g, render_template, request, redirect, url_for,
    jsonify, session, send_file, flash
)
from werkzeug.security import check_password_hash, generate_password_hash
from io import StringIO, BytesIO

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

app = Flask(__name__)
app.secret_key = "change-me-to-a-secure-random-value"

# Demo admin credentials (change for production)
ADMIN_USERNAME = "admin"
# Default password: admin123 (hash is generated at runtime from this string).
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        rating INTEGER NOT NULL CHECK(rating>=1 AND rating<=5),
        comments TEXT,
        date_submitted TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Initialize DB at startup if not present
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json() or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    rating = data.get("rating")
    comments = (data.get("comments") or "").strip()

    # server-side validation
    if not name:
        return jsonify({"success": False, "error": "Name is required."}), 400
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError()
    except Exception:
        return jsonify({"success": False, "error": "Rating must be integer 1-5."}), 400

    date_submitted = datetime.utcnow().isoformat()

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO feedback (name, email, rating, comments, date_submitted) VALUES (?, ?, ?, ?, ?)",
        (name, email, rating, comments, date_submitted)
    )
    db.commit()
    return jsonify({"success": True, "message": "Feedback submitted. Thank you!"})

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapped

@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM feedback ORDER BY date_submitted DESC")
    rows = cur.fetchall()

    # compute stats
    total = len(rows)
    avg_rating = 0
    rating_counts = {str(i):0 for i in range(1,6)}
    if total:
        s = 0
        for r in rows:
            rt = int(r["rating"]) if isinstance(r, dict) is False else int(r["rating"])
            s += rt
            rating_counts[str(rt)] += 1
        avg_rating = round(s / total, 2)
    return render_template("admin.html", feedbacks=rows, total=total, avg_rating=avg_rating, rating_counts=rating_counts)

@app.route("/export-csv")
@admin_required
def export_csv():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY date_submitted DESC")
    rows = cur.fetchall()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["id", "name", "email", "rating", "comments", "date_submitted"])
    for r in rows:
        # sqlite3.Row supports mapping access
        cw.writerow([r["id"], r["name"], r["email"], r["rating"], r["comments"], r["date_submitted"]])
    si.seek(0)

    return send_file(
        BytesIO(si.getvalue().encode("utf-8")),
        as_attachment=True,
        download_name="feedback_export.csv",
        mimetype="text/csv"
    )

@app.route("/api/feedback", methods=["GET"])
def api_feedback():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, email, rating, comments, date_submitted FROM feedback ORDER BY date_submitted DESC")
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "name": r["name"],
            "email": r["email"],
            "rating": r["rating"],
            "comments": r["comments"],
            "date_submitted": r["date_submitted"],
        })
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
