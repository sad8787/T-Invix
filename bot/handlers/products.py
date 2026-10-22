import io
import logging
import httpx
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import settings

router = Router()
log = logging.getLogger(__name__)

@router.message(Command("create"))
async def create_help(message: Message):
    if message.from_user is None or message.from_user.id not in settings.admin_ids:
        await message.answer("Команда доступна только администратору.")
        return
    await message.answer("Отправьте одним сообщением фотографию и название товара в подписи (caption).")

@router.message(lambda m: bool(m.photo) and bool(m.caption))
async def create_product(message: Message, bot: Bot):
    if message.from_user is None or message.from_user.id not in settings.admin_ids:
        return
    name = " ".join((message.caption or "").split())
    if not name:
        await message.answer("Добавьте название товара в подпись к фотографии.")
        return
    photo = message.photo[-1]
    try:
        file = await bot.get_file(photo.file_id)
        buffer = io.BytesIO()
        await bot.download_file(file.file_path, destination=buffer)
        image_bytes = buffer.getvalue()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.api_url.rstrip('/')}/api/v1/products",
                data={"name": name, "admin_id": str(message.from_user.id)},\n                headers={"X-Internal-Token": settings.internal_api_token},
                files={"image": ("product.jpg", image_bytes, "image/jpeg")},
            )
        if response.status_code == 201:
            product = response.json()
            await message.answer(f"Товар «{product['name']}» добавлен. ID: {product['id']}")
        elif response.status_code == 403:
            await message.answer("Администратор не разрешён на сервере. Проверьте ADMIN_TELEGRAM_IDS.")
        else:
            log.warning("Product API returned %s: %s", response.status_code, response.text[:500])
            await message.answer(f"Не удалось создать товар (HTTP {response.status_code}).")
    except Exception:
        log.exception("Failed to create product")
        await message.answer("Ошибка при сохранении товара. Попробуйте позже.")

@router.message(lambda m: bool(m.photo) and not bool(m.caption))
async def photo_without_caption(message: Message):
    if message.from_user and message.from_user.id in settings.admin_ids:
        await message.answer("У фотографии нет подписи. Отправьте фото и название товара в одном сообщении.")
