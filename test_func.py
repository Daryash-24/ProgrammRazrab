# Импорт модуля unittest для создания тестов
import unittest
# Импорт тестируемой функции и пользовательского исключения из модуля triangle_func
from triangle_func import get_triangle_type, IncorrectTriangleSides


# Создание класса для тестирования функции определения типа треугольника
class TestTriangleFunction(unittest.TestCase):
# Тесты для функции определения типа треугольника

    def test_equilateral_triangle(self):
    # Тестирование равностороннего треугольника
    # Проверка, что функция возвращает "equilateral" для равносторонних треугольников
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")
        self.assertEqual(get_triangle_type(5.5, 5.5, 5.5), "equilateral")

    def test_isosceles_triangle(self):
    # Тестирование равнобедренных треугольников
    # Проверка, что функция возвращает "isosceles" для равнобедренных треугольников
        self.assertEqual(get_triangle_type(4, 4, 5), "isosceles")
        self.assertEqual(get_triangle_type(5, 4, 5), "isosceles")
        self.assertEqual(get_triangle_type(4, 5, 5), "isosceles")

    def test_nonequilateral_triangle(self):
    # Тестирование разносторонних треугольников
    # Проверка, что функция возвращает "nonequilateral" для разносторонних треугольников
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")
        self.assertEqual(get_triangle_type(5, 6, 7), "nonequilateral")

    def test_invalid_sides_negative(self):
    # Тестирование отрицательных сторон
    # Проверка, что функция вызывает исключение IncorrectTriangleSides при отрицательных сторонах
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 2)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, -1, 1)

    def test_invalid_sides_zero(self):
    # Тестирование нулевых сторон
    # Проверка, что функция вызывает исключение IncorrectTriangleSides при нулевых сторонах
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 2, 2)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 0, 1)

    def test_invalid_triangle_inequality(self):
    # Тестирование нарушения неравенства треугольника
    # Проверка, что функция вызывает исключение IncorrectTriangleSides при нарушении неравенства треугольника
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 1, 3)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(2, 2, 4)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(5, 1, 1)

# Стандартная проверка для запуска тестов при выполнении скрипта
if __name__ == '__main__':
    unittest.main()