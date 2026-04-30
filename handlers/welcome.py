import asyncio
import os
from aiogram import Router, Bot, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_NOT_MEMBER,
    IS_MEMBER,
)
from utils import delete_after_delay

router = Router()

@router.chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER)
)
async def welcome_new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user

    text = (
        f"👋 <b>Welcome to NOTAPES World!</b>\n\n"
        f"<blockquote>"
        f"Glad to see you, {user.mention_html()}! <tg-emoji id='5368324170671202286'>✨</tg-emoji>\n\n"
        f"ℹ️ <b>Information:</b>\n"
        f"• Founder: <a href='https://t.me/notapes'>NOTAPES</a>\n"
        f"• Chat rules: <a href='https://t.me/notapes_rules'>Read Rules</a>"
        f"</blockquote>"
    )

    try:
        # Try sending with GIF if we had the ID, otherwise just message
        # Since we don't have the real ID, we send message for now.
        msg = await bot.send_message(event.chat.id, text, parse_mode="HTML")
        asyncio.create_task(delete_after_delay(msg, 600))
    except Exception:
        pass
