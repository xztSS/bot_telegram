import logging
import io
from PIL import Image
from pyzbar.pyzbar import decode
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

API_TOKEN = "8500629637:AAGxsJbngLUu8hIi-BYBYThdayzy36Cfan4"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer("Привет! Отправь мне фото с QR или штрихкодом, я расшифрую его.")

# Обработка фото
@dp.message(types.ContentType.PHOTO)
async def handle_photo(message: Message):
    # Берём лучшее качество фото (последний вариант)
    photo = message.photo[-1]
    photo_bytes = await photo.download(destination=io.BytesIO())
    photo_bytes.seek(0)
    img = Image.open(photo_bytes)

    # Декодируем QR и штрихкоды
    decoded_objects = decode(img)

    if not decoded_objects:
        await message.answer("Не удалось распознать QR или штрихкод.")
        return

    response = ""
    for obj in decoded_objects:
        response += f"Тип: {obj.type}\nДанные: {obj.data.decode('utf-8')}\n\n"

    await message.answer(response.strip())

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot, skip_updates=True))
