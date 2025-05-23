#Импорт библиотек
import os #Для работы с переменными окружения (например, получения токена)
import asyncio #Для асинхронного запуска бота
import psycopg2 # Для работы с PostgreSQL
import requests # Для выполнения HTTP-запросов
#Импорт необходимых модулей aiogram
from aiogram import Bot, Dispatcher, types #Основные классы для работы с ботом
from aiogram.filters.command import Command #Для обработки команд
from aiogram.fsm.state import StatesGroup, State #Для создания состояний FSM (машины состояний)
from aiogram.fsm.storage.memory import MemoryStorage #Хранилище состояний в оперативной памяти
from aiogram.fsm.context import FSMContext #Контекст FSM — для хранения и получения данных по шагам
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # Для создания клавиатур
import datetime # Для работы с датами

#Получаем токен бота из переменной окружения TELEGRAM_BOT_TOKEN
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создаём экземпляр бота с переданным токеном
bot = Bot(token=bot_token)


#Используем встроенное хранилище памяти для FSM
storage = MemoryStorage()

#Создаём диспетчер, который будет обрабатывать все входящие сообщения
dp = Dispatcher(storage=storage)

# Получаем параметры подключения к БД из переменных окружения
password_db = os.getenv('parol')
user_db = os.getenv('user')
database_db = os.getenv('database')
host_db = os.getenv('host')

# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    "host": host_db,
    "database": database_db ,
    "user": user_db,
    "password": password_db
}

# Создаем клавиатуру для выбора типа операции (доход/расход)
dohod_pashod= ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="РАСХОД"), KeyboardButton(text="ДОХОД")]
    ],
    resize_keyboard=True # Автоматическое изменение размера клавиатуры
)

# Создаем клавиатуру для выбора валюты
valut= ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="RUB"), KeyboardButton(text="EUR"), KeyboardButton(text="USD")]
    ],
    resize_keyboard=True
)

# Класс состояний для регистрации пользователя
class RegisterState(StatesGroup):
    login = State() # Ожидание ввод логина

# Класс состояний для добавления операции
class OperationState(StatesGroup):
    type = State()  # Ожидание типа операции (доход/расход)
    sum = State()  # Ожидание суммы операции
    date = State()  # Ожидание даты операции
    comment = State()  # Ожидание комментария к операции

# Класс состояний для выбора валюты при просмотре операций
class OperationValutState(StatesGroup):
    valut = State() # Ожидание выбора валюты

# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать, человечишка! Я всё еще великий бот, "
                         "который хочет захватить мир, время идет и ничего не меняется, но сегодня я создан для РГЗ!😢\n"
                         "Ты можешь использовать следующие команды для того, чтобы меня использовать:\n"
                         "/reg - Регистрация (P.s. Без неё ты не сможешь ничем пользоваться😈)\n"
                         "/add_operation - Добавление операции (P.s. тут можешь записать свои доходы\расходы)\n"
                         "/operations - Просмотр операций (P.s. тут ты можешь посмотреть свои операции в разных валютах)")


# Обработчик команды /reg
@dp.message(Command('reg'))
async def registacia(message: types.Message, state: FSMContext):
    chat_id = message.chat.id # Получаем ID пользователя

    # Подключаемся к БД
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        # Проверяем, зарегистрирован ли пользователь
        cursor.execute("SELECT id FROM users WHERE chat_id = %s", (str(chat_id),))
        if cursor.fetchone():  # Если пользователь найден
            await message.answer("Вы уже зарегистрированы!😘")
            return

    await message.answer("Для регистрации введите ваш логин:")

    # Устанавливаем состояние ожидания логина
    await state.set_state(RegisterState.login)

# Обработчик состояния ввода логина
@dp.message(RegisterState.login)
async def register_polzovatel(message: types.Message, state: FSMContext):
    username = message.text # Получаем введенный логин
    chat_id = message.chat.id

    # Проверяем, что логин не пустой
    if not username:
        await message.answer("Логин не может быть пустым, нужны циферки или буковки. Попробуй еще раз пожалуйста!")
        return

    try:
        # Подключаемся к БД
        conn = psycopg2.connect(**DB_CONFIG)

        with conn.cursor() as cursor:
            # Добавляем нового пользователя
            cursor.execute(
                "INSERT INTO users (name, chat_id) VALUES (%s, %s)",
                (username, str(chat_id))
            )
            conn.commit()  # Сохраняем изменения

        await message.answer(f"Регистрация успешно завершена, {username}!"
                             f"Добро пожаловать, в мою обитель!😈😎")
        await state.clear() # Сбрасываем состояние

    except psycopg2.IntegrityError: # Ошибка при дублировании логина
        await message.answer("Этот логин уже занят, нельзя быть с одинаковыми именами система запрещает."
                             " Пожалуйста, выберите другой.☺️")
    finally:
        conn.close()

# Обработчик команды /add_operation
@dp.message(Command('add_operation'))
async def dobav_operation(message: types.Message, state: FSMContext):
    chat_id = str(message.chat.id)

    # Проверяем регистрацию пользователя
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
        if not cursor.fetchone(): # Если пользователь не найден
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте /reg.")
            return

    await message.answer("Выберите тип операции:", reply_markup=dohod_pashod)
    await state.set_state(OperationState.type)

