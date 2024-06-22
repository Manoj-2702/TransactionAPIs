# Dockerfile

# Use an official Python runtime as a parent image (multi-stage builds)
FROM python:3.11-slim
# Set the working directory in the builder stage
WORKDIR /app

# Copy just the requirements.txt initially to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local code to the container's workspace
COPY . /app

# Create a non-root user and set ownership of the app directory
RUN useradd --create-home --shell /bin/bash vscode \
    && chown -R vscode:vscode /app

# Switch to the non-root user
USER vscode

# Set environment variables
ARG DATABASE_URL

ENV TERM=xterm-256color
ENV FAST_APP=service:app
ENV HOST 0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=$DATABASE_URL

# Expose the specified port
EXPOSE $PORT

# Command to run the FastAPI application
CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
