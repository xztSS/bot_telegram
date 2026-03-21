import os
import tempfile
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pyzbar.pyzbar import decode
from PIL import Image

# Получаем токен из переменной окружения
API_TOKEN = os.environ.get("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=['photo', 'document'])
async def handle_file(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.reply("Пожалуйста, отправьте QR или штрихкод как фото или файл.")
        return

    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
    response = requests.get(file_url)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(response.content)
        tmp_filename = tmp_file.name

    try:
        img = Image.open(tmp_filename)
        decoded_objects = decode(img)

        if decoded_objects:
            results = []
            for obj in decoded_objects:
                type_name = obj.type  # QR_CODE, EAN13, CODE128 и т.д.
                data = obj.data.decode("utf-8")
                results.append(f"{type_name}: {data}")
            await message.reply("Найдено:\n" + "\n".join(results))
        else:
            await message.reply("QR или штрихкод не найден 😕")
    finally:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
