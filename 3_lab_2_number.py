import requests # Для отправки HTTP-запросов
import random

# 1. GET запрос (параметр param=случайное число)
param = random.randint(1, 10) # Генерируем случайное число от 1 до 10 для параметра запроса
otvet_get = requests.get(f'http://localhost:5000/number/?param={param}')
data_get = otvet_get.json() # Преобразуем ответ сервера из JSON формата в словарь Python
print("GET:", data_get)

# 2. POST запрос (тело {"jsonParam": случайное число})
jsonParam = random.randint(1, 10) # Генерируем новое случайное число для тела запроса
otvet_post = requests.post(
    'http://localhost:5000/number/', # Указываем URL endpoint
    json={"jsonParam": jsonParam}, # Передаем тело запроса в формате JSON
    headers={'Content-Type': 'application/json'} # Устанавливаем заголовок Content-Type для корректной обработки JSON
)
data_post = otvet_post.json()
print("POST:", data_post)

# 3. DELETE запрос
otvet_delete = requests.delete('http://localhost:5000/number/')
data_delete = otvet_delete.json()
print("DELETE:", data_delete)

# 4. Вычисление результата
# Проверяем, что оба запроса (POST и DELETE) выполнены успешно (код 200)
if otvet_post.status_code == 200 and otvet_delete.status_code == 200:
    # Получаем числа и операции из ответов
    pervoe_chislo = data_post["Рандомное число"]
    vtoroe_chislo = data_delete["Рандомное число"]
    pervaya_operaciya = data_post["Рандомная операция"]
    vtoraya_operaciya = data_delete["Рандомная операция"]

    # Выполняем операцию из POST ответа между числами из POST и DELETE
    if pervaya_operaciya == 'sum':
        rezultat = pervoe_chislo + vtoroe_chislo
    elif pervaya_operaciya == 'sub':
        rezultat = pervoe_chislo - vtoroe_chislo
    elif pervaya_operaciya == 'mul':
        rezultat = pervoe_chislo * vtoroe_chislo
    elif pervaya_operaciya == 'div':
        rezultat = pervoe_chislo / vtoroe_chislo
    else:
        rezultat = 0
        print("Неизвестная операция в POST ответе")

    # Приводим результат к целому числу
    celiy_rezultat = int(rezultat)
    print(f"Результат вычислений: {celiy_rezultat}")
else:
    print("Не удалось выполнить вычисления из-за ошибок в запросах")