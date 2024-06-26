from contextlib import contextmanager
import os
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
pool = psycopg2.pool.SimpleConnectionPool(1, 20, DATABASE_URL)


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
        
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                origin_user_id VARCHAR(50) NOT NULL,
                destination_user_id VARCHAR(50) NOT NULL,
                origin_amount NUMERIC NOT NULL,
                origin_currency VARCHAR(3) NOT NULL,
                origin_country VARCHAR(2) NOT NULL,
                destination_amount NUMERIC NOT NULL,
                destination_currency VARCHAR(3) NOT NULL,
                destination_country VARCHAR(2) NOT NULL,
                description TEXT,
                promotion_code_used BOOLEAN,
                reference TEXT,
                origin_device_data JSONB,
                destination_device_data JSONB,
                tags JSONB
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


def insert_transaction(transaction_data: dict) -> int:
    conn = None
    cur = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Transactions (
                type, timestamp, origin_user_id, destination_user_id,
                origin_amount, origin_currency, origin_country,
                destination_amount, destination_currency, destination_country,
                description, promotion_code_used, reference, origin_device_data,
                destination_device_data, tags
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """, (
            transaction_data["type"],
            datetime.fromtimestamp(transaction_data["timestamp"] / 1000),
            transaction_data["originUserId"],
            transaction_data["destinationUserId"],
            transaction_data["originAmountDetails"]["transactionAmount"],
            transaction_data["originAmountDetails"]["transactionCurrency"],
            transaction_data["originAmountDetails"]["country"],
            transaction_data["destinationAmountDetails"]["transactionAmount"],
            transaction_data["destinationAmountDetails"]["transactionCurrency"],
            transaction_data["destinationAmountDetails"]["country"],
            transaction_data.get("description"),
            transaction_data.get("promotionCodeUsed"),
            transaction_data.get("reference"),
            Json(transaction_data.get("originDeviceData")),
            Json(transaction_data.get("destinationDeviceData")),
            Json(transaction_data.get("tags"))
        ))

        transaction_id = cur.fetchone()[0]
        conn.commit()
        return transaction_id

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred while inserting transaction: {e}")
        return None

    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)


def get_transaction_by_id(transaction_id: int) -> dict:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM Transactions WHERE transaction_id = %s
        """, (transaction_id,))

        transaction = cur.fetchone()
        column_names = [desc[0] for desc in cur.description]
        return dict(zip(column_names, transaction)) if transaction else None

    except Exception as e:
        print(f"An error occurred while fetching transaction: {e}")
        return None

    finally:
        if cur:
            cur.close()
        if conn:
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

# Initialize tables
create_tables()
