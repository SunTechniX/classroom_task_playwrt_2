"""Статический анализ синтаксиса и логики"""
import ast
import re
from pathlib import Path
import pytest

PROJECT_ROOT = Path("practice_locators")

def parse_python_file(filepath):
    """Парсинг файла через AST без выполнения"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return ast.parse(content, filename=str(filepath)), content
    except SyntaxError as e:
        pytest.fail(f"❌ Синтаксическая ошибка в {filepath.name}: {e.msg} (строка {e.lineno})")
    except FileNotFoundError:
        pytest.fail(f"❌ Файл {filepath.name} не найден")
    except Exception as e:
        pytest.fail(f"❌ Ошибка чтения {filepath.name}: {e}")

def has_sync_playwright_import(tree):
    """Проверка импорта sync_playwright"""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "playwright.sync_api":
            if any(alias.name == "sync_playwright" for alias in node.names):
                return True
    return False

def has_playwright_imports(tree):
    """Проверка импорта всех необходимых модулей"""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "playwright.sync_api":
            imports.extend([alias.name for alias in node.names])
    return imports

def has_click_method(code):
    """Проверка наличия метода .click()"""
    return bool(re.search(r'\.click\(\)', code))

def has_locator_method(code, method_name):
    """Проверка использования метода локатора"""
    pattern = rf'\.{method_name}\('
    return bool(re.search(pattern, code))

def has_expect_visible(code):
    """Проверка использования expect().to_be_visible()"""
    return bool(re.search(r'expect.*\.to_be_visible\(\)', code))

def has_clear_method(code):
    """Проверка использования метода .clear()"""
    return bool(re.search(r'\.clear\(\)', code))

# === Тесты для Задания 1 ===

@pytest.mark.syntax
def test_task1_imports():
    tree, _ = parse_python_file(PROJECT_ROOT / "task1_click.py")
    assert has_sync_playwright_import(tree), "❌ Отсутствует импорт sync_playwright"

@pytest.mark.syntax
def test_task1_locators():
    _, code = parse_python_file(PROJECT_ROOT / "task1_click.py")
    # Проверка использования разных способов поиска
    has_text = bool(re.search(r'get_by_text|text=', code))
    has_css = bool(re.search(r'locator\("#home"\)', code))
    has_role = bool(re.search(r'get_by_role', code))
    
    assert has_text or has_css or has_role, \
        "❌ Не найдено использование хотя бы одного способа поиска элемента (text, CSS, role)"

@pytest.mark.syntax
def test_task1_button_click():
    _, code = parse_python_file(PROJECT_ROOT / "task1_click.py")
    assert has_click_method(code), "❌ Не найден метод .click() для кнопки"

# === Тесты для Задания 2 ===

@pytest.mark.syntax
def test_task2_imports():
    tree, _ = parse_python_file(PROJECT_ROOT / "task2_form.py")
    assert has_sync_playwright_import(tree), "❌ Отсутствует импорт sync_playwright"

@pytest.mark.syntax
def test_task2_form_locators():
    _, code = parse_python_file(PROJECT_ROOT / "task2_form.py")
    # Проверка использования разных способов поиска поля ввода
    has_placeholder = bool(re.search(r'get_by_placeholder\(["\']Enter name["\']\)', code))
    has_css = bool(re.search(r'locator\("#fullName"\)', code))
    
    assert has_placeholder or has_css, \
        "❌ Не найдено использование метода поиска поля ввода (placeholder или CSS)"

@pytest.mark.syntax
def test_task2_clear():
    _, code = parse_python_file(PROJECT_ROOT / "task2_form.py")
    assert has_clear_method(code), "❌ Не найден метод .clear() для очистки поля"

# === Тесты для Задания 3 ===

@pytest.mark.syntax
def test_task3_imports():
    tree, _ = parse_python_file(PROJECT_ROOT / "task3_visibility.py")
    imports = has_playwright_imports(tree)
    assert "expect" in imports, "❌ Отсутствует импорт 'expect' из playwright.sync_api"

@pytest.mark.syntax
def test_task3_expect_visible():
    _, code = parse_python_file(PROJECT_ROOT / "task3_visibility.py")
    assert has_expect_visible(code), \
        "❌ Не найдено использование expect().to_be_visible() для проверки видимости"