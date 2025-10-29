#!/usr/bin/env python3
"""
Скрипт для подготовки данных для Kaggle
Создает архив с моделью и тестовыми данными для загрузки в Kaggle
"""

import os
import shutil
import zipfile
import argparse
from pathlib import Path

def create_kaggle_package(model_path="output/model.keras", 
                         test_images_path="data/images", 
                         output_dir="kaggle_package"):
    """Создает пакет данных для Kaggle"""
    
    print("📦 Создаем пакет данных для Kaggle...")
    
    # Создаем папку для пакета
    os.makedirs(output_dir, exist_ok=True)
    
    # Создаем структуру папок
    model_dir = os.path.join(output_dir, "model")
    test_dir = os.path.join(output_dir, "test_images")
    
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Копируем модель
    if os.path.exists(model_path):
        shutil.copy2(model_path, model_dir)
        print(f"✅ Модель скопирована: {model_path} -> {model_dir}")
    else:
        print(f"❌ Модель не найдена: {model_path}")
        return False
    
    # Копируем тестовые изображения
    if os.path.exists(test_images_path):
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']:
            image_files.extend(Path(test_images_path).glob(ext))
            image_files.extend(Path(test_images_path).glob(ext.upper()))
        
        if image_files:
            for img_file in image_files:
                shutil.copy2(str(img_file), test_dir)
            print(f"✅ Скопировано {len(image_files)} изображений в {test_dir}")
        else:
            print(f"❌ Изображения не найдены в {test_images_path}")
            return False
    else:
        print(f"❌ Папка с изображениями не найдена: {test_images_path}")
        return False
    
    # Создаем README для Kaggle
    readme_content = """# CAPTCHA OCR Prediction Package

## Содержимое:
- `model/model.keras` - обученная модель CAPTCHA OCR
- `test_images/` - тестовые CAPTCHA изображения

## Как использовать:
1. Загрузите этот архив в Kaggle как dataset
2. Используйте notebook `predict_kaggle.ipynb` для предсказаний
3. Модель автоматически загрузится из `input/model/model.keras`
4. Тестовые изображения должны быть в `input/test_images/`

## Требования:
- TensorFlow 2.x
- Keras
- PIL (Pillow)
- matplotlib
- pandas
- numpy

## Поддерживаемые форматы изображений:
- PNG, JPEG, JPG, BMP, TIFF
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README создан: {readme_path}")
    
    # Создаем ZIP архив
    zip_path = f"{output_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ ZIP архив создан: {zip_path}")
    
    # Показываем размер архива
    zip_size = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"📊 Размер архива: {zip_size:.2f} MB")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Подготовка данных для Kaggle')
    parser.add_argument('--model', '-m', default='output/model.keras', 
                       help='Путь к модели (по умолчанию: output/model.keras)')
    parser.add_argument('--images', '-i', default='data/images', 
                       help='Папка с тестовыми изображениями (по умолчанию: data/images)')
    parser.add_argument('--output', '-o', default='kaggle_package', 
                       help='Папка для выходных данных (по умолчанию: kaggle_package)')
    
    args = parser.parse_args()
    
    print("🚀 Подготовка данных для Kaggle")
    print("=" * 40)
    
    success = create_kaggle_package(args.model, args.images, args.output)
    
    if success:
        print("\n✅ Пакет данных готов!")
        print(f"📁 Папка: {args.output}")
        print(f"📦 Архив: {args.output}.zip")
        print("\n📋 Следующие шаги:")
        print("1. Загрузите архив в Kaggle как dataset")
        print("2. Используйте notebook predict_kaggle.ipynb")
        print("3. Укажите правильные пути в notebook")
    else:
        print("\n❌ Ошибка при создании пакета данных")

if __name__ == "__main__":
    main()