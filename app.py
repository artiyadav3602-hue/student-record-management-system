
from flask import Flask, render_template, request, redirect, abort
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Photo upload settings
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# CREATE TABLE AND UPDATE OLD DATABASE
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

    existing_columns = [
        row[1] for row in con.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    ]

    new_columns = {
        "phone": "TEXT",
        "cgpa": "REAL",
        "semester": "TEXT",
        "address": "TEXT",
        "photo": "TEXT"
    }

    for column, datatype in new_columns.items():
        if column not in existing_columns:
            con.execute(
                f"ALTER TABLE students ADD COLUMN {column} {datatype}"
            )

    con.commit()
    con.close()


@app.route("/")
def home():
    return render_template("home.html")


# ADD STUDENT
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        email = request.form["email"]

        phone = request.form.get("phone", "")
        cgpa = request.form.get("cgpa") or None
        semester = request.form.get("semester", "")
        address = request.form.get("address", "")

        # PHOTO UPLOAD
        photo = request.files.get("photo")
        photo_filename = None

        if photo and photo.filename:
            if not allowed_file(photo.filename):
                abort(400, description="Only PNG, JPG, JPEG and WEBP images are allowed.")

            extension = photo.filename.rsplit(".", 1)[1].lower()
            photo_filename = str(uuid.uuid4()) + "." + extension

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    secure_filename(photo_filename)
                )
            )

        con = sqlite3.connect("students.db")

        con.execute("""
            INSERT INTO students
            (name, roll, course, email, phone, cgpa, semester, address, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, roll, course, email,
            phone, cgpa, semester, address, photo_filename
        ))

        con.commit()
        con.close()

        return redirect("/view")

    return render_template("add.html")


# VIEW STUDENTS
@app.route("/view")
def view_students():
    return "Access Denied", 403

# SEARCH STUDENT
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


# UPDATE STUDENT

@app.route("/update", methods=["GET", "POST"])
def update_student():
    message = ""

    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        course = request.form["course"]
        email = request.form["email"]
        phone = request.form.get("phone", "")
        cgpa = request.form.get("cgpa") or None
        semester = request.form.get("semester", "")
        address = request.form.get("address", "")

        con = sqlite3.connect("students.db")

        cursor = con.execute("""
            UPDATE students
            SET name=?, course=?, email=?, phone=?,
                cgpa=?, semester=?, address=?
            WHERE roll=?
        """, (name, course, email, phone, cgpa,
              semester, address, roll))

        con.commit()

        if cursor.rowcount > 0:
            message = "Student record updated successfully!"
        else:
            message = "Student not found!"

        con.close()

    return render_template("update.html", message=message)

# DELETE STUDENT
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
