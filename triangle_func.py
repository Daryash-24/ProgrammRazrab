# Создание пользовательского исключения для некорректных сторон треугольника
class IncorrectTriangleSides(Exception):
    pass

# Функция для определения типа треугольника по длинам его сторон
def get_triangle_type(a: float, b: float, c: float) -> str:
    # Проверка, что все стороны положительные
    if not all(side > 0 for side in (a, b, c)):
        raise IncorrectTriangleSides("Все стороны должны быть положительными")

    # Сортировка сторон для удобства проверки неравенства треугольника
    sides = sorted([a, b, c])

    # Проверка неравенства треугольника (сумма двух меньших сторон должна быть больше наибольшей стороны)
    if sides[0] + sides[1] <= sides[2]:
        raise IncorrectTriangleSides("Не выполняется неравенство треугольника")

    # Проверка на равносторонний треугольник
    if a == b == c:
        return "equilateral"
    # Проверка на равнобедренный треугольник
    elif len({a, b, c}) == 2:
        return "isosceles"
    # Если все стороны разные, возвращаем "nonequilateral"
    else:
        return "nonequilateral"

# Пример вызова функции
# print(get_triangle_type(3, 3, 3))