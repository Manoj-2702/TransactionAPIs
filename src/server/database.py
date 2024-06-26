from contextlib import contextmanager
import os
import json
import psycopg2
import psycopg2.pool
from dotenv import load_dotenv
from psycopg2.extras import Json
from datetime import datetime, timedelta
from typing import Optional

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

def create_tables():
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Keys (
                key VARCHAR(255)
            );
        """)
        
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cur.close()
            pool.putconn(conn)
            
            
            
def verify_key(key: str):
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT key FROM Keys WHERE key = %s", (key,))
        key_exists = cur.fetchone() is not None
        return key_exists
    except Exception as e:
        print(f"An error occurred while verifying key: {e}")
        return False
    finally:
        if conn:
            cur.close()
            pool.putconn(conn)
            