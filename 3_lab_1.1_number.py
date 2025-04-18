#Импорт необходимых модулей
#Flask для создания веб-приложения, request для обработки запросов, jsonify для возврата JSON-ответов
from flask import Flask, request, jsonify
#Модуль для генерации случайных чисел
import random

#Создание экземпляра Flask
app = Flask(__name__)

#Определение маршрута "/number/" с методом GET
@app.route("/number/", methods=["GET"])
def chislo():

    #Получение параметра 'param' из URL запроса
    param = request.args.get('param')

    #Преобразование параметра в формат числа с плавающей точкой
    chislo = float(param)

    #Генерация рандомного числа от 1 до 1000
    random_chislo = random.uniform(1, 1000)

    #Умножение параметра на рандомно сгенерированное число
    random_umoj_znach = chislo * random_chislo

    #Возврат JSON-ответа с результатами
    return jsonify({
        "Заданное значение параметра": chislo,
        "Рандомное число": round(random_chislo, 3),
        "Результат уножения рандомного числа с введеным": round(random_umoj_znach, 3)
    })

#Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)


