import io
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from pyzbar.pyzbar import decode
from PIL import Image

API_TOKEN = "8500629637:AAGxsJbngLUu8hIi-BYBYThdayzy36Cfan4"

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне фото с QR или штрихкодом, и я расшифрую его.")

# Обработчик фото
@dp.message(F.photo)
async def handle_photo(message: Message):
    # Берём фото с наибольшим разрешением
    photo = message.photo[-1]
    
    # Загружаем в память
    photo_bytes = io.BytesIO()
    await photo.download(destination_file=photo_bytes)
    photo_bytes.seek(0)

    # Открываем и конвертируем в RGB
    image = Image.open(photo_bytes).convert("RGB")

    # Декодируем QR/штрихкоды
    codes = decode(image)
    logging.info(f"Найденные коды: {codes}")

    # Формируем ответ
    if codes:
        response = "\n".join([f"Тип: {c.type}, Данные: {c.data.decode('utf-8')}" for c in codes])
    else:
        response = "Коды не найдены."

    await message.answer(response)

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
