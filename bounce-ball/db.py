import logging
import os
import sqlite3


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)


def create_connection():
    if not os.getenv("DB_FILE_PATH"):
        raise Exception("Env DB_FILE_PATH not defined!")

    connection = None
    try:
        db_file = os.getenv("DB_FILE_PATH")
        connection = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        logger.error(f"The error '{e}' occurred")
        raise e

    return connection


def execute_query(connection, query, values=None):
    cursor = connection.cursor()
    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"The error '{e}' occurred")
        raise e


def execute_read_query(connection, query, values=None):
    cursor = connection.cursor()
    result = None
    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        logger.error(f"The error '{e}' occurred")
        raise e


def update(connection, run_id, fs, value_dic):
    sql = "UPDATE records SET "
    sql += ", ".join([f"{f} = ?" for f in fs])
    sql += " WHERE username = ?"
    values = tuple([value_dic[f] for f in fs])
    values += (run_id,)
    execute_query(connection, sql, values)


def insert(connection, value_dic):
    sql = f"INSERT INTO runs ({', '.join(value_dic.keys())}) "
    sql += f"VALUES ({', '.join(['?'] * len(value_dic.keys()))})"
    values = tuple([value_dic[k] for k in value_dic.keys()])
    execute_query(connection, sql, values)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    conn = create_connection()
    create_runs_table = """
CREATE TABLE IF NOT EXISTS records(
  username TEXT NOT NULL PRIMARY KEY,
  highest_score INTEGER,
  last_update_time_utc DATETIME NULL
);
"""
    execute_query(conn, create_runs_table)

    conn.close()
    logger.info("Database setup done successfully!")
