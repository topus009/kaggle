#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real CAPTCHA Tester
Скрипт для загрузки реальных CAPTCHA с FSSP API,
сохранения их и тестирования модели на предсказание
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime
import subprocess
import time

# Настройки
API_URL = "https://is.fssp.gov.ru/refresh_visual_captcha/"
CAPTCHA_FOLDER = "test_captchas"
RESULTS_FOLDER = "real_results"

def create_folders():
    """Создает необходимые папки"""
    os.makedirs(CAPTCHA_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    print(f"[OK] Папки созданы: {CAPTCHA_FOLDER}, {RESULTS_FOLDER}")

def fetch_captcha(count=5):
    """Загружает CAPTCHA с FSSP API"""
    print(f"\n[*] Загружаем {count} CAPTCHA с FSSP API...")
    
    # Заголовки для имитации браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://is.fssp.gov.ru/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    saved_files = []
    
    for i in range(count):
        try:
            # Параметры запроса
            params = {
                'callback': f'callback_{int(time.time() * 1000)}',
                '_': str(int(time.time() * 1000))
            }
            
            # Делаем запрос с заголовками
            response = requests.get(API_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Парсим ответ (JSONP)
            text = response.text
            
            # Извлекаем JSON из JSONP callback
            # Формат: callback_123({...})
            if '({' in text:
                json_str = text[text.index('({') + 1:text.rindex('})') + 1]
            else:
                json_str = text
            
            data = json.loads(json_str)
            
            # Проверяем наличие поля image
            if 'image' not in data:
                print(f"[ERROR] Ответ {i+1}: нет поля 'image' в ответе")
                print(f"[DEBUG] Доступные поля: {list(data.keys())}")
                continue
            
            # Декодируем base64 изображение
            image_data = data['image']
            
            # Удаляем префикс data:image если он есть
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Декодируем base64
            image_bytes = base64.b64decode(image_data)
            
            # Сохраняем файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"captcha_{timestamp}_{i+1}.png"
            filepath = os.path.join(CAPTCHA_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            saved_files.append(filepath)
            print(f"[OK] CAPTCHA {i+1}: сохранена в {filepath}")
            
            # Небольшая задержка между запросами
            if i < count - 1:
                time.sleep(0.5)
        
        except Exception as e:
            print(f"[ERROR] Ошибка при загрузке CAPTCHA {i+1}: {e}")
            continue
    
    return saved_files

def test_captchas(captcha_files, output_folder='real_results'):
    """Тестирует загруженные CAPTCHA с помощью predict.py"""
    if not captcha_files:
        print("[ERROR] Нет CAPTCHA для тестирования")
        return
    
    print(f"\n[*] Тестируем {len(captcha_files)} CAPTCHA...")
    print("=" * 60)
    
    # Запускаем predict.py
    cmd = [
        'python',
        'predict.py',
        '--folder', CAPTCHA_FOLDER,
        '--output', output_folder
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Выводим результат
        print(result.stdout)
        
        if result.stderr:
            print("[STDERR]")
            print(result.stderr)
        
        # Читаем результаты из файла predictions.txt
        predictions_file = os.path.join(output_folder, "predictions.txt")
        if os.path.exists(predictions_file):
            print("\n" + "=" * 60)
            print("РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЙ:")
            print("=" * 60)
            with open(predictions_file, 'r', encoding='utf-8') as f:
                print(f.read())
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout при выполнении predict.py")
    except Exception as e:
        print(f"[ERROR] Ошибка при запуске predict.py: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real CAPTCHA Tester - FSSP API Integration')
    parser.add_argument('--count', '-c', type=int, default=5, help='Количество CAPTCHA для загрузки (по умолчанию 5)')
    parser.add_argument('--no-test', action='store_true', help='Только загрузить CAPTCHA без тестирования')
    parser.add_argument('--captcha-folder', default='test_captchas', help='Папка для сохранения CAPTCHA')
    parser.add_argument('--output-folder', default='real_results', help='Папка для результатов')
    
    args = parser.parse_args()
    
    # Используем переданные значения если указаны аргументы
    captcha_folder = args.captcha_folder
    output_folder = args.output_folder
    count = args.count
    
    print("=" * 60)
    print("*** Real CAPTCHA Tester ***")
    print("*** FSSP API Integration ***")
    print("=" * 60)
    
    # Создаем папки
    os.makedirs(captcha_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    print(f"[OK] Папки созданы: {captcha_folder}, {output_folder}")
    
    # Если нет аргументов командной строки, спросить у пользователя
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        try:
            count = int(input("\n[?] Сколько CAPTCHA загрузить? (по умолчанию 5): ") or "5")
            if count < 1:
                count = 5
        except ValueError:
            count = 5
    
    # Загружаем CAPTCHA
    print(f"\n[*] Загружаем {count} CAPTCHA с FSSP API...")
    
    # Используем глобальные переменные в fetch_captcha
    captcha_files = fetch_captcha(count)
    
    if not captcha_files:
        print("[ERROR] Не удалось загрузить ни одну CAPTCHA")
        return
    
    print(f"\n[OK] Успешно загружено {len(captcha_files)} CAPTCHA")
    
    # Тестируем CAPTCHA если не указан флаг --no-test
    if not args.no_test:
        test_captchas(captcha_files, output_folder)
    
    print("\n" + "=" * 60)
    print("[OK] Обработка завершена!")
    print(f"[INFO] CAPTCHA сохранены в: {captcha_folder}")
    if not args.no_test:
        print(f"[INFO] Результаты в: {output_folder}")
    print("=" * 60)

if __name__ == "__main__":
    main()
