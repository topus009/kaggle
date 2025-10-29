#!/usr/bin/env python3
"""
CAPTCHA OCR Prediction Script
Скрипт для предсказания текста на CAPTCHA изображениях
"""

import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import glob

# Настройки модели
IMG_WIDTH = 200
IMG_HEIGHT = 60
MAX_SEQUENCE_LENGTH = 7

def load_model(model_path="output/model.keras"):
    """Загружает обученную модель"""
    try:
        print(f"Загружаем модель из {model_path}...")
        model = keras.models.load_model(model_path)
        print("✓ Модель успешно загружена")
        return model
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return None

def load_char_mappings():
    """Загружает словари символов"""
    # Создаем словари символов (должны совпадать с обучением)
    characters = sorted(set('абвгдежзийклмнопрстуфхцчшщъыьэюя0123456789'))
    char_to_num = {v: i for i, v in enumerate(characters)}
    num_to_char = {str(i): v for i, v in enumerate(characters)}
    num_to_char['-1'] = 'UKN'  # Для CTC декодирования
    
    print(f"Алфавит ({len(characters)} символов): {characters}")
    return char_to_num, num_to_char

def preprocess_image(image_path, img_width=IMG_WIDTH, img_height=IMG_HEIGHT):
    """Предобрабатывает изображение для модели"""
    try:
        # Загружаем изображение
        img = tf.io.read_file(image_path)
        
        # Декодируем (пробуем PNG, затем JPEG)
        try:
            img = tf.io.decode_png(img, channels=3)
        except:
            img = tf.io.decode_jpeg(img, channels=3)
        
        # Конвертируем в float32 и нормализуем
        img = tf.image.convert_image_dtype(img, tf.float32)
        
        # Транспонируем (width, height, channels)
        img = tf.transpose(img, perm=[1, 0, 2])
        
        # Изменяем размер если нужно
        img = tf.image.resize(img, [img_width, img_height])
        
        # Добавляем batch dimension
        img = tf.expand_dims(img, 0)
        
        return img.numpy()
    except Exception as e:
        print(f"❌ Ошибка предобработки изображения {image_path}: {e}")
        return None

def decode_predictions(predictions, num_to_char):
    """Декодирует предсказания модели в текст"""
    # Получаем индексы с максимальной вероятностью
    input_len = np.ones(predictions.shape[0]) * predictions.shape[1]
    results = tf.keras.backend.ctc_decode(predictions, input_length=input_len, greedy=True)[0][0]
    
    # Конвертируем в текст
    texts = []
    for result in results:
        text = ""
        for idx in result:
            if idx != -1:  # -1 означает padding
                char = num_to_char.get(str(idx.numpy()), '')
                if char != 'UKN':
                    text += char
        texts.append(text)
    
    return texts

def predict_single_image(model, image_path, char_to_num, num_to_char):
    """Предсказывает текст для одного изображения"""
    print(f"\n🔍 Анализируем: {os.path.basename(image_path)}")
    
    # Предобрабатываем изображение
    processed_img = preprocess_image(image_path)
    if processed_img is None:
        return None
    
    # Делаем предсказание
    try:
        predictions = model.predict(processed_img, verbose=0)
        predicted_text = decode_predictions(predictions, num_to_char)[0]
        
        print(f"📝 Предсказанный текст: '{predicted_text}'")
        return predicted_text
        
    except Exception as e:
        print(f"❌ Ошибка предсказания: {e}")
        return None

def visualize_prediction(image_path, predicted_text, save_path=None):
    """Визуализирует изображение с предсказанием"""
    try:
        # Загружаем изображение для отображения
        img = Image.open(image_path)
        
        # Создаем фигуру
        plt.figure(figsize=(10, 4))
        plt.imshow(img, cmap='gray')
        plt.title(f"Предсказание: '{predicted_text}'", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            print(f"💾 Результат сохранен в {save_path}")
        
        plt.show()
        
    except Exception as e:
        print(f"❌ Ошибка визуализации: {e}")

def main():
    parser = argparse.ArgumentParser(description='CAPTCHA OCR Prediction')
    parser.add_argument('--image', '-i', type=str, help='Путь к изображению')
    parser.add_argument('--folder', '-f', type=str, help='Папка с изображениями')
    parser.add_argument('--model', '-m', type=str, default='output/model.keras', help='Путь к модели')
    parser.add_argument('--output', '-o', type=str, help='Папка для сохранения результатов')
    parser.add_argument('--show', action='store_true', help='Показать изображения')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔮 CAPTCHA OCR Prediction Script")
    print("=" * 60)
    
    # Загружаем модель
    model = load_model(args.model)
    if model is None:
        return
    
    # Загружаем словари символов
    char_to_num, num_to_char = load_char_mappings()
    
    # Создаем папку для результатов
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Обрабатываем изображения
    if args.image:
        # Одно изображение
        if not os.path.exists(args.image):
            print(f"❌ Файл не найден: {args.image}")
            return
        
        predicted_text = predict_single_image(model, args.image, char_to_num, num_to_char)
        
        if predicted_text and args.show:
            visualize_prediction(args.image, predicted_text)
        
        if predicted_text and args.output:
            output_path = os.path.join(args.output, f"result_{os.path.basename(args.image)}")
            visualize_prediction(args.image, predicted_text, output_path)
    
    elif args.folder:
        # Папка с изображениями
        if not os.path.exists(args.folder):
            print(f"❌ Папка не найдена: {args.folder}")
            return
        
        # Ищем изображения
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(args.folder, ext)))
            image_files.extend(glob.glob(os.path.join(args.folder, ext.upper())))
        
        if not image_files:
            print(f"❌ Изображения не найдены в папке: {args.folder}")
            return
        
        print(f"📁 Найдено {len(image_files)} изображений")
        
        # Обрабатываем каждое изображение
        results = []
        for i, image_path in enumerate(image_files):
            predicted_text = predict_single_image(model, image_path, char_to_num, num_to_char)
            if predicted_text:
                results.append((os.path.basename(image_path), predicted_text))
                
                if args.show:
                    visualize_prediction(image_path, predicted_text)
                
                if args.output:
                    output_path = os.path.join(args.output, f"result_{os.path.basename(image_path)}")
                    visualize_prediction(image_path, predicted_text, output_path)
        
        # Сохраняем результаты в файл
        if args.output and results:
            results_file = os.path.join(args.output, "predictions.txt")
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write("Результаты предсказаний:\n")
                f.write("=" * 40 + "\n")
                for filename, prediction in results:
                    f.write(f"{filename}: {prediction}\n")
            print(f"📄 Результаты сохранены в {results_file}")
    
    else:
        print("❌ Укажите --image или --folder")
        parser.print_help()

if __name__ == "__main__":
    main()