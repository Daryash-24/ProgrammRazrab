#Импорт необходимых модулей
#Flask для создания веб-приложения, request для обработки запросов, jsonify для возврата JSON-ответов
from flask import Flask, request, jsonify

#Модуль для генерации случайных чисел
import random

#Создание экземпляра Flask
app = Flask(__name__)

#Обработчик POST-запросов по маршруту "/number/"
@app.route("/number/", methods=["POST"])
def chislo():
    #Проверка Content-Type заголовка запроса
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":

        #Возвращаем ошибку 400, если Content-Type не JSON
        return f"Content-Type {content_type} not supported!", 400

    #Получаем JSON-данные из тела запроса
    json_data = request.get_json()

    #Извлекаем параметр jsonParam и преобразуем в число с плавающей точкой
    jsonParam = float(json_data["jsonParam"])

    #Генерация рандомного числа от 1 до 100
    random_chislo = random.uniform(1, 100)

    #Умножение параметра на рандомно сгенерированное число
    result = jsonParam * random_chislo

    #Список возможных операций
    #sum - сложение, sub - вычитание, mul - умножение, div - деление
    operation = ['sum', 'sub', 'mul', 'div']

    #Выбор рандомной операции из списка операций
    random_operation = random.choice(operation)

    #Возвращаем JSON-ответ с результатами
    return jsonify({
        "Число пришедшие в JSON": jsonParam,
        "Рандомное число": random_chislo,
        "Рандомная операция": random_operation,
        "Результат умножения": round(result, 4)
    })

#Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)