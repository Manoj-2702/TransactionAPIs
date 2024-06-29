# Use the official Python image from the DockerHub
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Start FastAPI and Streamlit using a script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Define the command to run the start script
CMD ["/start.sh"]
