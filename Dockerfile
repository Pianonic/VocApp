# Use the official Python image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY src/ /app/src/
COPY wsgi.py /app/wsgi.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:application"]
