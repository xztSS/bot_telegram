import os
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import ContentType

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Клавиатура ---
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить фото")],
    ],
    resize_keyboard=True
)

# --- Старт команды ---
@dp.message()
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Отправь мне фото с QR-кодом, и я расшифрую его.",
        reply_markup=keyboard
    )

# --- Обработка фото ---
@dp.message(ContentType.PHOTO)
async def handle_photo(message: Message):
    # Берем последнее фото (самое крупное)
    photo = message.photo[-1]
    file = await bot.download(photo.file_id)
    
    image = Image.open(BytesIO(file.read()))
    qr_codes = decode(image)

    if qr_codes:
        result = "\n".join([qr.data.decode() for qr in qr_codes])
    else:
        result = "QR-код не найден."

    await message.answer(result, reply_markup=ReplyKeyboardRemove())

# --- Основной запуск ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
