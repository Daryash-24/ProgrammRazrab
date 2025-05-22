# Импорт фреймворка pytest для тестирования
import pytest
# Импорт тестируемого класса Triangle и исключения IncorrectTriangleSides из модуля triangle_class
from triangle_class import Triangle, IncorrectTriangleSides


# Позитивные тесты
def test_equilateral_triangle():
    # Тест равностороннего треугольника
    t = Triangle(5, 5, 5)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 15


def test_isosceles_triangle():
    # Тест равнобедренного треугольника
    t = Triangle(5, 5, 7)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 17


def test_nonequilateral_triangle():
    # Тест разностороннего треугольника
    t = Triangle(3, 4, 5)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 12


def test_float_sides():
    # Тест треугольника с дробными сторонами
    t = Triangle(2.5, 3.5, 4.5)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 10.5


# Негативные тесты
def test_negative_side():
    # Тест отрицательной стороны
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 2)


def test_zero_side():
    # Тест нулевой стороны
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 1, 1)


def test_invalid_sides():
    # Тест некорректных сторон
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 1, 3)

    with pytest.raises(IncorrectTriangleSides):
        Triangle(2, 2, 4)


def test_all_zero_sides():
    # Тест всех нулевых сторон
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 0, 0)