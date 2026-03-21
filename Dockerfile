# Используем официальный Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем системные зависимости для pyzbar и Pillow
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements, если есть
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запуск бота
CMD ["python", "qr_bot.py"]
