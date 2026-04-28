from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from loader import ADMIN_IDS

def get_main_menu_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profile", callback_data="rpg_stats", icon_custom_emoji_id="5258185631355378853")
    builder.button(text="📦 OTC", callback_data="otc_start", icon_custom_emoji_id="5257969839313526622")
    builder.button(text="🏆 Top", callback_data="rpg_top", icon_custom_emoji_id="5273741156792951269")
    builder.button(text="🏷 Tags", callback_data="rpg_tags", icon_custom_emoji_id="5296348778012361146")

    # Доступ к Secret Supply только для админов
    if user_id in ADMIN_IDS:
         builder.button(text="⚙️ Admin Supply", callback_data="admin_supply_panel", icon_custom_emoji_id="5258096772776991776")

    builder.adjust(2)
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

def get_admin_supply_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Create Supply", callback_data="admin_create_supply"))
    builder.row(InlineKeyboardButton(text="📜 View Active Lots", callback_data="admin_view_lots"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="menu_main"))
    return builder.as_markup()
