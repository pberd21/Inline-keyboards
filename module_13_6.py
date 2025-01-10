from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = "YOUR_TELEGRAM_BOT_API_TOKEN"
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Рассчитать"), KeyboardButton("Информация"))

inline_keyboard = InlineKeyboardMarkup(row_width=1)
inline_keyboard.add(
    InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
    InlineKeyboardButton("Формулы расчёта", callback_data="formulas")

@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("Добро пожаловать! Нажмите 'Рассчитать', чтобы узнать вашу норму калорий, или 'Информация', чтобы узнать больше.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Рассчитать")
async def main_menu(message: Message):
    await message.reply("Выберите опцию:", reply_markup=inline_keyboard)

@dp.callback_query_handler(lambda call: call.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    await call.message.reply("Формула Миффлина-Сан Жеора для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\nДля женщин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161")

@dp.callback_query_handler(lambda call: call.data == "calories")
async def set_age(call: types.CallbackQuery):
    await call.message.reply("Введите свой возраст:")
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    weight = float(data["weight"])
    growth = float(data["growth"])
    age = int(data["age"])
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.reply(f"Ваша норма калорий: {calories:.2f} ккал")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Информация")
async def information(message: Message):
    await message.reply("Этот бот помогает рассчитать вашу норму калорий. Нажмите 'Рассчитать', чтобы начать.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
