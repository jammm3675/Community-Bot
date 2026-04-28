import logging
from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from loader import db
from utils import calculate_level_stats

router = Router()

@router.message(F.text, F.chat.type.in_({"group", "supergroup"}))
async def handle_message_xp(message: Message, bot: Bot):
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await db.create_user(
            user_id, message.from_user.first_name, message.from_user.username
        )
        user = await db.get_user(user_id)

    # Add XP
    result = await db.add_xp(user_id, 10)
    if result:
        xp_added, new_level = result
        # Принудительное обновление тега (Custom Title) при каждом сообщении
        # Теги: 1-5 лвл: Новичок 👶, 5-20: Ветеран 🎖, 20+: VIP ⚡️
        await update_user_tag(bot, message.chat.id, user_id, new_level)

async def update_user_tag(bot: Bot, chat_id: int, user_id: int, level: int):
    # Прямое вшивание текста тегов
    tag = "Новичок 👶" if level < 5 else "Ветеран 🎖" if level < 20 else "VIP ⚡️"
    try:
        await bot.set_chat_member_custom_title(chat_id, user_id, tag)
    except Exception as e:
        # Логируем, но не падаем
        logging.error(f"[SYNC] Failed to update tag for {user_id} in {chat_id}: {e}")

@router.message(Command("thanks"))
async def handle_thanks(message: Message):
    if not message.reply_to_message:
        await message.reply("☝️ Reply to a message to give reputation!")
        return

    from_user_id = message.from_user.id
    to_user_id = message.reply_to_message.from_user.id

    if from_user_id == to_user_id:
        await message.reply("🚫 You cannot give rep to yourself!")
        return

    success, msg = await db.give_rep(from_user_id, to_user_id)
    if success:
        text = (
            f"⭐ <b>Reputation Increased!</b>\n\n"
            f"<blockquote>"
            f"You gave +1 REP to {message.reply_to_message.from_user.first_name}!\n"
            f"Keep being helpful! <tg-emoji id='5368324170671202286'>🤝</tg-emoji>"
            f"</blockquote>"
        )
        await message.reply(text)
    else:
        await message.reply(f"❌ {msg}")
