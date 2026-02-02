#!/usr/bin/env python3
"""Проверка линтеров со сбором ВСЕХ ошибок"""
import subprocess
import json
import sys
from pathlib import Path

SCRIPTS = [
    "practice_locators/task1_click.py",
    "practice_locators/task2_form.py",
    "practice_locators/task3_visibility.py",
]

def check_project_exists():
    """Проверка существования папки проекта"""
    project = Path("practice_locators")
    if not project.exists():
        print("❌ Папка practice_locators не найдена!")
        sys.exit(1)
    
    missing = [s for s in SCRIPTS if not Path(s).exists()]
    if missing:
        print("❌ Отсутствуют файлы:")
        for f in missing:
            print(f"   - {f}")
        sys.exit(1)

def run_flake8():
    """Запуск flake8 со сбором ВСЕХ ошибок"""
    result = subprocess.run(
        ["flake8", "--exit-zero", "--max-line-length=88"] + SCRIPTS,
        capture_output=True,
        text=True,
        timeout=30
    )
    errors = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    error_count = len(errors)
    score = max(0, 5 - error_count // 2)  # 1 балл за каждые 2 ошибки
    
    return score, error_count, errors

def run_pylint():
    """Запуск pylint со сбором ВСЕХ критических ошибок"""
    result = subprocess.run(
        ["pylint", "--exit-zero", "--output-format=text", "--score=no",
         "--disable=all", "--enable=E,F,C0301,C0303,W0611,W0612"] + SCRIPTS,
        capture_output=True,
        text=True,
        timeout=30
    )
    errors = [
        line.strip() for line in result.stdout.strip().splitlines()
        if line.strip() and (
            line.startswith("E:") or 
            line.startswith("F:") or 
            "C030" in line or 
            "W0611" in line or
            "W0612" in line
        )
    ]
    error_count = len(errors)
    score = max(0, 5 - error_count)
    
    return score, error_count, errors

def main():
    check_project_exists()
    
    try:
        flake8_score, flake8_errors, flake8_details = run_flake8()
    except Exception as e:
        flake8_score, flake8_errors = 0, 0
        flake8_details = [f"Ошибка запуска flake8: {e}"]
    
    try:
        pylint_score, pylint_errors, pylint_details = run_pylint()
    except Exception as e:
        pylint_score, pylint_errors = 0, 0
        pylint_details = [f"Ошибка запуска pylint: {e}"]
    
    total = flake8_score + pylint_score
    
    # Сохраняем ВСЕ ошибки для отчёта
    with open("linters_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "flake8_score": flake8_score,
            "flake8_errors": flake8_errors,
            "flake8_details": flake8_details,
            "pylint_score": pylint_score,
            "pylint_errors": pylint_errors,
            "pylint_details": pylint_details,
            "total": total
        }, f, ensure_ascii=False, indent=2)
    
    # Вывод в консоль
    print("🔍 Результаты flake8:")
    print(f"   Баллы: {flake8_score}/5")
    print(f"   Ошибок: {flake8_errors}")
    for i, detail in enumerate(flake8_details[:25], 1):
        print(f"   {i}. {detail}")
    if len(flake8_details) > 25:
        print(f"   ... и ещё {len(flake8_details) - 25} ошибок")
    
    print("\n🔍 Результаты pylint:")
    print(f"   Баллы: {pylint_score}/5")
    print(f"   Критических ошибок: {pylint_errors}")
    for i, detail in enumerate(pylint_details[:25], 1):
        print(f"   {i}. {detail}")
    if len(pylint_details) > 25:
        print(f"   ... и ещё {len(pylint_details) - 25} ошибок")
    
    print(f"\n📊 Итого линтеры: {total}/10 баллов")
    return 0 if total >= 5 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        print("   Убедитесь, что все файлы находятся в папке practice_locators/")
        sys.exit(1)