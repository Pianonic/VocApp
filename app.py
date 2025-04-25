from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
    jsonify,
)
import sqlite3
import database
import json
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "a_default_secret_key_change_me")

def get_db():
    if "db" not in g:
        g.db = database.get_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM decks ORDER BY created_at DESC")
    decks = cursor.fetchall()
    return render_template("index.html", decks=decks)

@app.route("/create_deck", methods=["GET", "POST"])
def create_deck():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        target_exam = request.form.get("target_exam")
        level = request.form.get("level")

        if not name:
            flash("Deck Name is required.", "warning")
            return render_template("create_deck.html")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO decks (name, description, target_exam, level)
                VALUES (?, ?, ?, ?)
                """,
                (name, description, target_exam, level),
            )
            db.commit()
            flash(f"Deck '{name}' created successfully!", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            db.rollback()
            flash(f"Deck name '{name}' already exists. Please choose a different name.", "danger")
            return render_template("create_deck.html", form_data=request.form)
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {e}", "danger")
            app.logger.error(f"Error creating deck: {e}")
            return render_template("create_deck.html", form_data=request.form)

    return render_template("create_deck.html")

@app.route("/deck/<int:deck_id>", methods=["GET", "POST"])
def view_deck(deck_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST" and request.form.get("action") == "add_word":
        term = request.form.get("term")
        definition = request.form.get("definition")
        example = request.form.get("example")
        translation = request.form.get("translation")

        if not term or not definition:
            flash("Term and Definition are required to add a word.", "warning")
        else:
            try:
                cursor.execute(
                    """
                    INSERT INTO words (deck_id, term, definition, example, translation)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (deck_id, term, definition, example, translation),
                )
                db.commit()
                flash(f"Word '{term}' added successfully!", "success")
            except Exception as e:
                db.rollback()
                flash(f"An error occurred adding the word: {e}", "danger")
                app.logger.error(f"Error adding word to deck {deck_id}: {e}")

        return redirect(url_for("view_deck", deck_id=deck_id))

    cursor.execute("SELECT * FROM decks WHERE id = ?", (deck_id,))
    deck = cursor.fetchone()

    if not deck:
        flash("Deck not found.", "danger")
        return redirect(url_for("index"))

    cursor.execute(
        "SELECT * FROM words WHERE deck_id = ? ORDER BY RANDOM()", (deck_id,)
    )
    words = cursor.fetchall()

    return render_template("deck.html", deck=deck, words=words)

@app.route("/delete_deck/<int:deck_id>", methods=["POST"])
def delete_deck(deck_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT name FROM decks WHERE id = ?", (deck_id,))
        deck = cursor.fetchone()
        deck_name = deck['name'] if deck else f"ID {deck_id}"

        cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        db.commit()
        flash(f"Deck '{deck_name}' and all its words deleted.", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting deck: {e}", "danger")
        app.logger.error(f"Error deleting deck {deck_id}: {e}")

    return redirect(url_for("index"))

@app.route("/delete_word/<int:word_id>", methods=["POST"])
def delete_word(word_id):
    deck_id = request.form.get("deck_id")
    if not deck_id:
        flash("Could not determine which deck to return to.", "warning")
        return redirect(url_for("index"))

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT term FROM words WHERE id = ?", (word_id,))
        word = cursor.fetchone()
        word_term = word['term'] if word else f"ID {word_id}"

        cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
        db.commit()
        flash(f"Word '{word_term}' deleted.", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting word: {e}", "danger")
        app.logger.error(f"Error deleting word {word_id}: {e}")

    return redirect(url_for("view_deck", deck_id=deck_id))

@app.route("/learn/<int:deck_id>")
def learn_deck(deck_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM decks WHERE id = ?", (deck_id,))
    deck = cursor.fetchone()

    if not deck:
        flash("Deck not found.", "danger")
        return redirect(url_for("index"))

    cursor.execute(
        "SELECT id, term, definition, example, translation FROM words WHERE deck_id = ? ORDER BY RANDOM()",
        (deck_id,)
    )
    words_raw = cursor.fetchall()

    words = [dict(row) for row in words_raw]

    if not words:
        flash("This deck has no words to learn yet!", "warning")
        return redirect(url_for("view_deck", deck_id=deck_id))

    words_json = json.dumps(words)

    return render_template("learn.html", deck=deck, words_json=words_json, total_words=len(words))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
