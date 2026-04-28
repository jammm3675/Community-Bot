from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from loader import ADMIN_IDS

def get_main_menu(user_id: int = None):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Profile", callback_data="rpg_stats"),
        InlineKeyboardButton(text="📦 OTC", callback_data="otc_start"),
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Leaderboard", callback_data="rpg_top"),
        InlineKeyboardButton(text="🏷 Tags", callback_data="rpg_tags"),
    )

    # Only show Secret Supply for admins or if we want to show it to everyone (as per requirements refactoring)
    # The requirement says: "For normal users: Button is hidden. For admins: Button opens management."
    if user_id in ADMIN_IDS:
        builder.row(InlineKeyboardButton(text="⚙️ Manage Supplies", callback_data="admin_supply_menu"))
    else:
        # According to point 3: "For ordinary users: The button is hidden."
        # However, point 1 mentions "start OTC, view profile" should have GIFs like in donor.
        # Let's keep it hidden for now as per point 3.
        pass

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
