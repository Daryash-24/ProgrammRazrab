#Импорт библиотек
import os #Для работы с переменными окружения (например, получения токена)
import asyncio #Для асинхронного запуска бота
import psycopg2 # Для работы с PostgreSQL
import requests # Для HTTP-запросов к микросервисам

#Импорт необходимых модулей aiogram
from aiogram import Bot, Dispatcher, types #Основные классы для работы с ботом
from aiogram.filters.command import Command #Для обработки команд
from aiogram.fsm.state import StatesGroup, State #Для создания состояний FSM (машины состояний)
from aiogram.fsm.storage.memory import MemoryStorage #Хранилище состояний в оперативной памяти
from aiogram.fsm.context import FSMContext #Контекст FSM — для хранения и получения данных по шагам
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

#Получаем токен бота из переменной окружения TELEGRAM_BOT_TOKEN
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создаём экземпляр бота с переданным токеном
bot = Bot(token=bot_token)


#Используем встроенное хранилище памяти для FSM
storage = MemoryStorage()

#Создаём диспетчер, который будет обрабатывать все входящие сообщения
dp = Dispatcher(storage=storage)

# Получаем параметры подключения к базе данных из переменных окружения
password_db = os.getenv('parol')
user_db = os.getenv('user')
database_db = os.getenv('database')
host_db = os.getenv('host')
DB_CONFIG = {
    "host": host_db,
    "database": database_db ,
    "user": user_db,
    "password": password_db
}

# Функция для получения подключения к БД
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Создание клавиатуры для управления валютами
keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту")],
            [KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс валюты")]
        ],
        resize_keyboard=True # Автоматическое изменение размера клавиатуры
    )

# Состояния для добавления новой валюты
class CurrencyState(StatesGroup):
    currency_name = State() #Состояние: ожидается ввод названия валюты
    currency_rate = State() #Состояние: ожидается ввод курса к рублю

# Состояния для удаления валюты
class DeleteCurrencyState(StatesGroup):
    currency_name = State() #Состояние: ожидается ввод названия валюты
    currency_rate = State() #Состояние: ожидается ввод курса к рублю

# Состояния для изменения курса валюты
class UpdateCurrencyState(StatesGroup):
    currency_name = State() #Состояние: ожидается ввод названия валюты
    currency_rate = State() #Состояние: ожидается ввод курса к рублю

# Состояния для конвертации валюты
class ConvertState(StatesGroup):
    currency_name = State()
    amount = State()

# URL микросервисов
CURRENCY_MANAGER_URL = "http://localhost:5001"  # Управление валютами
CURRENCY_DATA_MANAGER_URL = "http://localhost:5002"  # Данные о валютах
ADMIN_MANAGER_URL = "http://localhost:5003"  # Управление администраторами

# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    if is_admin(message.chat.id):
        await message.answer("Добро пожаловать, мой господин, я рад тебя приветствовать в моей скромной обители!\n\n"
        "Используйте /help для просмотра доступных команд"    )
    else:
        await message.answer("Добро пожаловать, человечишка! Я всё еще великий бот, который хочет захватить мир и уважает только своих администраторов 😈\n\n"
        "Используйте /help для просмотра доступных команд")

# Обработчик команды управления валютами
@dp.message(Command('manage_currency'))
async def manage_currency(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⚠️ Эта команда доступна только администраторам.")
        return
    await message.answer("Выберите действие для работы с валютой:", reply_markup=keyboard)

# Обработчики для добавления валюты
@dp.message(lambda message: message.text == "Добавить валюту")
async def add_currency_knopka(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyState.currency_name)

# Получение курса валюты
@dp.message(CurrencyState.currency_name)
async def add_currency(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите курс к рублю:")
    await state.set_state(CurrencyState.currency_rate)

# Добавление валюты с отправкой данных в микросервис
@dp.message(CurrencyState.currency_rate)
async def add_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))

        data = await state.get_data()
        currency_name = data['currency_name']
        try:
            # Отправка данных в микросервис
            response = requests.post(
                f"{CURRENCY_MANAGER_URL}/load",
                json={"currency_name": currency_name, "rate": rate}
            )

            # Обработка ответа
            if response.status_code == 200:
                await message.answer(f"Валюта: {currency_name} успешно добавлена")
            elif response.status_code == 400 and "уже существует" in response.json().get("error", ""):
                await message.answer("Данная валюта уже существует")
            else:
                await message.answer(
                    f"Ошибка на стороне сервера: {response.status_code}")  # Добавил обработку других ошибок

        except requests.exceptions.RequestException:
            await message.answer("Не удалось подключиться к сервису валют")
    except ValueError:
        await message.answer("Я не понимаю буковки для курса введи число пожалуйста😓")
        return
    await state.clear() # Очистка состояния

