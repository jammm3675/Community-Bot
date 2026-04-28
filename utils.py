import asyncio
import re
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

async def safe_edit_text(message: Message, text: str, reply_markup=None, parse_mode="HTML"):
    try:
        return await message.edit_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return message
        # If HTML parsing fails, try sending as plain text
        if "can't parse entities" in str(e):
            return await message.edit_text(text=strip_custom_emojis(text), reply_markup=reply_markup, parse_mode=None)
        raise e

async def safe_answer(callback: CallbackQuery, text: str = None, show_alert: bool = False):
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest:
        pass

def strip_custom_emojis(text: str) -> str:
    """Removes <tg-emoji> tags but keeps the emoji inside if possible,
    or just cleans up the string for safe display."""
    return re.sub(r'<tg-emoji id=".*?">(.*?)</tg-emoji>', r'\1', text)

def get_progress_bar(percent):
    percent = max(0, min(100, percent))
    filled = int(percent / 10)
    return "█" * filled + "░" * (10 - filled)

async def delete_after_delay(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

def calculate_level_stats(xp):
    level = (xp // 1000) + 1
    xp_in_current_level = xp % 1000
    percent = (xp_in_current_level / 1000) * 100
    return level, xp_in_current_level, percent
