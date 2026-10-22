import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from bot.config import settings
from bot.handlers import start, products

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
dp.include_routers(start.router, products.router)

async def run_polling():
    # Development-only fallback. Run exactly one replica in polling mode.
    async with Bot(settings.bot_token) as bot:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)

async def run_webhook():
    bot = Bot(settings.bot_token)
    if not settings.webhook_public_url:
        raise RuntimeError("WEBHOOK_PUBLIC_URL must be set in webhook mode (public HTTPS URL)")
    await bot.set_webhook(
        url=settings.webhook_public_url.rstrip("/") + settings.webhook_path,
        secret_token=settings.webhook_secret,
        allowed_updates=dp.resolve_used_update_types(),
    )
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.webhook_secret
    ).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)
    app.router.add_get("/health/live", lambda request: web.json_response({"status": "ok"}))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)
    await site.start()
    logging.info("Webhook server listening on %s:%s", settings.webhook_host, settings.webhook_port)
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    if settings.bot_mode.lower() == "polling":
        asyncio.run(run_polling())
    else:
        asyncio.run(run_webhook())
