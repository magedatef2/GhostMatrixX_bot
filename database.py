import sqlite3

from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection

        connection.commit()

    except Exception:
        connection.rollback()

        raise

    finally:
        connection.close()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    with db() as con:

        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );


            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                dial_code TEXT NOT NULL,
                continent TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_id INTEGER NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                kind TEXT NOT NULL DEFAULT 'temporary',
                status TEXT NOT NULL DEFAULT 'available',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(country_id)
                    REFERENCES countries(id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                number_id INTEGER,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(number_id)
                    REFERENCES numbers(id)
                    ON DELETE SET NULL
            );


            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number_id INTEGER NOT NULL,
                sender TEXT DEFAULT 'demo',
                body TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(number_id)
                    REFERENCES numbers(id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                blocked INTEGER NOT NULL DEFAULT 0
            );


            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                actor_id INTEGER NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        defaults = {
            "maintenance": "0",
            "demo_otp": "1",
            "welcome": "👻 أهلاً بك في GhostNum",
        }

        for key, value in defaults.items():

            con.execute(
                """
                INSERT OR IGNORE INTO settings(key, value)
                VALUES (?, ?)
                """,
                (key, value),
            )


# =========================================================
# SETTINGS
# =========================================================

def get_setting(key, default=""):

    with db() as con:

        row = con.execute(
            """
            SELECT value
            FROM settings
            WHERE key = ?
            """,
            (key,),
        ).fetchone()

        if row:
            return row["value"]

        return default


def set_setting(key, value):

    with db() as con:

        con.execute(
            """
            INSERT INTO settings(key, value)
            VALUES (?, ?)

            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (key, str(value)),
        )


# =========================================================
# COUNTRIES
# =========================================================

def seed_countries(rows):

    with db() as con:

        for name, dial_code, continent in rows:

            con.execute(
                """
                INSERT OR IGNORE INTO countries(
                    name,
                    dial_code,
                    continent
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    dial_code,
                    continent,
                ),
            )


def countries(enabled_only=False, continent=None):

    query = """
        SELECT *
        FROM countries
        WHERE 1 = 1
    """

    args = []

    if enabled_only:

        query += " AND enabled = 1"

    if continent:

        query += " AND continent = ?"

        args.append(continent)

    query += """
        ORDER BY continent ASC, name ASC
    """

    with db() as con:

        return con.execute(
            query,
            args,
        ).fetchall()


def country(country_id):

    with db() as con:

        return con.execute(
            """
            SELECT *
            FROM countries
            WHERE id = ?
            """,
            (country_id,),
        ).fetchone()


