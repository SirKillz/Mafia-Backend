# Python Base Image
FROM python:3.12

# Set the working directory
WORKDIR /app

# COPY the src folder into the container
COPY src/mafia_backend /app/mafia_backend/

# COPY the Requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "mafia_backend.__main__:app", "--host", "0.0.0.0", "--port", "8000"]