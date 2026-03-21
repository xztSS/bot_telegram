FROM python:3.11-slim

# Устанавливаем zbar для pyzbar
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    zbar-tools \
    libzbar0 \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем проект
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Запуск бота
CMD ["python", "qr_bot.py"]
