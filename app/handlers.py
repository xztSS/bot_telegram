from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.decoder import BarcodeDecoder, DecoderUnavailableError, InvalidImageError


def build_router(decoder: BarcodeDecoder) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        await message.answer(
            "Привет! Отправьте фото или файл с QR-кодом/штрихкодом, и я постараюсь его расшифровать.",
        )

    @router.message(F.photo)
    async def handle_photo(message: Message, bot: Bot) -> None:
        photo = message.photo[-1]
        file = await bot.download(photo)
        await process_payload(message, decoder, file.read())

    @router.message(F.document)
    async def handle_document(message: Message, bot: Bot) -> None:
        document = message.document
        if document.content_type and not document.content_type.startswith("image/"):
            await message.answer("Пожалуйста, отправьте изображение: JPG, PNG, WEBP или другой image/* файл.")
            return

        file = await bot.download(document)
        await process_payload(message, decoder, file.read())

    @router.message()
    async def handle_other_messages(message: Message) -> None:
        if message.content_type in {ContentType.TEXT, ContentType.STICKER, ContentType.VOICE, ContentType.VIDEO}:
            await message.answer(
                "Я умею распознавать QR-коды и штрихкоды с изображений. Пришлите фото или файл с кодом.",
            )
            return

        await message.answer("Этот тип сообщения пока не поддерживается. Пришлите изображение с кодом.")

    return router


async def process_payload(message: Message, decoder: BarcodeDecoder, payload: bytes) -> None:
    try:
        results = decoder.decode_bytes(payload)
    except InvalidImageError:
        await message.answer("Не удалось открыть изображение. Попробуйте отправить файл в другом формате.")
        return
    except DecoderUnavailableError:
        await message.answer(
            "Сервис распознавания временно недоступен: на сервере отсутствует библиотека zbar. Проверьте конфигурацию Railway/Docker.",
        )
        return

    if not results:
        await message.answer("Не удалось найти QR-код или штрихкод. Попробуйте более чёткое изображение без бликов.")
        return

    response_lines = ["Найденные коды:"]
    response_lines.extend(
        f"{index}. {result.symbol_type}: {result.data}"
        for index, result in enumerate(results, start=1)
    )
    await message.answer("\n".join(response_lines))
