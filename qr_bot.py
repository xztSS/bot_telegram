import os
import requests
import tempfile
from pyzxing import BarCodeReader
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

reader = BarCodeReader()

@dp.message_handler(content_types=['photo'])
async def scan_barcode(message: types.Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'
    
    # Сохраняем временно
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(response.content)
        tmp_filename = tmp_file.name

    try:
        result = reader.decode(tmp_filename)
        if result:
            await message.reply(f"Распознано:\n{result}")
        else:
            await message.reply("QR/штрихкод не найден")
    finally:
        os.remove(tmp_filename)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
