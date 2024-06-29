import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add the src directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

@pytest.fixture(scope='session', autouse=True)
def mock_db():
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_conn = MagicMock()
        mock_pool.return_value.getconn.return_value = mock_conn
        mock_pool.return_value.putconn.return_value = None
        mock_conn.cursor.return_value = MagicMock()
        yield mock_pool


load_dotenv()

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client

@pytest.fixture(scope="module", autouse=True)
def set_up():
    os.environ["API_KEY"] = "zamnnn"
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:fO0wLPoB9GUS@ep-proud-art-a1ywobap-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
