import pytest
from src.server.database import get_transactions, get_total_transaction_amount
import threading
import time

def test_get_transactions():
    transaction_id = 123456
    transaction = get_transactions(transaction_id)
    assert transaction is not None
    assert transaction["transaction_id"] == transaction_id

def test_get_total_transaction_amount():
    start_date = "2023-01-01T00:00:00Z"
    end_date = "2023-12-31T23:59:59Z"
    total_amount = get_total_transaction_amount(start_date, end_date)
    assert isinstance(total_amount, float)

def test_generate_transaction():
    from src.server.routes.transaction import generate_transaction, cron_running, cron_thread
    cron_running = True
    cron_thread = threading.Thread(target=generate_transaction)
    cron_thread.start()
    time.sleep(2)
    cron_running = False
    cron_thread.join()
    transaction_id = 123456
    transaction = get_transactions(transaction_id)
    assert transaction is not None
    assert transaction["transaction_id"] == transaction_id
