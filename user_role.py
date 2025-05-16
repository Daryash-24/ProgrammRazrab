from flask import Flask, request, jsonify # Flask — это веб-фреймворк, request нужен для получения параметров запроса, jsonify — для возврата JSON-ответов
import psycopg2 # Библиотека для работы с бд
import os # Для работы с переменными окружения

# Создаём экземпляр Flask-приложения
app = Flask(__name__)

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

# Функция для установки подключения к базе данных
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Объявляем маршрут /check_admin, который обрабатывает GET-запросЫ
# Проверяет, является ли пользователь с заданным chat_id администратором
@app.route('/check_admin', methods=['GET'])
def check_admin():
    # Получаем параметр chat_id из строки запроса
    chat_id = request.args.get('chat_id')
    if not chat_id:
        # Если chat_id не передан — возвращаем ошибку 400 (неверный запрос) и сообщение
        return jsonify({"У Вас нет прав администратора"}), 400

    # Подключаемся к базе данных
    conn = get_db_connection()
    cur = conn.cursor()

    # Выполняем SQL-запрос: проверяем, есть ли запись с таким chat_id в таблице admins
    cur.execute("SELECT 1 FROM admins WHERE chat_id = %s", (str(chat_id),))

    # Проверяем, есть ли результат (если есть — значит пользователь админ)
    is_admin = cur.fetchone() is not None

    # Закрываем курсор и соединение с базой данных
    cur.close()
    conn.close()

    return jsonify({"is_admin": is_admin}), 200

# Запуск приложения
if __name__ == '__main__':
    app.run(port=5003)
