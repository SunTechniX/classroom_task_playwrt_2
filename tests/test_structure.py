"""Проверка структуры проекта"""
import pytest
from pathlib import Path

PROJECT_ROOT = Path("practice_locators")
REQUIRED_FILES = [
    "task1_click.py",
    "task2_form.py",
    "task3_visibility.py",
]

@pytest.mark.structure
def test_project_folder_exists():
    """Папка practice_locators существует"""
    assert PROJECT_ROOT.exists(), "❌ Папка practice_locators отсутствует"
    assert PROJECT_ROOT.is_dir(), "❌ practice_locators не является папкой"

@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_required_file_exists(filename):
    """Все обязательные файлы присутствуют"""
    filepath = PROJECT_ROOT / filename
    assert filepath.exists(), f"❌ Файл {filename} отсутствует"
    assert filepath.is_file(), f"❌ {filename} не является файлом"