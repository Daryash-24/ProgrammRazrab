from flask import Flask, request, jsonify

# Инициализация Flask приложения
app = Flask(__name__)

# Словарь с курсами валют
Slovar_for_valut = {
    "USD": 79.75,
    "EUR": 91.30
}

# Обработчик GET-запросов по адресу /rate
@app.route('/rate', methods=['GET'])
def vnesh_server():
    try:
        # Получаем параметр currency из URL и приводим к верхнему регистру
        currency = request.args.get("currency", "").upper()

        # Проверяем наличие валюты в словаре
        if currency not in Slovar_for_valut:
            # Возвращаем ошибку 400 если валюта неизвестна
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400
        # Возвращаем курс валюты с кодом 200 (успех)
        return jsonify({"rate": Slovar_for_valut[currency]}), 200
    except Exception as e:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

# Запуск приложения на порту 5001
if __name__ == '__main__':
    app.run(port=5001, debug=True)