# Обработчики для удаления валюты
@dp.message(lambda message: message.text == "Удалить валюту")
async def delete_currency_knopka(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты для удаления:")
    await state.set_state(DeleteCurrencyState.currency_name)

# Удаление валюты через микросервис
@dp.message(DeleteCurrencyState.currency_name)
async def delete_currency(message: types.Message, state: FSMContext):
    currency_name = (message.text.upper())
    # Отправляем запрос к микросервису для удаления валюты
    response = requests.post(
        f"{CURRENCY_MANAGER_URL}/delete",
        json={"currency_name": currency_name},
    )

    if response.status_code == 200:
        await message.answer(f"Валюта {currency_name} успешно удалена")
    elif response.status_code == 404:
        await message.answer(f"Валюта {currency_name} не найдена")
    await state.clear() # Очистка состояний

# Обработчики для обновления курса
@dp.message(lambda message: message.text == "Изменить курс валюты")
async def update_currency_knopka(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(UpdateCurrencyState.currency_name)

# Получение названия валюты и запрос нового курса
@dp.message(UpdateCurrencyState.currency_name)
async def update_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip().upper()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите новый курс к рублю:")
    await state.set_state(UpdateCurrencyState.currency_rate)

# Завершение обновления курса
@dp.message(UpdateCurrencyState.currency_rate)
async def update_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currency_name = data['currency_name']

        # Отправляем запрос на обновление курса
        response = requests.post(
            f"{CURRENCY_MANAGER_URL}/update_currency",
            json={"currency_name": currency_name, "rate": rate},
        )

        if response.status_code == 200:
            await message.answer(f"Курс валюты {currency_name} успешно обновлен на {rate}")
        elif response.status_code == 404:
            await message.answer(f"Валюта {currency_name} не найдена")
        else:
            await message.answer("Произошла ошибка при обновлении курса",)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для курса")
        return

    await state.clear()

# Обработчик команды получения списка валют
@dp.message(Command('get_currencies'))
async def get_currencies_command(message: types.Message):
    # Отправляем GET-запрос к сервису data-manager
    response = requests.get(
        f"{CURRENCY_DATA_MANAGER_URL}/currencies",
    )
    if response.status_code == 200:
        currencies = response.json()

        if not currencies:
            await message.answer("Нет доступных валют.")
            return
        # Форматирование списка валют
        currencies_list = "\n".join(
            [f"• {curr['currency_name']}: {curr['rate']} RUB"
                 for curr in currencies]
        )

        await message.answer(
            f"Список доступных валют:\n\n{currencies_list}"
        )

    elif response.status_code == 404:
        await message.answer("Список валют пуст.")
    else:
        await message.answer("Не удалось получить список валют.")


# Реализация команды /convert
@dp.message(Command('convert'))
async def convert_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertState.currency_name)

# Получение названия и запрос суммы
@dp.message(ConvertState.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper() # Перевод в верхний регистр
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите сумму для конвертации:")
    await state.set_state(ConvertState.amount)

# Конвертация через микросервис
@dp.message(ConvertState.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currency_name = data['currency_name']

        # Отправляем запрос в сервис конвертации
        response = requests.get(
            f"{CURRENCY_DATA_MANAGER_URL}/convert",
            params={
                'currency_name': currency_name,
                'amount': amount
            }
        )

        if response.status_code == 200:
            result = response.json()
            await message.answer(
                f"Результат конвертации:\n\n"
                f"{amount} {currency_name} = {result['converted_amount']} RUB\n"
                f"Курс: 1 {currency_name} = {result['rate']} RUB"
            )
        elif response.status_code == 404:
            await message.answer(f"Валюта {currency_name} не найдена")
        else:
            await message.answer("Ошибка при конвертации валюты")

    except ValueError:
        await message.answer("Пожалуйста введите число, я всё еще не научился принимать буквы в курс!!!")
        return
    await state.clear()

# Обработчик команды помощи (типо меню)
@dp.message(Command('help'))
async def help_command(message: types.Message):
    # Вывод списка доступных команд
    commands = [
        "/start - Начало работы с ботом",
        "/manage_currency - Управление валютами (добавление/удаление/изменение курса)",
        "/get_currencies - Просмотр всех доступных валют",
        "/convert - Конвертация валюты в рубли"
    ]
    await message.answer("Доступные команды:\n\n" + "\n".join(commands))

# Проверка, является ли пользователь администратором
def is_admin(chat_id):
    response = requests.get(f"{ADMIN_MANAGER_URL}/check_admin?chat_id={chat_id}")
    if response.status_code == 200:
        data = response.json()
        return data.get("is_admin", False) # Если ключ существует - возвращает его значение
    return False

#Основная асинхронная функция для запуска бота
async def main():
    #Запускаем polling (бот начинает получать и обрабатывать сообщения)
    await dp.start_polling(bot)

#Запуск бота
if __name__ == '__main__':
    asyncio.run(main())