from database import get_db_connection


# CHECK USER LOGIN
def authenticate_user(email, password):

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user

    except Exception as e:

        return {
            "error": str(e)
        }


# CHECK ADMIN
def is_admin(user):

    if user["role"] == "admin":
        return True

    return False