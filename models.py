from database import get_connection

def get_all_assignments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assignments ORDER BY due_date").fetchall()
    conn.close()
    return rows

def add_assignment(subject, title, due_date):
    conn = get_connection()
    conn.execute("INSERT INTO assignments(subject,title,due_date,status,student_id) VALUES(?,?,?,?,?)",
                 (subject,title,due_date,"Pending",1))
    conn.commit()
    conn.close()

def mark_submitted(assignment_id):
    conn = get_connection()
    conn.execute("UPDATE assignments SET status='Submitted' WHERE id=?", (assignment_id,))
    conn.commit()
    conn.close()

def delete_assignment(assignment_id):
    conn = get_connection()
    conn.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
    conn.commit()
    conn.close()
