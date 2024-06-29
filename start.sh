#!/bin/bash

# Start the FastAPI server
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload &

# Start the Streamlit server
streamlit run src/streamlit_app.py
