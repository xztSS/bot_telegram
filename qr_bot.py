import asyncio
import logging
import os
from io import BytesIO
from typing import TYPE_CHECKING, Any, Iterable

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from aiohttp import web
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
try:
    from pyzbar.pyzbar import ZBarSymbol, decode
except ImportError:  # pragma: no cover - depends on system libzbar
    ZBarSymbol = Any  # type: ignore[assignment]
    decode = None

if TYPE_CHECKING:
    from pyzbar.pyzbar import Decoded
else:
    Decoded = Any

API_TOKEN = os.getenv("API_TOKEN")
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger(__name__)

router = Router()
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить изображение с кодом")]],
    resize_keyboard=True,
    input_field_placeholder="Пришлите фото или файл с QR/штрихкодом",
)

if decode is not None:
    SUPPORTED_SYMBOLS: list[ZBarSymbol] = [
        ZBarSymbol.QRCODE,
        ZBarSymbol.EAN13,
        ZBarSymbol.EAN8,
        ZBarSymbol.CODE128,
        ZBarSymbol.CODE39,
        ZBarSymbol.PDF417,
        ZBarSymbol.DATABAR,
        ZBarSymbol.DATABAR_EXP,
        ZBarSymbol.UPCA,
        ZBarSymbol.UPCE,
        ZBarSymbol.I25,
        ZBarSymbol.CODABAR,
    ]
else:
    SUPPORTED_SYMBOLS = []


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Отправьте фото или файл с QR-кодом/штрихкодом, и я постараюсь его расшифровать.",
        reply_markup=keyboard,
    )


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot) -> None:
    photo = message.photo[-1]
    file = await bot.download(photo)
    await process_image_message(message, file.read(), source_name="photo")


@router.message(F.document)
async def handle_document(message: Message, bot: Bot) -> None:
    document = message.document
    if document.content_type and not document.content_type.startswith("image/"):
        await message.answer("Пожалуйста, отправьте изображение: JPG, PNG, WEBP или другой image/* файл.")
        return

    file = await bot.download(document)
    await process_image_message(message, file.read(), source_name=document.file_name or "document")


@router.message()
async def handle_other_messages(message: Message) -> None:
    if message.content_type in {ContentType.TEXT, ContentType.STICKER, ContentType.VOICE, ContentType.VIDEO}:
        await message.answer(
            "Я умею распознавать QR-коды и штрихкоды с изображений. Пришлите фото или файл с кодом.",
            reply_markup=keyboard,
        )
        return

    await message.answer("Этот тип сообщения пока не поддерживается. Пришлите изображение с кодом.")


async def process_image_message(message: Message, payload: bytes, source_name: str) -> None:
    try:
        image = Image.open(BytesIO(payload))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        logger.warning("Failed to read image %s: %s", source_name, exc)
        await message.answer("Не удалось открыть изображение. Попробуйте отправить файл в другом формате.")
        return

    codes = decode_image(image)
    if not codes:
        if decode is None:
            await message.answer(
                "Сервис распознавания временно недоступен: на сервере отсутствует библиотека zbar. Проверьте конфигурацию Railway/Docker.",
            )
            return

        await message.answer(
            "Не удалось найти QR-код или штрихкод. Попробуйте более чёткое изображение без бликов.",
        )
        return

    response_lines = ["Найденные коды:"]
    for index, code in enumerate(codes, start=1):
        data = safe_decode(code.data)
        response_lines.append(f"{index}. {code.type}: {data}")

    await message.answer("\n".join(response_lines))



def decode_image(image: Image.Image) -> list[Decoded]:
    if decode is None:
        logger.error("libzbar is not available; barcode decoding is disabled")
        return []

    variants = build_image_variants(image)
    unique_codes: dict[tuple[str, bytes], Decoded] = {}

    for variant in variants:
        try:
            decoded = decode(variant, symbols=SUPPORTED_SYMBOLS)
        except Exception as exc:  # pragma: no cover - zbar runtime issue protection
            logger.exception("Barcode decoding failed: %s", exc)
            continue

        for item in decoded:
            unique_codes[(item.type, item.data)] = item

    return list(unique_codes.values())



def build_image_variants(image: Image.Image) -> Iterable[Image.Image]:
    prepared = ImageOps.exif_transpose(image).convert("RGB")
    grayscale = ImageOps.grayscale(prepared)
    high_contrast = ImageOps.autocontrast(grayscale)
    sharpened = ImageEnhance.Sharpness(high_contrast).enhance(2.0)
    threshold = sharpened.point(lambda px: 255 if px > 140 else 0)

    variants = [prepared, grayscale, high_contrast, sharpened, threshold]
    rotated_variants = []
    for variant in variants:
        rotated_variants.append(variant)
        rotated_variants.append(variant.rotate(90, expand=True))
        rotated_variants.append(variant.rotate(180, expand=True))
        rotated_variants.append(variant.rotate(270, expand=True))

    return rotated_variants



def safe_decode(value: bytes) -> str:
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
    return value.decode("utf-8", errors="replace")


async def healthcheck(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def start_healthcheck_server() -> tuple[web.AppRunner, web.BaseSite]:
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=HOST, port=PORT)
    await site.start()
    logger.info("Healthcheck server started on %s:%s", HOST, PORT)
    return runner, site


async def main() -> None:
    if not API_TOKEN:
        raise RuntimeError("Environment variable API_TOKEN is required")

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    runner, _ = await start_healthcheck_server()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
