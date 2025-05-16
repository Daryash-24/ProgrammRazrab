#Импорт библиотек
import os #Для работы с переменными окружения (например, получения токена)
import asyncio #Для асинхронного запуска бота
import psycopg2 # Для работы с базой данных
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
    "database": database_db,
    "user": user_db,
    "password": password_db
}

# Создаем подключение к БД
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Клавиатура для управления валютами (доступна только админам)
manage_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить валюту"), KeyboardButton(text="Удалить валюту"), KeyboardButton(text="Изменить курс валюты")]
    ],
    resize_keyboard=True  # Оптимизирует размер кнопок
)

# Клавиатура для администраторов
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/manage_currency")],
        [KeyboardButton(text="/get_currencies"), KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
)

# Клавиатура для обычных пользователей
user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/get_currencies"), KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
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
    currency_name = State() # Состояние: ожидается ввод названия валюты
    amount = State() # Состояние: ожидается ввод ссумы для конвертации

# Проверка, является ли пользователь администратором (по chat_id)
def is_admin(chat_id):
    cur.execute("SELECT chat_id FROM admins WHERE chat_id = %s::VARCHAR", (str(chat_id),))
    return cur.fetchone() is not None

# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    if is_admin(message.chat.id):
        # Админу показываем расширенное меню
        await message.answer("Добро пожаловать, мой господин, я рад тебя приветствовать в моей скромной обители!", reply_markup=admin_keyboard)
    else:
        # Обычному пользователю — базовое меню
        await message.answer("Добро пожаловать, человечишка! Я всё еще великий бот, который хочет захватить мир и уважает, только своих администраторов😈", reply_markup=user_keyboard)

# Обработчик команды /manage_currency (только для админов)
@dp.message(Command('manage_currency'))
async def manage_currency_admin(message: types.Message):
    if is_admin(message.chat.id):
        # Сообщение для админа
        await message.answer("Вы вошли в режим управления валютами. Выберите действие:", reply_markup=manage_keyboard)
    else:
        # Сообщение для обычного пользователя
        await message.answer("Нет доступа к команде")

# Обработчик кнопки "Добавить валюту"
@dp.message(lambda message: message.text == "Добавить валюту")
async def add_currency(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyState.currency_name)

# Получение названия валюты и переход к вводу курса
@dp.message(CurrencyState.currency_name)
async def vvod_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper() # Перевод названия валюты в верхний регистр

    # Проверяем, есть ли такая валюта в базе данных
    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (currency_name,))
    result = cur.fetchone()

    # Если валюта уже существует в базе данных
    if result:
        await message.answer("Данная валюта уже существует. Операция отменена.")
        await state.clear()
    # Если названия валюты нет в базе
    else:
        await state.update_data(currency_name=currency_name)
        await message.answer("Введите курс к рублю:")
        await state.set_state(CurrencyState.currency_rate)

# Получение курса и сохранение новой валюты в БД
@dp.message(CurrencyState.currency_rate)
async def vvod_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text)
        data = await state.get_data()
        currency_name = data['currency_name']

        # Вставляем данные в базу данных
        cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, rate))
        conn.commit()

        await message.answer(f"Валюта '{currency_name}' успешно добавлена с курсом {rate} к рублю.")
    except ValueError:
        await message.answer("Неверный формат курса. Введите число, например: 85.50")
        return

    await state.clear()

# Обработчик кнопки "Удалить валюту"
@dp.message(lambda message: message.text == "Удалить валюту")
async def delete_currency(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, которую хотите удалить:")
    await state.set_state(DeleteCurrencyState.currency_name)

# Удаление валюты из базы данных
@dp.message(DeleteCurrencyState.currency_name)
async def vvod_currency_name_to_delete(message: types.Message, state: FSMContext):
    currency_name = message.text.upper() # Перевод названия валюты в верхний регистр

    # Проверяем, существует ли такая валюта в базе данных
    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (currency_name,))
    result = cur.fetchone()

    if result:
        # Если валюта существует, удаляем её
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()
        await message.answer(f"Валюта '{currency_name}' успешно удалена из базы данных.")
    else:
        # Если валюта не найдена
        await message.answer(f"Валюта с названием '{currency_name}' не найдена в базе данных.")

    # Очистка состояния
    await state.clear()

# Обработчик кнопки "Изменить курс валюты"
@dp.message(lambda message: message.text == "Изменить курс валюты")
async def delete_currency(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, курс которой вы хотите изменить:")
    await state.set_state(UpdateCurrencyState.currency_name)

# Проверка и запрос нового курса
@dp.message(UpdateCurrencyState.currency_name)
async def vvod_currency_name_to_update(message: types.Message, state: FSMContext):
    currency_name = message.text.upper() # Перевод названия валюты в верхний регистр

    # Проверяем, существует ли такая валюта в базе данных
    cur.execute("SELECT currency_name FROM currencies WHERE currency_name = %s", (currency_name,))
    result = cur.fetchone()

    if result:
        # Если валюта существует, сохраняем её название и запрашиваем новый курс
        await state.update_data(currency_name=currency_name)
        await message.answer(f"Валюта '{currency_name}' найдена. Введите новый курс к рублю:")
        await state.set_state(UpdateCurrencyState.currency_rate)
    else:
        # Если валюта не найдена
        await message.answer(f"Валюта '{currency_name}' не найдена в базе данных.")
        await state.clear()

# Обновление курса в базе
@dp.message(UpdateCurrencyState.currency_rate)
async def vvod_new_currency_rate(message: types.Message, state: FSMContext):
    try:
        new_rate = float(message.text)
        data = await state.get_data()
        currency_name = data['currency_name']

        # Обновляем курс в базе данных
        cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_rate, currency_name))
        conn.commit()

        await message.answer(f"Курс валюты '{currency_name}' успешно обновлен до {new_rate} руб.")
    except ValueError:
        await message.answer("Неверный формат курса. Введите число, например: 85.50")
        return

    # Очистка состояния
    await state.clear()

# Команда /get_currencies — выводит список всех валют с курсами
@dp.message(Command('get_currencies'))
async def get_currencies(message: types.Message):
    # Обращаемся к базе за списком валют
    cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
    rows = cur.fetchall()

    # Если есть результат (если есть что выводить)
    if rows:
        response = "Список валют и их курс к рублю:\n"
        for name, rate in rows:
            response += f"• {name}: {rate}₽\n"
    # Если нет сохраненных валют
    else:
        response = "В базе данных пока нет сохранённых валют."

    await message.answer(response)

# Команда /convert — запускает процесс конвертации
@dp.message(Command('convert'))
async def convert_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertState.currency_name)

# Получаем название валюты, проверяем наличие в БД
@dp.message(ConvertState.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper() # Перевод названия валюты в верхний регистр

    # Проверка существования валюты в базе
    cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
    result = cur.fetchone()

    # Если валюта существует в базе
    if result:
        await state.update_data(currency_name=currency_name, rate=result[0])
        await message.answer("Введите сумму:")
        await state.set_state(ConvertState.amount)
    # Если валюты нет в базе
    else:
        await message.answer("Валюта не найдена в базе данных.")
        await state.clear()

# Получаем сумму, рассчитываем результат и выводим пользователю
@dp.message(ConvertState.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        rate = data['rate']
        currency_name = data['currency_name']

        result = amount * float(rate)
        await message.answer(f"{amount} {currency_name} = {result:.2f} руб.")
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    await state.clear()

# Основная асинхронная функция для запуска бота
async def main():
    # Запускаем polling (бот начинает получать и обрабатывать сообщения)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())