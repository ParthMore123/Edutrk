from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_NAME = "student.db"
_db_initialized = False

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            title TEXT,
            due_date TEXT,
            status TEXT,
            student_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


@app.before_request
def initialize_database():
    """Ensure the database and tables exist before handling requests.
    This runs once before the first request in Flask 2.0+.
    """
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM assignments WHERE status='Pending'").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM assignments WHERE status='Submitted'").fetchone()[0]
    conn.close()
    return render_template("dashboard.html", total=total, pending=pending, completed=completed)

@app.route("/subjects")
def subjects():
    conn = get_db_connection()
    subjects = conn.execute("SELECT DISTINCT subject FROM assignments").fetchall()
    conn.close()
    return render_template("subjects.html", subjects=subjects)

@app.route("/assignments")
def assignments():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM assignments ORDER BY due_date").fetchall()
    conn.close()
    return render_template("assignments.html", assignments=rows)

@app.route("/add-assignment", methods=["GET","POST"])
def add_assignment():
    if request.method=="POST":
        subject=request.form["subject"]
        title=request.form["title"]
        due_date=request.form["due_date"]
        conn=get_db_connection()
        conn.execute("INSERT INTO assignments(subject,title,due_date,status,student_id) VALUES(?,?,?,?,?)",
                     (subject,title,due_date,"Pending",1))
        conn.commit()
        conn.close()
        return redirect(url_for("assignments"))
    return render_template("add_assignment.html")

@app.route("/submit/<int:id>")
def submit_assignment(id):
    conn=get_db_connection()
    conn.execute("UPDATE assignments SET status='Submitted' WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect(url_for("assignments"))

@app.route("/delete/<int:id>")
def delete_assignment(id):
    conn=get_db_connection()
    conn.execute("DELETE FROM assignments WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect(url_for("assignments"))

if __name__=="__main__":
    init_db()
    app.run(debug=True)
