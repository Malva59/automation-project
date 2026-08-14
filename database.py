import sqlite3

DATABASE = "codes.db"


def init_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def is_code_known(code):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT 1 FROM codes WHERE code = ?",
        (code,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def save_code(code):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO codes (code) VALUES (?)",
        (code,)
    )

    connection.commit()
    connection.close()


def get_new_codes(codes):
    new_codes = []

    for code in codes:
        if not is_code_known(code):
            new_codes.append(code)

    return new_codes
