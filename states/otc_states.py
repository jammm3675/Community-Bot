from aiogram.fsm.state import State, StatesGroup


class OTCStates(StatesGroup):
    choosing_type = State()
    entering_item = State()
    entering_price = State()
