import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardRemove
from aiogram import F

from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode

API_TOKEN = "ВАШ_ТОКЕН_БОТА"

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def extract_qr_from_photo(photo_bytes: bytes) -> str:
    """Декодирует QR-код из изображения"""
    image = Image.open(BytesIO(photo_bytes))
    qr_codes = decode(image)
    if qr_codes:
        return qr_codes[0].data.decode("utf-8")
    return None

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Пришли фото с QR-кодом, и я его расшифрую.")

# Обработка фото
@dp.message(content_types=ContentType.PHOTO)
async def photo_handler(message: types.Message):
    # Получаем наибольшее изображение
    photo = message.photo[-1]
    photo_bytes = await photo.download(destination=BytesIO())
    photo_bytes.seek(0)
    
    qr_text = await extract_qr_from_photo(photo_bytes.read())
    
    if qr_text:
        await message.answer(f"QR-код расшифрован: {qr_text}")
    else:
        await message.answer("Не удалось найти QR-код на изображении.")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import Dispatcher
    
    async def main():
        try:
            logging.info("Бот запущен...")
            await dp.start_polling(bot)
        finally:
            await bot.session.close()

    asyncio.run(main())
