import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ContentType
from aiogram.types import Message
from pyzbar.pyzbar import decode
from PIL import Image
import os

API_TOKEN = "8500629637:AAGxsJbngLUu8hIi-BYBYThdayzy36Cfan4"

# Создаем папку для загруженных фото
os.makedirs("downloads", exist_ok=True)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def decode_qr_barcode(file_path: str) -> str:
    """Декодирует QR и штрихкоды из изображения"""
    try:
        image = Image.open(file_path)
        codes = decode(image)
        if not codes:
            return "Код не найден."
        return "\n".join([f"{code.type}: {code.data.decode('utf-8')}" for code in codes])
    except Exception as e:
        return f"Ошибка при декодировании: {e}"

@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photo(message: Message):
    photo = message.photo[-1]  # берём наибольшее по размеру
    file_info = await bot.get_file(photo.file_id)
    file_path = f"downloads/{photo.file_id}.jpg"
    await photo.download(destination=file_path)
    
    result = await decode_qr_barcode(file_path)
    await message.reply(result)

@dp.message_handler(commands=["start"])
async def start_cmd(message: Message):
    await message.reply("Привет! Отправь мне фото с QR или штрихкодом, и я расшифрую его.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
