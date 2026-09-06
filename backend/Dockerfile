FROM python:3.11-slim
WORKDIR /app
# Instalamos las librerías necesarias
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
COPY . .
# Iniciamos el backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]