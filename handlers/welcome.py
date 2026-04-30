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
        f"┏{ 👿 }.. ⋐(    •︠ ﹏ •︡  )っ🍌\n"
        f"┋\n"
        f"┣ WELCOME TO MY PIXEL WORLD!\n"
        f"┋\n"
        f"┣ CEO: KLASSIKA href='https://t.me/notapes'>\n"
        f"┋\n"
        f"┣ RULES href='https://t.me/notapes_rules'>"
        f"┋\n"
        f"┣ TOOLS href='https://t.me/notapes' \n"
        f"┋\n"
        f"┗┅ [ HUMANS.. NOT APES ]"
    )

    try:
        # Try sending with GIF if we had the ID, otherwise just message
        # Since we don't have the real ID, we send message for now.
        msg = await bot.send_message(event.chat.id, text, parse_mode="HTML")
        asyncio.create_task(delete_after_delay(msg, 600))
    except Exception:
        pass
