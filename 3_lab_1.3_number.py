#Импорт необходимых модулей
#Flask для создания веб-приложения, jsonify для возврата JSON-ответов
from flask import Flask, jsonify
#Модуль для генерации случайных чисел
import random
#Создание экземпляра Flask
app = Flask(__name__)

#Обработчик DELETE-запросов по маршруту "/number/"
@app.route("/number/", methods=["DELETE"])
def chislo():

    #Генерация рандомного числа от 1 до 1000
    random_chislo = random.uniform(1, 1000)

    #Список возможных операций
    #sum - сложение, sub - вычитание, mul - умножение, div - деление
    operation = ['sum', 'sub', 'mul', 'div']

    #Выбор рандомной операции из списка операций
    random_operation = random.choice(operation)

    #Возвращаем JSON-ответ с результатами
    return jsonify({
        "Рандомное число": round(random_chislo, 3),
        "Рандомная операция": random_operation
    })

#Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)