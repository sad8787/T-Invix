from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from bot.config import settings

router = Router()

def catalog_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть каталог", web_app=WebAppInfo(url=settings.mini_app_url))
    ]])

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("У меня есть товар", reply_markup=catalog_keyboard())