def add_country(name, dial_code, continent):

    with db() as con:

        con.execute(
            """
            INSERT INTO countries(
                name,
                dial_code,
                continent
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                dial_code,
                continent,
            ),
        )


def toggle_country(country_id):

    with db() as con:

        con.execute(
            """
            UPDATE countries

            SET enabled =
                CASE
                    WHEN enabled = 1 THEN 0
                    ELSE 1
                END

            WHERE id = ?
            """,
            (country_id,),
        )


def delete_country(country_id):

    with db() as con:

        con.execute(
            """
            DELETE FROM countries
            WHERE id = ?
            """,
            (country_id,),
        )


# =========================================================
# NUMBERS
# =========================================================

def add_number(
    country_id,
    phone,
    kind="temporary",
):

    with db() as con:

        con.execute(
            """
            INSERT INTO numbers(
                country_id,
                phone,
                kind
            )
            VALUES (?, ?, ?)
            """,
            (
                country_id,
                phone,
                kind,
            ),
        )


def number(number_id):

    with db() as con:

        return con.execute(
            """
            SELECT
                n.*,
                c.name AS country_name,
                c.dial_code,
                c.continent

            FROM numbers n

            JOIN countries c
                ON c.id = n.country_id

            WHERE n.id = ?
            """,
            (number_id,),
        ).fetchone()


def numbers(
    country_id=None,
    status=None,
    kind=None,
    limit=100,
):

    query = """
        SELECT
            n.*,
            c.name AS country_name,
            c.dial_code

        FROM numbers n

        JOIN countries c
            ON c.id = n.country_id

        WHERE 1 = 1
    """

    args = []

    if country_id is not None:

        query += " AND n.country_id = ?"

        args.append(country_id)

    if status:

        query += " AND n.status = ?"

        args.append(status)

    if kind:

        query += " AND n.kind = ?"

        args.append(kind)

    query += """
        ORDER BY n.id DESC
        LIMIT ?
    """

    args.append(limit)

    with db() as con:

        return con.execute(
            query,
            args,
        ).fetchall()


def delete_number(number_id):

    with db() as con:

        con.execute(
            """
            DELETE FROM numbers
            WHERE id = ?
            """,
            (number_id,),
        )


def rotate_number(number_id):

    with db() as con:

        row = con.execute(
            """
            SELECT *
            FROM numbers
            WHERE id = ?
            """,
            (number_id,),
        ).fetchone()

        if not row:

            return None

        con.execute(
            """
            UPDATE numbers
            SET status = 'available'
            WHERE id = ?
            """,
            (number_id,),
        )

        return row


# =========================================================
# ORDERS
# =========================================================

def create_order(user_id, number_id):

    with db() as con:

        number_row = con.execute(
            """
            SELECT *
            FROM numbers
            WHERE id = ?
            AND status = 'available'
            """,
            (number_id,),
        ).fetchone()

        if not number_row:

            return None

        con.execute(
            """
            UPDATE numbers

            SET status = 'used'

            WHERE id = ?
            """,
            (number_id,),
        )

        cursor = con.execute(
            """
            INSERT INTO orders(
                user_id,
                number_id,
                status
            )
            VALUES (?, ?, 'active')
            """,
            (
                user_id,
                number_id,
            ),
        )

        return cursor.lastrowid, number_row


def user_orders(user_id):

    with db() as con:

        return con.execute(
            """
            SELECT
                o.*,
                n.phone,
                n.kind,
                c.name AS country_name

            FROM orders o

            LEFT JOIN numbers n
                ON n.id = o.number_id

            LEFT JOIN countries c
                ON c.id = n.country_id

            WHERE o.user_id = ?

            ORDER BY o.id DESC
            """,
            (user_id,),
        ).fetchall()


def all_orders(limit=100):

    with db() as con:

        return con.execute(
            """
            SELECT
                o.*,
                n.phone,
                n.kind,
                c.name AS country_name

            FROM orders o

            LEFT JOIN numbers n
                ON n.id = o.number_id

            LEFT JOIN countries c
                ON c.id = n.country_id

            ORDER BY o.id DESC

            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def close_order(order_id):

    with db() as con:

        row = con.execute(
            """
            SELECT number_id
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        if not row:

            return False

        con.execute(
            """
            UPDATE orders
            SET status = 'closed'
            WHERE id = ?
            """,
            (order_id,),
        )

        if row["number_id"]:

            con.execute(
                """
                UPDATE numbers
                SET status = 'available'
                WHERE id = ?
                """,
                (row["number_id"],),
            )

        return True


# =========================================================
# MESSAGES
# =========================================================

def add_message(
    number_id,
    body,
    sender="demo",
):

    with db() as con:

        con.execute(
            """
            INSERT INTO messages(
                number_id,
                sender,
                body
            )
            VALUES (?, ?, ?)
            """,
            (
                number_id,
                sender,
                body,
            ),
        )


def number_messages(
    number_id,
    limit=30,
):

    with db() as con:

        return con.execute(
            """
            SELECT *
            FROM messages

            WHERE number_id = ?

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                number_id,
                limit,
            ),
        ).fetchall()


# =========================================================
# USERS
# =========================================================

def upsert_user(
    user_id,
    first_name="",
    username="",
):

    with db() as con:

        con.execute(
            """
            INSERT INTO users(
                user_id,
                first_name,
                username
            )

            VALUES (?, ?, ?)

            ON CONFLICT(user_id)

            DO UPDATE SET

                first_name =
                    excluded.first_name,

                username =
                    excluded.username,

                last_seen =
                    CURRENT_TIMESTAMP
            """,
            (
                user_id,
                first_name,
                username,
            ),
        )


def users(limit=100):

    with db() as con:

        return con.execute(
            """
            SELECT *
            FROM users

            ORDER BY last_seen DESC

            LIMIT ?
            """,
            (limit,),
        ).fetchall()


# =========================================================
# STATISTICS
# =========================================================

def stats():

    with db() as con:

        def count(sql):

            return con.execute(sql).fetchone()[0]

        return {

            "users":
                count(
                    "SELECT COUNT(*) FROM users"
                ),

            "countries":
                count(
                    "SELECT COUNT(*) FROM countries"
                ),

            "enabled_countries":
                count(
                    """
                    SELECT COUNT(*)
                    FROM countries
                    WHERE enabled = 1
                    """
                ),

            "numbers":
                count(
                    "SELECT COUNT(*) FROM numbers"
                ),

            "available":
                count(
                    """
                    SELECT COUNT(*)
                    FROM numbers
                    WHERE status = 'available'
                    """
                ),

            "used":
                count(
                    """
                    SELECT COUNT(*)
                    FROM numbers
                    WHERE status = 'used'
                    """
                ),

            "orders":
                count(
                    "SELECT COUNT(*) FROM orders"
                ),

            "active_orders":
                count(
                    """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE status = 'active'
                    """
                ),

            "messages":
                count(
                    "SELECT COUNT(*) FROM messages"
                ),
        }


# =========================================================
# AUDIT LOG
# =========================================================

def audit(
    actor_id,
    action,
    details="",
):

    with db() as con:

        con.execute(
            """
            INSERT INTO audit(
                action,
                actor_id,
                details
            )

            VALUES (?, ?, ?)
            """,
            (
                action,
                actor_id,
                details,
            ),
        )


def audit_logs(limit=100):

    with db() as con:

        return con.execute(
            """
            SELECT *
            FROM audit

            ORDER BY id DESC

            LIMIT ?
            """,
            (limit,),
        ).fetchall()
