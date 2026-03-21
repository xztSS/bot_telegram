import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.filters import Command
from pyzbar.pyzbar import decode
from PIL import Image
import io

# Получаем токен из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("API_TOKEN не задан! Установи переменную окружения.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Пришли мне фото с QR или штрихкодом, я его прочитаю.")

# Обработка фото
@dp.message(types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # Берём фото с наибольшим разрешением
    file = await bot.download(photo.file_id)
    img = Image.open(file)
    codes = decode(img)

    if not codes:
        await message.answer("Код не найден. Попробуй другое фото.")
        return

    result_text = "\n".join([f"{c.type}: {c.data.decode('utf-8')}" for c in codes])
    await message.answer(f"Распознано:\n{result_text}")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import F
    from aiogram.utils import executor

    asyncio.run(dp.start_polling(bot))
