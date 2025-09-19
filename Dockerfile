# Use Python version 3.11 as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first for caching
COPY requirements.txt .

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the working directory inside the container
COPY . .

# Expose the port used by Streamlit
EXPOSE 8501

# Default command to run the application when the container starts
CMD ["streamlit", "run", "app.py"]
