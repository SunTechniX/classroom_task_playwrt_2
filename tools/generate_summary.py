#!/usr/bin/env python3
"""Генератор отчёта с объединённой таблицей статусов"""
import subprocess
import sys
import re
import os
import json

def run_pytest():
    """Запуск тестов и возврат вывода"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--color=no"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    return result.stdout, result.stderr, result.returncode

def parse_pytest_output(stdout):
    """Парсинг вывода pytest: статус каждого файла"""
    file_status = {
        "task1_click.py": False,
        "task2_form.py": False,
        "task3_visibility.py": False,
    }
    
    # Проверяем тесты синтаксиса
    pattern = r"tests/test_syntax\.py::test_(\w+)\s+(PASSED|FAILED)"
    matches = re.findall(pattern, stdout, re.MULTILINE)
    
    for test_name, status in matches:
        if "task1" in test_name:
            file_status["task1_click.py"] = (status == "PASSED")
        elif "task2" in test_name:
            file_status["task2_form.py"] = (status == "PASSED")
        elif "task3" in test_name:
            file_status["task3_visibility.py"] = (status == "PASSED")
    
    return file_status

def check_project_structure():
    """Проверка наличия файлов"""
    project = os.path.join(os.getcwd(), "practice_locators")
    if not os.path.isdir(project):
        return False, None
    
    files = {
        "task1_click.py": os.path.isfile(os.path.join(project, "task1_click.py")),
        "task2_form.py": os.path.isfile(os.path.join(project, "task2_form.py")),
        "task3_visibility.py": os.path.isfile(os.path.join(project, "task3_visibility.py")),
    }
    return True, files

def load_linter_results():
    """Загрузка результатов линтеров"""
    try:
        with open("linters_result.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    # 1. Проверка структуры
    structure_ok, structure_files = check_project_structure()
    
    # 2. Запуск тестов
    pytest_out, _, _ = run_pytest()
    
    # 3. Парсинг результатов
    syntax_status = parse_pytest_output(pytest_out)
    
    # 4. Формируем общий статус для каждого файла
    file_summary = {}
    for fname in ["task1_click.py", "task2_form.py", "task3_visibility.py"]:
        exists = structure_files.get(fname, False) if structure_files else False
        passed = syntax_status.get(fname, False)
        
        if not exists:
            file_summary[fname] = {
                "status": "❌ отсутствует",
                "reason": "Файл не найден"
            }
        elif exists and passed:
            file_summary[fname] = {
                "status": "✅ пройден",
                "reason": "Файл существует и прошёл проверку"
            }
        else:
            file_summary[fname] = {
                "status": "⚠️ требует исправления",
                "reason": "Файл существует, но проверка упала"
            }
    
    # 5. Загрузка линтеров
    linters = load_linter_results()
    
    # === ФОРМИРОВАНИЕ ОТЧЁТА ===
    report = []
    report.append("# 📊 Автопроверка задания: Практика по локаторам")
    report.append("")
    
    # Объединённая таблица статусов
    report.append("## 📁 Структура и результаты проверки")
    report.append("")
    report.append("| Файл | Статус | Причина |")
    report.append("|------|--------|---------|")
    for fname, data in file_summary.items():
        report.append(f"| `{fname}` | {data['status']} | {data['reason']} |")
    report.append("")
    
    # Ошибки линтеров
    if linters:
        report.append("## 🔍 Ошибки линтеров")
        report.append("")
        report.append(f"**flake8:** {linters['flake8_score']}/5 баллов ({linters['flake8_errors']} ошибок)")
        if linters['flake8_errors'] > 0:
            for i, err in enumerate(linters['flake8_details'][:15], 1):
                report.append(f"  {i}. `{err}`")
        report.append("")
        report.append(f"**pylint:** {linters['pylint_score']}/5 баллов ({linters['pylint_errors']} ошибок)")
        if linters['pylint_errors'] > 0:
            for i, err in enumerate(linters['pylint_details'][:15], 1):
                report.append(f"  {i}. `{err}`")
        report.append("")
    
    # Итог
    report.append("## 🏆 Итоговая оценка")
    report.append("")
    if not structure_ok:
        report.append("❌ **РАБОТА НЕ ПРИНЯТА** — отсутствует папка `practice_locators`")
        exit_code = 1
    elif any("требует исправления" in data["status"] for data in file_summary.values()):
        report.append("⚠️ **ДОРАБОТКА** — некоторые файлы не прошли проверку")
        exit_code = 1
    else:
        report.append("✅ **ЗАЧЁТ** — все файлы присутствуют и прошли проверку")
        if linters and linters['total'] >= 5:
            report.append("✅ Стиль кода соответствует требованиям")
        else:
            report.append("💡 Рекомендуется исправить замечания линтеров")
        exit_code = 0
    
    report.append("")
    report.append("> 💡 Задание на уроке (30-40 минут). Основной фокус — корректное использование локаторов.")
    
    # Сохранение
    summary_text = "\n".join(report)
    github_summary = os.getenv("GITHUB_STEP_SUMMARY")
    
    if github_summary and os.path.exists(github_summary):
        with open(github_summary, "w", encoding="utf-8") as f:
            f.write(summary_text)
    else:
        with open("SUMMARY.md", "w", encoding="utf-8") as f:
            f.write(summary_text)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()