import os #Для работы с переменными окружения
from flask import Flask, request, jsonify # Flask - веб-фреймворк, request - для обработки запросов, jsonify - для формирования JSON-ответов
import psycopg2 # Для работы с базой данных
from psycopg2 import sql

# Создание экземпляра Flask приложения
app = Flask(__name__)

# Получение параметров подключения к бд из переменных окружения
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
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Роут для добавления новой валюты
@app.route('/load', methods=['POST'])
def load_currency():
    # Получение данных из запроса в формате JSON
    data = request.get_json()
    currency_name = data.get('currency_name')
    rate = data.get('rate')

    # Проверка наличия обязательных полей
    if not currency_name or not rate:
        return jsonify({"error": "Необходимо указать название валюты и курс"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверка существования валюты
        cur.execute("SELECT id FROM currencies WHERE currency_name = %s", (currency_name,))
        if cur.fetchone():
            return jsonify({"error": "Данная валюта уже существует"}), 400

        # Добавление новой валюты
        cur.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name, float(rate))
        )
        conn.commit() # Фиксация изменений в бд

        # Формирование успешного ответа
        return jsonify({
            "message": f"Валюта {currency_name} успешно добавлена",
            "currency_name": currency_name,
            "rate": rate
        }), 200

    except ValueError:
        # Обработка ошибки, если курс не является числом
        return jsonify({"error": "Курс должен быть числом"}), 400
    finally:
        # Закрытие соединения с БД в любом случае
        cur.close()
        conn.close()

# Роут для обновления курса валюты
@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.get_json()
    currency_name = data.get('currency_name')
    new_rate = data.get('rate')

    # Проверка наличия обязательных полей
    if not currency_name or not new_rate:
        return jsonify({"error": "Необходимо указать название валюты и новый курс"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверка существования валюты
        cur.execute("SELECT id FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({"error": "Данная валюта не существует"}), 404

        # Обновление курса валюты
        cur.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (float(new_rate), currency_name)
        )
        conn.commit()

        # Формирование успешного ответа
        return jsonify({
            "message": f"Курс валюты {currency_name} успешно обновлен",
            "currency_name": currency_name,
            "new_rate": new_rate
        }), 200

    except ValueError:
        # Обработка ошибки, если курс не является числом
        return jsonify({"error": "Курс должен быть числом"}), 400
    finally:
        cur.close()
        conn.close()

# Роут для удаления валюты
@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.get_json()
    currency_name = data.get('currency_name')

    # Проверка наличия обязательного поля
    if not currency_name:
        return jsonify({"error": "Необходимо указать название валюты"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверка существования валюты
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({"error": "Данная валюта не существует"}), 404

        # Удаление валюты
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()

        return jsonify({
            "message": f"Валюта {currency_name} успешно удалена",
            "currency_name": currency_name
        }), 200
    finally:
        cur.close()
        conn.close()

# Запуск приложения
if __name__ == '__main__':
    app.run(port=5001, debug=True) # Запуск на порту 5001 с включенным режимом отладкиЫ