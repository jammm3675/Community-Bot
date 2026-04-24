from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Profile", callback_data="rpg_stats"),
        InlineKeyboardButton(text="📦 OTC", callback_data="otc_start"),
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Leaderboard", callback_data="rpg_top"),
        InlineKeyboardButton(text="🏷 Tags", callback_data="rpg_tags"),
    )
    builder.row(InlineKeyboardButton(text="🎁 Secret Supply", callback_data="rpg_burn"))
    return builder.as_markup()


def get_otc_type_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="WTS (Sell)", callback_data="otc_type_WTS"),
        InlineKeyboardButton(text="WTB (Buy)", callback_data="otc_type_WTB"),
    )
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="menu_main"))
    return builder.as_markup()


def get_lot_kb(lot_id, cost):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"🔥 Burn {cost} XP", callback_data=f"burn_lot_{lot_id}"
        )
    )
    return builder.as_markup()
