from contextlib import contextmanager
import os
import json
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
pool = psycopg2.pool.SimpleConnectionPool(1, 20,DATABASE_URL)

@contextmanager
def get_db():
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            conn.cursor().close()
            pool.putconn(conn)