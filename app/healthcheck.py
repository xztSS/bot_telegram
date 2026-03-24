from __future__ import annotations

from aiohttp import web


async def healthcheck(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def start_healthcheck_server(host: str, port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner
