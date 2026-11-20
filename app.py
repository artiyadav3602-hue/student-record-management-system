from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def create_table():
    con = sqlite3.connect("students.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            course TEXT,
            email TEXT
        )
    """)
    con.commit()
    con.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        email = request.form["email"]

        con = sqlite3.connect("students.db")
        con.execute(
            "INSERT INTO students (name, roll, course, email) VALUES (?, ?, ?, ?)",
            (name, roll, course, email)
        )
        con.commit()
        con.close()

        return redirect("/")

    return render_template("add.html")
@app.route("/view")
def view_students():
    con = sqlite3.connect("students.db")
    con.row_factory = sqlite3.Row
    students = con.execute("SELECT * FROM students").fetchall()
    con.close()

    return render_template("view.html", students=students)
@app.route("/search", methods=["GET", "POST"])
def search_student():
    student = None

    if request.method == "POST":
        roll = request.form["roll"]

        con = sqlite3.connect("students.db")
        con.row_factory = sqlite3.Row
        student = con.execute(
            "SELECT * FROM students WHERE roll = ?", (roll,)
        ).fetchone()
        con.close()

    return render_template("search.html", student=student)
@app.route("/update", methods=["GET", "POST"])
def update_student():
    message = ""

    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        course = request.form["course"]
        email = request.form["email"]

        con = sqlite3.connect("students.db")
        cursor = con.execute(
            "UPDATE students SET name=?, course=?, email=? WHERE roll=?",
            (name, course, email, roll)
        )
        con.commit()

        if cursor.rowcount > 0:
            message = "Student record updated successfully!"
        else:
            message = "Student not found!"

        con.close()

    return render_template("update.html", message=message)
@app.route("/delete", methods=["GET", "POST"])
def delete_student():
    message = ""

    if request.method == "POST":
        roll = request.form["roll"]

        con = sqlite3.connect("students.db")
        cursor = con.execute(
            "DELETE FROM students WHERE roll=?", (roll,)
        )
        con.commit()

        if cursor.rowcount > 0:
            message = "Student deleted successfully!"
        else:
            message = "Student not found!"

        con.close()

    return render_template("delete.html", message=message)
create_table()

if __name__ == "__main__":
    app.run(debug=True)