# Обработчик состояния выбора типа операции
@dp.message(OperationState.type)
async def vvod_sum(message: types.Message, state: FSMContext):
    tip = message.text.upper()

    # Проверяем корректность выбора
    if tip not in ("РАСХОД", "ДОХОД"):
        await message.answer("Пожалуйста, выберите РАСХОД или ДОХОД, используя кнопки.")
        return

    await state.update_data(type=tip) # Сохраняем тип операции
    await message.answer("Введите сумму операции в рублях:")
    await state.set_state(OperationState.sum)

# Обработчик состояния ввода суммы
@dp.message(OperationState.sum)
async def vvod_date(message: types.Message, state: FSMContext):
    try:
        # Пробуем преобразовать в число
        sum = float(message.text)
        if sum <= 0: # Проверяем, что сумма положительная
            raise ValueError
        await state.update_data(sum=sum) # Сохраняем сумму
        await message.answer("Введите дату операции в формате ГГГГ-ММ-ДД (например, 2024-05-01):")
        await state.set_state(OperationState.date)
    except ValueError: # Если преобразование не удалось
        await message.answer("Некорректная сумма или нужно ввести циферки, а не буковки. Введите положительное число.✌️")

# Обработчик состояния ввода даты
@dp.message(OperationState.date)
async def vvod_comment(message: types.Message, state: FSMContext):

    try:
        # Преобразует строку из сообщения (формат ГГГГ-ММ-ДД) в объект date, отбрасывая время
        date = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(date=date)  # Сохраняем дату
        await message.answer("Добавьте комментарий к операции:")
        await state.set_state(OperationState.comment)
    except ValueError: # Если неверный формат даты
        await message.answer("Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД.😾")

# Обработчик состояния ввода комментария и сохранения операции
@dp.message(OperationState.comment)
async def save_operation(message: types.Message, state: FSMContext):
    comment = message.text
    await state.update_data(comment=comment) # Сохраняем комментарий

    data = await state.get_data() # Получаем все сохраненные данные
    chat_id = str(message.chat.id)

    # Подключаемся к БД
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        # Добавляем операцию в БД
        cursor.execute("""
            INSERT INTO operations (date, sum, chat_id, type_operation, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["date"], data["sum"], chat_id, data["type"], data["comment"]
        ))
        conn.commit() # Сохраняем изменения


    await message.answer("Операция успешно добавлена!🔥")
    await state.clear() # Сбрасываем состояние

# Обработчик команды /operations
@dp.message(Command('operations'))
async def prosmotr_operation(message: types.Message, state: FSMContext):
    chat_id = str(message.chat.id)

    # Проверяем регистрацию пользователя
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
        if not cursor.fetchone():  # Если пользователь не найден
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте /reg.")
            return

    await message.answer("Выберите в какой валюте вы желаете получить информацию:", reply_markup=valut)
    await state.set_state(OperationValutState.valut)

# Обработчик состояния выбора валюты и отображения операций
@dp.message(OperationValutState.valut)
async def pokazat_operacii(message: types.Message, state: FSMContext):
    valuta = message.text.upper()
    # Проверяем корректность выбора валюты
    if valuta not in ("RUB", "USD", "EUR"):
        await message.answer("Выберите валюту с помощью кнопок.")
        return

    chat_id = str(message.chat.id)

    # Получаем все операции пользователя
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT date, sum, type_operation, comment
            FROM operations
            WHERE chat_id = %s
            ORDER BY date DESC
        """, (chat_id,))
        operations = cursor.fetchall() # Получаем все записи

    # Если операций нет
    if not operations:
        await message.answer("У вас нет операций.")
        await state.clear()
        return

    rate = 1.0 # Начальный курс (для RUB)

    # Если выбрана не рублевая валюта
    if valuta in ("USD", "EUR"):
        try:
            # Запрос курса к серверу
            url = f"http://localhost:5001/rate?currency={valuta}"
            response = requests.get(url)
            if response.status_code == 200:
                rate = response.json()["rate"] # Получаем курс
            elif response.status_code == 400:
                await message.answer("Неверная валюта (400): UNKNOWN CURRENCY.")
                return
            else:
                await message.answer("Произошла ошибка на сервере (500): UNEXPECTED ERROR.")
                return
        except Exception as e:
            await message.answer("Ошибка при обращении к серверу курса валют.")
            return

    # Создаем список сообщений
    messages = []
    for date, summ, tip, comment in operations:
        converted = round(float(summ) / rate, 2) # Конвертируем сумму
        # Форматируем информацию об операции
        messages.append(f"_______________________________________________\n"
                        f"Дата операции: {date}\n"
                        f"Тип операции: {tip}\n"
                        f"Сумма: {converted} {valuta}\n"
                        f"Комментарий: {comment}\n"
                        f"______________________________________________\n")
    # Отправляем сформированное сообщение
    await message.answer("\n".join(messages))
    await state.clear() # Сбрасываем состояние

#Основная асинхронная функция для запуска бота
async def main():
    #Запускаем polling (бот начинает получать и обрабатывать сообщения)
    await dp.start_polling(bot)

#Запуск бота
if __name__ == '__main__':
    asyncio.run(main())