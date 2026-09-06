FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    python-jose[cryptography] \
    "passlib[bcrypt]" \
    bcrypt==4.0.1 \
    python-multipart

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]