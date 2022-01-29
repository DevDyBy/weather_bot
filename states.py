from aiogram.dispatcher.filters.state import StatesGroup, State


class GetWeather(StatesGroup):
    weather = State()