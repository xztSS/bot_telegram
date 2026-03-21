import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from pyzbar.pyzbar import decode
from PIL import Image

API_TOKEN = "ВАШ_API_ТОКЕН"  # замените на токен вашего бота

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer("Привет! Отправь фото с QR-кодом или штрихкодом.")

# Обработчик фото
@dp.message(F.photo)
async def handle_photo(message: Message):
    # Берем лучшее качество фото
    photo = message.photo[-1]
    # Скачиваем фото в память
    photo_bytes = await photo.download(destination=io.BytesIO())
    photo_bytes.seek(0)
    image = Image.open(photo_bytes)

    # Декодируем QR/штрихкод
    codes = decode(image)
    if codes:
        response = "\n".join([f"Тип: {c.type}, Данные: {c.data.decode()}" for c in codes])
    else:
        response = "Коды не найдены."

    await message.answer(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
