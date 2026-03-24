from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher

from app.config import Settings
from app.decoder import BarcodeDecoder
from app.handlers import build_router
from app.healthcheck import start_healthcheck_server


async def main() -> None:
    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(token=settings.api_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router(BarcodeDecoder()))

    healthcheck_runner = None
    if settings.enable_healthcheck:
        healthcheck_runner = await start_healthcheck_server(settings.host, settings.port)
        logging.getLogger(__name__).info(
            "Healthcheck server started on %s:%s",
            settings.host,
            settings.port,
        )

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        if healthcheck_runner is not None:
            await healthcheck_runner.cleanup()


if __name__ == "__main__":
    import asyncio as _asyncio

    _asyncio.run(main())
