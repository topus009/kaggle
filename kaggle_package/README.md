# CAPTCHA OCR Prediction Package

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
