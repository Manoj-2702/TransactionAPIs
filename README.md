# FlagrightTask
 
# Transaction Management System

## Overview

The Transaction Management System is a comprehensive platform designed to handle various financial transactions efficiently. It comprises a FastAPI backend for handling API requests, a Streamlit frontend for user interaction, and a PostgreSQL database for data storage. The system supports creating, retrieving, and searching transactions, as well as generating transaction reports.

## Features

- **FastAPI Backend**: Provides a robust API for transaction management.
- **Streamlit Frontend**: Offers a user-friendly interface for interacting with the system.
- **PostgreSQL Database**: Ensures reliable data storage and retrieval.
- **CRON Job**: Automated transaction generation for testing purposes.
- **Authentication**: Secure API endpoints with API keys.

## Project Structure

- **app.py**: Main FastAPI application file.
- **streamlit_app.py**: Streamlit application for the frontend interface.
- **transaction.py**: Contains API routes for transaction-related operations.
- **database.py**: Handles database connections and operations.
- **Dockerfile**: Docker configuration for containerizing the application.
- **docker-compose.yml**: Docker Compose configuration for setting up the entire stack.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+
- PostgreSQL

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Manoj-2702/TransactionAPIs
   cd TransactionAPIs
   ```

2. **Set up environment variables:**
    Create a .env file in the root directory and add the following variables:
    ```bash
    DATABASE_URL=your_database_url
    API_KEY=your_api_key
    ```

3. **Build and run the application using Docker Compose:**

```bash
docker-compose up --build
```


4. **Access the Streamlit frontend:**
 - Open your browser and go to `http://localhost:8501.`

5. **Access the FastAPI documentation:**
- Open your browser and go to `http://localhost:8000/docs.`


### API ENDPOINTS

#### Transactions
- Create a Transaction
```http
POST /create_transactions
```
<b>Request Body:</b>

```json
{
  "amount": 100.0,
  "sender_id": "user_123",
  "destination_id": "user_456",
  "type": "TRANSFER",
  "currency": "USD",
  "country": "US"
}
```

- Retrieve a Transaction

```http
GET /get_transactions/{transaction_id}
```


- Search Transactions by Amount

```http
GET /search_transaction_by_amount
```

<b>Query Parameters:</b>

- `amount`: The amount to search for.

- Search Transactions by Date Range

```http
GET /search_transaction_by_date_range
```

<b>Query Parameters:</b>

- `start_date`: The start date of the range.
- `end_date`: The end date of the range.


- Search Transactions by Type

```http
GET /search_transaction_by_type
```
<b>Query Parameters:</b>
- `type`: The type of transactions to search for.

#### CRON Job

#### REPORTS



### Usage
<h1>Streamlit Frontend</h1>
- <b>Transaction Dashboard</b>: View and manage transactions.
- <b>Create a New Transaction</b>: Fill out the form and submit to create a transaction.
- <b>Control CRON Job</b>: Start or stop the automated transaction generation.
- <b>Generate Reports</b>: Generate and download transaction reports.

<h1>FastAPI Backend</h1>
- The backend provides a comprehensive API for managing transactions, handling errors, and generating reports.

<h1>Database</h1>
- 
The PostgreSQL database is used to store all transaction data. It includes tables for transactions and keys for authentication.