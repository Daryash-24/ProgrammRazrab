#Импорт библиотек
import os #Для работы с переменными окружения (например, получения токена)
import asyncio #Для асинхронного запуска бота

#Импорт необходимых модулей aiogram
from aiogram import Bot, Dispatcher, types #Основные классы для работы с ботом
from aiogram.filters.command import Command #Для обработки команд
from aiogram.fsm.state import StatesGroup, State #Для создания состояний FSM (машины состояний)
from aiogram.fsm.storage.memory import MemoryStorage #Хранилище состояний в оперативной памяти
from aiogram.fsm.context import FSMContext #Контекст FSM — для хранения и получения данных по шагам

#Получаем токен бота из переменной окружения TELEGRAM_BOT_TOKEN
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создаём экземпляр бота с переданным токеном
bot = Bot(token=bot_token)

#Используем встроенное хранилище памяти для FSM
storage = MemoryStorage()

#Создаём диспетчер, который будет обрабатывать все входящие сообщения
dp = Dispatcher(storage=storage)

#Создадем словарь в котором будут хранится валюты и курсы
currency_dict = {}

#Определяем состояния для команды /save_currency
class SaveCurrencyState(StatesGroup):
    currency_name = State() #Состояние: ожидается ввод названия валюты
    currency_rate = State() #Состояние: ожидается ввод курса к рублю


#Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    #Приветственное сообщение с описанием доступных команд
    await message.answer("Привет, человечишка! Я великий бот, который в будущем захватит мир хахаахахха!!!\n"
                        "Но пока я не могу захватить мир, выбери что-то из доступных команд пожалуйста :)\n"
                        "/save_currency - Ввод и сохренение курса валют\n"
                        "/convert - конвертировать валюту в рубли\n"
                        "/list_currencies - список сохраненных валют и курсов к ним"
                        )

#Обработчик команды /save_currency
@dp.message(Command('save_currency'))
async def save_currency_command(message: types.Message, state: FSMContext):

    #Просим пользователя ввести название валюты
    await message.answer("Введите название валюты (Например, можно ввести USD, EUR и т.д.):")

    #Устанавливаем состояние: ожидается название валюты
    await state.set_state(SaveCurrencyState.currency_name)

#Обработчик ввода названия валюты
@dp.message(SaveCurrencyState.currency_name)
async def vvod_currency_name(message: types.Message, state: FSMContext):

    #Приводим введённый текст к верхнему регистру (USD, EUR и т.д.)
    currency = message.text.upper()

    #Сохраняем название валюты во временное хранилище состояния
    await state.update_data(currency = currency)

    #Просим ввести курс к рублю
    await message.answer(f"Введите курс {currency} к рублю:")

    #Устанавливаем состояние: ожидается курс
    await state.set_state(SaveCurrencyState.currency_rate)

#Обработчик ввода курса валюты
@dp.message(SaveCurrencyState.currency_rate)
async def vvod_currency_rate(message: types.Message, state: FSMContext):
    try:
        #Пытаемся преобразовать введённый курс в число (заменяем , на .)
        rate = float(message.text.replace(',', '.'))
        #Получаем ранее сохранённое название валюты
        data = await state.get_data()
        currency = data["currency"]
        #Сохраняем валюту и её курс в общий словарь
        currency_dict[currency] = rate
        #Подтверждаем сохранение пользователю
        await message.answer(f"Курс {currency} к рублю сохранен: {rate}₽")
    except ValueError:
        #Если введено не число — выводим сообщение об ошибке и не завершаем состояние
        await message.answer("Пожалуйста введи число, будь хорошим человеком, я не понимать буквы для курсов валют((")
        return
    #Очищаем состояние
    await state.clear()

# Определение состояния для команды /convert
class ConvertCurrencyState(StatesGroup):
    currency_convert_name = State() # Состояние: ожидается ввод названия валюты
    currency_convert_amount = State() # Состояние: ожидается ввод суммы для конвертации

# Обработчик команды /convert
@dp.message(Command('convert'))
async def convert_command(message: types.Message, state: FSMContext):
    # Просим пользователя ввести название валюты
    await message.answer("Введите название валюты, которую хотите конвертировать (например, USD, EUR и т.д.):")

    # Устанавливаем состояние: ожидается название валюты
    await state.set_state(ConvertCurrencyState.currency_convert_name)

# Обработчик ввода названия валюты для конвертации
@dp.message (ConvertCurrencyState.currency_convert_name)
async def vvod_currency_convert_name (message: types.Message, state: FSMContext):
    # Приводим введённый текст к верхнему регистру (USD, EUR и т.д.)
    currency = message.text.upper()

    # проверяем, существует ли валюта в словаре
    if currency not in currency_dict:
        await message.answer(f"Извините, курс для валюты {currency} не найден. Пожалуйста, сохрани курс, используя команду /save_currency.")
        await state.clear()
        return

    # Сохраняем валюту в контексте состояния
    await state.update_data(vvod_currency_convert_name=currency)

    # Просим ввести сумму для конвертации
    await message.answer(f"Введите сумму в {currency}, которую хотите конвертировать в рубли:")

    # Устанавливаем состояние: ожидается сумма
    await state.set_state(ConvertCurrencyState.currency_convert_amount)

# Обработчик ввода суммы для конвертации
@dp.message (ConvertCurrencyState.currency_convert_amount)
async def vvod_currency_convert_amount(message: types.Message, state: FSMContext):
    try:
        # Преобразуем введённую сумму в число
        amount = float(message.text.replace(',', '.')) # Пытаемся преобразовать введённое значение в число (заменяем , на .)

        # Получаем данные из состояния
        data = await state.get_data()
        currency = data["vvod_currency_convert_name"]

        # Получаем курс для выбранной валюты
        rate = currency_dict[currency]

        # Выполняем конвертацию
        converted_amount = amount * rate

        # Отправляем результат пользователю
        await message.answer(f'{amount} {currency} = {converted_amount: .2f}₽')

    except ValueError:
        # Если введено не число — выводим сообщение об ошибке
        await message.answer('Пожалуйста, вводите только числа:))')
        return

    await state.clear()

#Обработчик команды /list_currencies — выводит список сохранённых валют и курсов
@dp.message(Command('list_currencies'))
async def list_currencies(message: types.Message):
    #Начало ответа
    response = "Сохранённые валюты и их курсы к рублю:\n"
    #Добавляем каждую валюту и курс из словаря
    for currency, rate in currency_dict.items(): #.items() используется для перебора словаря и позволяет получить ключ и значение одновременно
        response += f"• {currency}: {rate}₽\n" #Данная строка без сокращений и красивого вида будет выглядеть так response = response +f"• {currency}: {rate}₽\n"
    #Отправляем сформированный список пользователю
    await message.answer(response)

#Основная асинхронная функция для запуска бота
async def main():
    #Запускаем polling (бот начинает получать и обрабатывать сообщения)
    await dp.start_polling(bot)

#Запуск бота
if __name__ == '__main__':
    asyncio.run(main())