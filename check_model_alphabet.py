#!/usr/bin/env python3
"""
Скрипт для проверки алфавита обученной модели
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np

def check_model_alphabet(model_path="output/model.keras"):
    """Проверяет алфавит обученной модели"""
    try:
        print(f"🔍 Загружаем модель из {model_path}...")
        model = keras.models.load_model(model_path)
        print("✅ Модель загружена успешно")
        
        # Получаем последний слой (dense с выходными классами)
        last_layer = model.layers[-1]
        print(f"📊 Последний слой: {last_layer.name}")
        print(f"📊 Выходных классов: {last_layer.units}")
        
        # Показываем архитектуру
        print("\n🏗️ Архитектура модели:")
        model.summary()
        
        # Проверяем, есть ли информация об алфавите в метаданных
        if hasattr(model, 'config'):
            config = model.config
            print(f"\n📋 Конфигурация модели:")
            for key, value in config.items():
                if isinstance(value, (list, dict)) and len(str(value)) > 100:
                    print(f"   {key}: {type(value)} (большой объект)")
                else:
                    print(f"   {key}: {value}")
        
        return model
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return None

def analyze_training_data():
    """Анализирует данные, на которых обучалась модель"""
    print("\n📊 Анализ данных обучения...")
    
    # Читаем тестовые данные
    try:
        with open("data/labels.csv", 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Извлекаем все символы
        all_chars = set()
        for line in lines:
            text = line.split(';')[0].strip()
            all_chars.update(text)
        
        characters = sorted(all_chars)
        print(f"📝 Символы в данных: {characters}")
        print(f"📊 Количество символов: {len(characters)}")
        
        # Создаем словари как в обучении
        char_to_num = {v: i for i, v in enumerate(characters)}
        num_to_char = {str(i): v for i, v in enumerate(characters)}
        num_to_char['-1'] = 'UKN'
        
        print(f"📝 Словарь char_to_num: {char_to_num}")
        print(f"📝 Словарь num_to_char: {num_to_char}")
        
        return characters, char_to_num, num_to_char
        
    except Exception as e:
        print(f"❌ Ошибка анализа данных: {e}")
        return None, None, None

def main():
    print("🔍 Проверка алфавита модели")
    print("=" * 40)
    
    # Проверяем модель
    model = check_model_alphabet()
    
    # Анализируем данные
    characters, char_to_num, num_to_char = analyze_training_data()
    
    if model and characters:
        # Сравниваем количество классов
        last_layer_units = model.layers[-1].units
        expected_units = len(characters) + 1  # +1 для CTC blank
        
        print(f"\n🔍 Сравнение:")
        print(f"   Символов в данных: {len(characters)}")
        print(f"   Ожидаемых выходов: {expected_units}")
        print(f"   Фактических выходов: {last_layer_units}")
        
        if last_layer_units == expected_units:
            print("✅ Количество выходов соответствует данным!")
        else:
            print("❌ Несоответствие количества выходов!")
            print("   Возможно, модель обучалась на других данных")
    
    print(f"\n📝 Правильный алфавит для predict.py:")
    if characters:
        print(f"characters = {characters}")
    else:
        print("Не удалось определить алфавит")

if __name__ == "__main__":
    main()