from contextlib import contextmanager
import os
import psycopg2
import psycopg2.pool
from psycopg2.extras import Json
from datetime import datetime
from dotenv import load_dotenv
from server.models.transaction import TransactionType, Currency, Country, DeviceData, Tag

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
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
                id SERIAL PRIMARY KEY,
                transaction_id NUMERIC,
                type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                origin_user_id VARCHAR(50) ,
                destination_user_id VARCHAR(50) ,
                origin_amount NUMERIC NOT NULL,
                origin_currency VARCHAR(3) NOT NULL,
                origin_country VARCHAR(2) ,
                destination_amount NUMERIC NOT NULL,
                destination_currency VARCHAR(3) NOT NULL,
                destination_country VARCHAR(2) ,
                promotion_code_used BOOLEAN,
                reference VARCHAR(255),
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


def insert_transaction(transaction_data: dict, transaction_id: str) -> int:
    conn = None
    cur = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Transactions (
                transaction_id, type, timestamp, origin_user_id, destination_user_id,
                origin_amount, origin_currency, origin_country,
                destination_amount, destination_currency, destination_country,
                promotion_code_used, reference, origin_device_data,
                destination_device_data, tags
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """, (
            transaction_id,
            transaction_data["type"],
            transaction_data["timestamp"],  # Use provided timestamp
            transaction_data["originUserId"],
            transaction_data.get("destinationUserId"),
            transaction_data["originAmountDetails"]["transactionAmount"],
            transaction_data["originAmountDetails"]["transactionCurrency"],
            transaction_data["originAmountDetails"]["country"],
            transaction_data["destinationAmountDetails"]["transactionAmount"],
            transaction_data["destinationAmountDetails"]["transactionCurrency"],
            transaction_data["destinationAmountDetails"]["country"],
            transaction_data.get("promotionCodeUsed", False),
            transaction_data.get("reference", ""),
            Json(transaction_data.get("originDeviceData", {})),
            Json(transaction_data.get("destinationDeviceData", {})),
            Json(transaction_data.get("tags", []))
        ))
        
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
        if transaction is None:
            return None

        column_names = [desc[0] for desc in cur.description]
        transaction_dict = dict(zip(column_names, transaction))

        # Ensure all expected keys are present and set default values if missing
        transaction_dict["executedRules"] = transaction_dict.get("executed_rules", [])
        transaction_dict["hitRules"] = transaction_dict.get("hit_rules", [])
        transaction_dict["riskScoreDetails"] = transaction_dict.get("risk_score_details", {
            "trsScore": 0.0,
            "trsRiskLevel": "LOW"
        })
        transaction_dict["status"] = transaction_dict.get("status", "Completed")
        transaction_dict["transactionId"] = str(transaction_dict["transaction_id"])
        transaction_dict["message"] = transaction_dict.get("message", "Transaction retrieved successfully")

        # Convert to appropriate enums and nested structures
        transaction_dict["type"] = TransactionType(transaction_dict["type"])
        transaction_dict["originAmountDetails"] = {
            "transactionAmount": transaction_dict["origin_amount"],
            "transactionCurrency": Currency(transaction_dict["origin_currency"]),
            "country": Country(transaction_dict["origin_country"]),
        }
        transaction_dict["destinationAmountDetails"] = {
            "transactionAmount": transaction_dict["destination_amount"],
            "transactionCurrency": Currency(transaction_dict["destination_currency"]),
            "country": Country(transaction_dict["destination_country"]),
        }
        transaction_dict["originDeviceData"] = transaction_dict.get("origin_device_data", DeviceData())
        transaction_dict["destinationDeviceData"] = transaction_dict.get("destination_device_data", DeviceData())
        transaction_dict["tags"] = transaction_dict.get("tags", [Tag().dict()])

        return transaction_dict

    except Exception as e:
        print(f"An error occurred while fetching transaction: {e}")
        return None

    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)



def get_transactions(transaction_id):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
            row = cur.fetchone()
            if row:
                return {
                    "transaction_id": row[0],
                    "type": row[1],
                    "timestamp": row[2],
                    "origin_user_id": row[3],
                    "destination_user_id": row[4],
                    "origin_amount": row[5],
                    "origin_currency": row[6],
                    "origin_country": row[7],
                    "destination_amount": row[8],
                    "destination_currency": row[9],
                    "destination_country": row[10],
                    "is_fraudulent": row[11],
                    "metadata": row[12],
                    "origin_device_data": row[13],
                    "destination_device_data": row[14],
                    "tags": row[15],
                }
    finally:
        pool.putconn(conn)
    return None



def search_transactions_by_amount(amount: float) -> list:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        query = """
            SELECT * FROM Transactions WHERE origin_amount = %s
        """
        params = [amount]

        cur.execute(query, tuple(params))
        transactions = cur.fetchall()

        return transactions

    except Exception as e:
        print(f"An error occurred while searching for transactions: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)

def search_transactions_by_date_range(start_date: datetime, end_date: datetime) -> list:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        query = """
            SELECT * FROM Transactions WHERE timestamp >= %s AND timestamp <= %s
        """
        params = [start_date, end_date]

        cur.execute(query, tuple(params))
        transactions = cur.fetchall()

        return transactions

    except Exception as e:
        print(f"An error occurred while searching for transactions: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)

def search_transactions_by_type(type: str) -> list:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        query = """
            SELECT * FROM Transactions WHERE type = %s
        """
        params = [type]

        cur.execute(query, tuple(params))
        transactions = cur.fetchall()

        return transactions

    except Exception as e:
        print(f"An error occurred while searching for transactions: {e}")
        return []
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


def get_transaction_summary(start_date: datetime, end_date: datetime) -> dict:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        query = """
            SELECT type, COUNT(*) AS count, SUM(origin_amount) AS total_amount
            FROM Transactions
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY type
        """
        params = [start_date, end_date]

        cur.execute(query, tuple(params))
        result = cur.fetchall()

        summary = [{"type": row[0], "count": row[1], "total_amount": row[2]} for row in result]

        return summary

    except Exception as e:
        print(f"An error occurred while fetching transaction summary: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)

def get_total_transaction_amount(start_date: datetime, end_date: datetime) -> float:
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        query = """
            SELECT SUM(origin_amount)
            FROM Transactions
            WHERE timestamp >= %s AND timestamp <= %s
        """
        params = [start_date, end_date]

        cur.execute(query, tuple(params))
        result = cur.fetchone()

        total_amount = result[0] if result[0] is not None else 0.0

        return total_amount

    except Exception as e:
        print(f"An error occurred while fetching total transaction amount: {e}")
        return 0.0
    finally:
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)




# Initialize tables
create_tables()
