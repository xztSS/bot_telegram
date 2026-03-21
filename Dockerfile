# Базовый образ Python
FROM python:3.11-slim

# Устанавливаем зависимости для pyzbar и Pillow
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
COPY qr_bot.py .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запуск бота
CMD ["python", "qr_bot.py"]
