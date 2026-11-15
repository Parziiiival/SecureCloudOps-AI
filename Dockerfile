FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip

# 2. Prevent Python from writing .pyc files and enable real-time terminal logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy and install dependencies first (caches this layer for faster rebuilds)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y setuptools wheel && \
    rm -rf /usr/local/lib/python3.11/ensurepip/_bundled/setuptools*

# 5. Copy your Django project files into the container
COPY . /app/

# 6. Document that the container listens on port 8000
EXPOSE 8000

# 7. Start the Django server listening on all container network interfaces
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]