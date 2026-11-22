
from app.database import get_connection


def main():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")

            result = cursor.fetchone()

            print("Connected database:", result[0])


if __name__ == "__main__":
    main()
