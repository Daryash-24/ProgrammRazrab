import os #Для работы с переменными окружения
from flask import Flask, request, jsonify # Flask - веб-фреймворк, request - для обработки запросов, jsonify - для формирования JSON-ответов
import psycopg2 # Для работы с базой данных

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

# Маршрут для конвертации валюты
@app.route('/convert', methods=['GET'])
def convert_currency():
    # Чтение параметров запроса
    currency_name = request.args.get('currency_name')
    amount = request.args.get('amount')

    # Валидация входных данных
    if not currency_name or not amount:
        return jsonify({"error": "Параметры 'currency_name' и 'amount' обязательны"}), 400

    try:
        amount = float(amount) # Пробуем преобразовать сумму в число
    except ValueError:
        return jsonify({"error": "Сумма должна быть числом"}), 400

    # Используем контекстный менеджер для автоматического закрытия соединения
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем, есть ли валюта в базе данных
            cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name.upper(),))
            result = cur.fetchone() # Получаем первую строку результата

            if not result:
                return jsonify({"error": f"Валюта '{currency_name}' не найдена в базе данных"}), 404

            rate = float(result[0])
            converted_amount = round(amount * rate, 2) # Вычисляем конвертированную сумму с округлением

        # Возвращаем результат в JSON формате
    return jsonify({
        "currency_name": currency_name.upper(),
        "amount": amount,
        "rate": rate,
        "converted_amount": converted_amount
    }), 200

# Маршрут для получения списка всех валют
@app.route('/currencies', methods=['GET'])
def get_currencies():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Получаем все валюты из БД
            cur.execute("SELECT currency_name, rate FROM currencies")
            currencies = cur.fetchall() # Получаем все строки результата
            # Формируем JSON-ответ
            result = [{"currency_name": row[0], "rate": float(row[1])} for row in currencies]
    return jsonify(result), 200

# Запускаем приложение
if __name__ == '__main__':
    app.run(port=5002)