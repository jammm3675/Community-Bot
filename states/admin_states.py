from aiogram.fsm.state import State, StatesGroup

class SupplyCreation(StatesGroup):
    entering_name = State()
    entering_description = State()
    entering_price = State()
    entering_limit = State()
