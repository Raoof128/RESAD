FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Modbus and Web ports
EXPOSE 5020 8000

# Default command (overridden in docker-compose)
CMD ["python", "simulation/modbus_server.py"]
