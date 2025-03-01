# Use official Python image as base
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask application's port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py", "http://*:5000"]
