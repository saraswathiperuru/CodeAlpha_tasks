from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("urls.db")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():
    short_url = ""

    if request.method == "POST":
        original_url = request.form.get("url", "").strip()

        if not original_url.startswith(("http://", "https://")):
            return "Please enter a valid URL", 400

        connection = sqlite3.connect("urls.db")

        short_code = "".join(
            random.choices(string.ascii_letters + string.digits, k=6)
        )

        connection.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
            (short_code, original_url)
        )

        connection.commit()
        connection.close()

        short_url = request.host_url + short_code

    connection = sqlite3.connect("urls.db")

    urls = connection.execute(
        "SELECT original_url, short_code FROM urls ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        short_url=short_url,
        urls=urls
    )


@app.route("/<short_code>")
def redirect_url(short_code):
    connection = sqlite3.connect("urls.db")

    result = connection.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    connection.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


if __name__ == "__main__":
    create_database()
    app.run(debug=True)