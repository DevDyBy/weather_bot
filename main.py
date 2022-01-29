import pyowm
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor

import config
from states import GetWeather

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(Command(["start", "help"]))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌦 Узнать погоду 🌦",
                callback_data="weather"
            )
        ]
    ])
    await message.answer("Привет, это WeatherBot! Ты можешь узнать у меня погоду 🌦", reply_markup=keyboard)


@dp.callback_query_handler(text="weather")
async def type_city(call: CallbackQuery):
    await call.message.answer("Отправьте название города, погоду которого вы хотите узнать:")
    await GetWeather.weather.set()


@dp.message_handler(state=GetWeather.weather)
async def send_weather(message: types.Message, state: FSMContext):
    place = message.text
    mgr = config.owm.weather_manager()
    try:
        observation = mgr.weather_at_place(place)
        w = observation.weather
        t = w.temperature("celsius")
    except pyowm.commons.exceptions.NotFoundError:
        await message.answer("Город не найден.")
        await message.answer_sticker('CAACAgIAAxkBAAEDH3phcQlrYn60HQxEomCwJ5GxO0aYQgACPQEAAjDUnREQ98oHcZKP7iEE')
    except pyowm.commons.exceptions.TimeoutError:
        await message.answer("Ошибка.")
        await message.answer_sticker('CAACAgIAAxkBAAEDH3phcQlrYn60HQxEomCwJ5GxO0aYQgACPQEAAjDUnREQ98oHcZKP7iEE')
    else:
        await message.answer(f"В городе {place} {t['temp']}°, ощущается как {t['feels_like']}°, максимальная "
                             f"температура - {t['temp_max']}°, минимальная температура - {t['temp_min']}°. Скорость "
                             f"ветра - {w.wind()['speed']} м/с. Облачность - {w.clouds}. Статус - {w.status}. Детали - "
                             f"{w.detailed_status}. Справочное время - {w.reference_time('iso')}. Давление - "
                             f"{w.pressure['press']} Па. Видимость - {w.visibility_distance} метров.")
    await state.finish()


executor.start_polling(dp)

