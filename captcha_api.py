#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAPTCHA OCR REST API
Flask сервер для предсказания текста на CAPTCHA изображениях.
Может быть вызван из Node.js или любого другого приложения через HTTP.

Использование:
    python captcha_api.py --host 0.0.0.0 --port 5000
    
    Затем вызывать через HTTP:
    curl -X POST -F "image=@test.png" http://localhost:5000/predict
"""

import os
import sys
import json
import base64
import argparse
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки модели
IMG_WIDTH = 200
IMG_HEIGHT = 60
MAX_SEQUENCE_LENGTH = 7
MODEL_PATH = "final-results/output/model.keras"
LABELS_PATH = "images/labels.csv"

app = Flask(__name__)
CORS(app)  # Разрешить CORS для запросов с других серверов

# Глобальные переменные для кеша
model = None
char_to_num = None
num_to_char = None

def load_model_weights():
    """Загружает модель и словари символов"""
    global model, char_to_num, num_to_char
    
    try:
        logger.info(f"Загружаем модель из {MODEL_PATH}...")
        model = keras.models.load_model(MODEL_PATH)
        logger.info("✓ Модель загружена успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки модели: {e}")
        raise
    
    # Загружаем словари символов
    try:
        logger.info(f"Определяем алфавит из {LABELS_PATH}...")
        with open(LABELS_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        all_chars = set()
        for line in lines:
            text = line.split(';')[0].strip()
            all_chars.update(text)
        
        characters = sorted(all_chars)
        char_to_num = {v: i for i, v in enumerate(characters)}
        num_to_char = {str(i): v for i, v in enumerate(characters)}
        num_to_char['-1'] = 'UKN'
        
        logger.info(f"✓ Алфавит загружен: {len(characters)} символов")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки словарей: {e}")
        raise

def preprocess_image(image_data, img_width=IMG_WIDTH, img_height=IMG_HEIGHT):
    """Предобрабатывает изображение для модели"""
    try:
        # Если это bytes, декодируем
        if isinstance(image_data, bytes):
            img = tf.io.decode_image(image_data, channels=3)
        else:
            # Если это PIL Image
            img = tf.convert_to_tensor(np.array(image_data))
        
        # Конвертируем в float32
        img = tf.image.convert_image_dtype(img, tf.float32)
        
        # Транспонируем (width, height, channels)
        img = tf.transpose(img, perm=[1, 0, 2])
        
        # Изменяем размер
        img = tf.image.resize(img, [img_width, img_height])
        
        # Добавляем batch dimension
        img = tf.expand_dims(img, 0)
        
        return img.numpy()
    except Exception as e:
        logger.error(f"❌ Ошибка предобработки изображения: {e}")
        raise

def decode_predictions(predictions):
    """Декодирует предсказания модели в текст"""
    try:
        input_len = np.ones(predictions.shape[0]) * predictions.shape[1]
        results = tf.keras.backend.ctc_decode(predictions, input_length=input_len, greedy=True)[0][0]
        
        texts = []
        for result in results:
            text = ""
            for idx in result:
                if idx != -1:
                    char = num_to_char.get(str(idx.numpy()), '')
                    if char != 'UKN':
                        text += char
            texts.append(text)
        
        return texts
    except Exception as e:
        logger.error(f"❌ Ошибка декодирования: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'version': '1.0'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Основной endpoint для предсказания"""
    try:
        # Проверяем что модель загружена
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Получаем изображение - 3 варианта
        image_data = None
        
        # Вариант 1: загруженный файл
        if 'image' in request.files:
            image_file = request.files['image']
            image_data = image_file.read()
            logger.info(f"Получено изображение: {image_file.filename} ({len(image_data)} bytes)")
        
        # Вариант 2: base64 в JSON
        elif request.is_json:
            data = request.get_json()
            if 'image' in data:
                image_b64 = data['image']
                # Удаляем префикс data:image если он есть
                if ',' in image_b64:
                    image_b64 = image_b64.split(',')[1]
                image_data = base64.b64decode(image_b64)
                logger.info(f"Получено base64 изображение ({len(image_data)} bytes)")
        
        if image_data is None:
            return jsonify({'error': 'No image provided'}), 400
        
        # Предобрабатываем изображение
        processed_img = preprocess_image(image_data)
        
        # Делаем предсказание
        predictions = model.predict(processed_img, verbose=0)
        predicted_texts = decode_predictions(predictions)
        predicted_text = predicted_texts[0] if predicted_texts else ""
        
        logger.info(f"Предсказание: '{predicted_text}'")
        
        return jsonify({
            'success': True,
            'prediction': predicted_text,
            'confidence': float(np.max(predictions))
        })
    
    except Exception as e:
        logger.error(f"❌ Ошибка: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """Batch endpoint для множества изображений"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        if not request.is_json:
            return jsonify({'error': 'JSON expected'}), 400
        
        data = request.get_json()
        if 'images' not in data or not isinstance(data['images'], list):
            return jsonify({'error': 'images array expected'}), 400
        
        results = []
        for i, image_b64 in enumerate(data['images']):
            try:
                # Удаляем префикс если есть
                if ',' in image_b64:
                    image_b64 = image_b64.split(',')[1]
                
                image_data = base64.b64decode(image_b64)
                processed_img = preprocess_image(image_data)
                predictions = model.predict(processed_img, verbose=0)
                predicted_texts = decode_predictions(predictions)
                
                results.append({
                    'index': i,
                    'prediction': predicted_texts[0] if predicted_texts else "",
                    'success': True
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'success': False
                })
        
        logger.info(f"Batch обработка: {len(data['images'])} изображений")
        return jsonify({
            'success': True,
            'total': len(data['images']),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"❌ Ошибка batch: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/info', methods=['GET'])
def info():
    """Информация о модели и API"""
    return jsonify({
        'name': 'CAPTCHA OCR API',
        'version': '1.0',
        'description': 'REST API for CAPTCHA text recognition',
        'model': {
            'path': MODEL_PATH,
            'image_size': [IMG_HEIGHT, IMG_WIDTH],
            'max_sequence_length': MAX_SEQUENCE_LENGTH,
            'accuracy_kaggle': '95%'
        },
        'endpoints': {
            'GET /health': 'Проверка статуса',
            'GET /info': 'Информация об API',
            'POST /predict': 'Предсказание для одного изображения',
            'POST /predict-batch': 'Batch предсказание для множества изображений'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def main():
    parser = argparse.ArgumentParser(description='CAPTCHA OCR REST API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("*** CAPTCHA OCR REST API Server ***")
    print("=" * 60)
    
    # Загружаем модель при старте
    try:
        load_model_weights()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)
    
    print(f"\n[*] Запускаем сервер на {args.host}:{args.port}")
    print(f"[*] Debug mode: {args.debug}")
    print(f"[*] Доступно на: http://{args.host}:{args.port}")
    print(f"[*] Информация: http://{args.host}:{args.port}/info")
    print(f"[*] Health check: http://{args.host}:{args.port}/health")
    print("\n" + "=" * 60)
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
