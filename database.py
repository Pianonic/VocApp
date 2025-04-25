# database.py
import sqlite3
import os

DATABASE = "vocabulary.db"


def get_db():
    """Connects to the specific database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initializes the database schema."""
    if os.path.exists(DATABASE):
        print("Database already exists.")
        return

    print("Initializing database...")
    conn = get_db()
    cursor = conn.cursor()

    # Create decks table
    cursor.execute(
        """
        CREATE TABLE decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            target_exam TEXT, -- e.g., 'Cambridge', 'DELF'
            level TEXT,       -- e.g., 'C1', 'B2'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create words table
    cursor.execute(
        """
        CREATE TABLE words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            definition TEXT NOT NULL,
            example TEXT,
            translation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
        )
    """
    )
    # ON DELETE CASCADE means if a deck is deleted, its words are also deleted

    conn.commit()
    conn.close()
    print("Database initialized.")


if __name__ == "__main__":
    # Run this script directly to initialize the DB
    init_db()
