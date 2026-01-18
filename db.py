import sqlite3

DB_NAME = "users.db"

def connect():
    return sqlite3.connect(DB_NAME)


def create_table():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
        tg_id INTEGER PRIMARY KEY,
        student_id UNIQUE
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS book(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT,
           author TEXT,
           genre TEXT,
           description TEXT,
           borrowed_by TEXT,
           FOREIGN KEY (borrowed_by) REFERENCES users(student_id)
        )
        """)

        con.execute("""
           CREATE TABLE IF NOT EXISTS comments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              student_id INTEGER,
              comment TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (student_id) REFERENCES users(tg_id)
        )
        """)

def add_user(tg_id, student_id):
    with connect() as con:
         con.execute(
        "INSERT OR IGNORE INTO users (tg_id, student_id) VALUES (?, ?)",
        (tg_id, student_id)
         )


def get_user(tg_id):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        return cur.fetchone()

def update_student_id(tg_id, student_id):
    with connect() as con:
        con.execute("UPDATE users SET student_id = ? WHERE tg_id = ?",
                    (student_id, tg_id))


def search_books_in_db(keyword):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT name, author, genre, description, borrowed_by
            FROM book
            WHERE name LIKE ? OR author LIKE ? 
            """,
            (f"%{keyword}%", f"%{keyword}%")
        )
        return cur.fetchall()

def get_book_by_name(book_name):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT id, borrowed_by FROM book WHERE name = ?", (book_name,))
        return cur.fetchone()

def borrow_book_in_db(book_name, student_id):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE book SET borrowed_by = ? WHERE name = ? AND borrowed_by IS NULL", (student_id, book_name))
        return cur.rowcount

def return_book_in_db(book_name, student_id):
    with connect() as con:
        cur = con.cursor()
        con.execute(
            "UPDATE book SET borrowed_by = NULL WHERE name = ? AND borrowed_by = ?",
            (book_name, student_id)
        )
        return cur.rowcount

def izoh_yozish(student_id, comment):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO comments (student_id, comment) VALUES (?, ?)",
            (student_id, comment)
        )
        con.commit()

def add_books( name, author, genre, description):
    with connect() as con:
        con.execute(
            "INSERT INTO book (name, author, genre, description)"
            " VALUES (?, ?,?,?)", (name, author, genre, description)
        )

def get_book_full(name):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT id, name, author, genre, description FROM book WHERE name = ?",
            (name,)
        )
        return cur.fetchone()


def delete_book_by_name(book_name):
    with connect() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM book WHERE name = ?", (book_name,))
        return cur.rowcount

def get_all_comments():
    with connect() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT users.student_id, comments.comment, comments.created_at
            FROM comments
            JOIN users ON users.tg_id = comments.student_id
            ORDER BY comments.created_at DESC
        """)
        return cur.fetchall()
def count_books():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM book")
        return cur.fetchone()[0]


def count_borrowed_books():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM book WHERE borrowed_by IS NOT NULL")
        return cur.fetchone()[0]

def count_available_books():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM book WHERE borrowed_by IS NULL")
        return cur.fetchone()[0]

def count_users():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

def count_comments():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM comments")
        return cur.fetchone()[0]

