import os #Для работы с переменными окружения
import psycopg2 # Для работы с базой данных

# Настройка подключения к бд, получаем значение переменных окружения
password_db = os.getenv('parol')
user_db = os.getenv('user')
database_db = os.getenv('database')
host_db = os.getenv('host')
conn = psycopg2.connect(
    host=host_db,
    database=database_db,
    user=user_db,
    password=password_db
)
cur = conn.cursor()

# Создание таблицы currencies
cur.execute("""
           CREATE TABLE IF NOT EXISTS currencies (
               id SERIAL PRIMARY KEY,
               currency_name VARCHAR(50) UNIQUE NOT NULL,
               rate NUMERIC NOT NULL
           )
       """)

# Создание таблицы admins
cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        chat_id VARCHAR(50) NOT NULL UNIQUE
    )
""")

# Сохранение изменений и закрытие соединения
conn.commit()