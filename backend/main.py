from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import get_db_connection

app = FastAPI()

# ENABLE CORS

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

# REGISTER ROUTE

@app.post("/register")
def register(

    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)

):

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        # CHECK EMAIL

        check_query = """
        SELECT * FROM users
        WHERE email=%s
        """

        cursor.execute(check_query, (email,))

        existing_user = cursor.fetchone()

        if existing_user:

            return {
                "message": "Email already registered"
            }

        # INSERT USER

        query = """
        INSERT INTO users

        (name, email, password, role)

        VALUES (%s, %s, %s, %s)
        """

        values = (

            name,
            email,
            password,
            "student"

        )

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "message": "User Registered Successfully"
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# LOGIN ROUTE

@app.post("/login")
def login(

    email: str = Form(...),
    password: str = Form(...)

):

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users

        WHERE email=%s
        AND password=%s
        """

        values = (email, password)

        cursor.execute(query, values)

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            return {

                "message": "Login Successful",

                "user": user

            }

        else:

            return {

                "message":
                "Invalid Email or Password"

            }

    except Exception as e:

        return {
            "error": str(e)
        }

# GET ALL BOOKS

@app.get("/books")
def get_books():

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM books"

        cursor.execute(query)

        books = cursor.fetchall()

        cursor.close()
        conn.close()

        return books

    except Exception as e:

        return {
            "error": str(e)
        }

# ADD BOOK

@app.post("/add-book")
def add_book(

    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    role: str = Form(...)

):

    try:

        # ADMIN CHECK

        if role != "admin":

            return {
                "message": "Access Denied"
            }

        conn = get_db_connection()

        cursor = conn.cursor()

        query = """
        INSERT INTO books

        (title, author, category,
        quantity, available_quantity)

        VALUES (%s, %s, %s, %s, %s)
        """

        values = (

            title,
            author,
            category,
            quantity,
            quantity

        )

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return {

            "message":
            "Book Added Successfully"

        }

    except Exception as e:

        return {
            "error": str(e)
        }

# ISSUE BOOK

@app.post("/issue-book")
def issue_book(

    user_id: int = Form(...),
    book_id: int = Form(...)

):

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM books
        WHERE id=%s
        """

        cursor.execute(query, (book_id,))

        book = cursor.fetchone()

        if not book:

            return {
                "message": "Book not found"
            }

        if book["available_quantity"] <= 0:

            return {
                "message": "Book not available"
            }

        issue_query = """
        INSERT INTO issued_books
        (user_id, book_id)

        VALUES (%s, %s)
        """

        cursor.execute(
            issue_query,
            (user_id, book_id)
        )

        update_query = """
        UPDATE books

        SET available_quantity =
        available_quantity - 1

        WHERE id=%s
        """

        cursor.execute(update_query, (book_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "message":
            "Book Issued Successfully"
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# MY BOOKS

@app.get("/my-books/{user_id}")
def my_books(user_id: int):

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT

        issued_books.id,
        books.title,
        books.author,
        books.category,
        issued_books.issue_date

        FROM issued_books

        JOIN books
        ON issued_books.book_id = books.id

        WHERE issued_books.user_id = %s
        """

        cursor.execute(query, (user_id,))

        books = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "books": books
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# RETURN BOOK

@app.post("/return-book")
def return_book(issue_id: int = Form(...)):

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM issued_books
        WHERE id=%s
        """

        cursor.execute(query, (issue_id,))

        issue = cursor.fetchone()

        if not issue:

            return {
                "message":
                "Issued record not found"
            }

        book_id = issue["book_id"]

        delete_query = """
        DELETE FROM issued_books
        WHERE id=%s
        """

        cursor.execute(delete_query, (issue_id,))

        update_query = """
        UPDATE books

        SET available_quantity =
        available_quantity + 1

        WHERE id=%s
        """

        cursor.execute(update_query, (book_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "message":
            "Book Returned Successfully"
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# LEADERBOARD

@app.get("/leaderboard")
def leaderboard():

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT

        users.name,

        COUNT(issued_books.id)
        AS books_count

        FROM users

        LEFT JOIN issued_books
        ON users.id = issued_books.user_id

        GROUP BY users.id

        ORDER BY books_count DESC
        """

        cursor.execute(query)

        leaderboard = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "leaderboard": leaderboard
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# FRONTEND + BACKEND SAME PORT

app.mount(

    "/",

    StaticFiles(
        directory="../frontend",
        html=True
    ),

    name="frontend"

)