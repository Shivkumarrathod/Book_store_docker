# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("BOOKS_DB", os.path.join(BASE_DIR, "instance", "books.db"))

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "dev-secret")  # override in prod
app.config["DATABASE"] = DATABASE

# Ensure instance folder exists
os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        year INTEGER,
        description TEXT
    );
    """)
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.before_first_request
def before_first():
    init_db()

@app.route("/")
def index():
    db = get_db()
    cur = db.execute("SELECT * FROM books ORDER BY id DESC")
    books = cur.fetchall()
    return render_template("index.html", books=books)

@app.route("/book/new", methods=("GET", "POST"))
def create_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("create.html")

        db = get_db()
        db.execute(
            "INSERT INTO books (title, author, year, description) VALUES (?, ?, ?, ?)",
            (title, author or None, int(year) if year else None, description or None),
        )
        db.commit()
        flash("Book created successfully.", "success")
        return redirect(url_for("index"))

    return render_template("create.html")

@app.route("/book/<int:book_id>/edit", methods=("GET", "POST"))
def edit_book(book_id):
    db = get_db()
    cur = db.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cur.fetchone()
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("edit.html", book=book)

        db.execute(
            "UPDATE books SET title = ?, author = ?, year = ?, description = ? WHERE id = ?",
            (title, author or None, int(year) if year else None, description or None, book_id),
        )
        db.commit()
        flash("Book updated.", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", book=book)

@app.route("/book/<int:book_id>/delete", methods=("POST",))
def delete_book(book_id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    flash("Book deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # For development; container will use gunicorn command
    app.run(host="0.0.0.0", port=5000, debug=True)
