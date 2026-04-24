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
        f"👋 <b>Welcome to my pixel world!</b>\n\n"
        f"Рады видеть: {user.mention_html()}\n\n"
        f"ℹ️ <b>О чате:</b>\n"
        f"• Founder: <a href='https://t.me/your_founder'>Link</a>\n"
        f"• Chat rules: <a href='https://t.me/your_rules'>Link</a>"
    )
    msg = await bot.send_message(event.chat.id, text, parse_mode="HTML")
    # Plan deletion after 10 minutes (600 seconds)
    import asyncio

    asyncio.create_task(delete_after_delay(msg, 600))
