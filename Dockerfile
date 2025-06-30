# 1. Use official Python base image
FROM python:3.12-slim

# 2. Set working directory inside the container
WORKDIR /code

# 3. Copy only requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the entire project into the container
COPY . .

# 5. Default command (will be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]