# --- Используем официальный Python ---
FROM python:3.11-slim

# --- Обновление и установка зависимостей для pyzbar ---
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# --- Создаем рабочую директорию ---
WORKDIR /app

# --- Копируем файлы ---
COPY requirements.txt .
COPY qr_bot.py .

# --- Установка зависимостей ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Запуск бота ---
CMD ["python", "qr_bot.py"]
