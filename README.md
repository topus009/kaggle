# CAPTCHA OCR Model

Модель для распознавания русских CAPTCHA с использованием CNN-LSTM архитектуры.

## Описание

Этот проект реализует OCR модель для распознавания текста на CAPTCHA изображениях, использующую комбинацию сверточных нейронных сетей (CNN) и долгосрочных краткосрочных сетей памяти (LSTM) с CTC loss.

## Архитектура

- **CNN слои**: Извлечение признаков из изображений
- **Bidirectional LSTM**: Распознавание последовательностей
- **CTC Loss**: Обработка вариативных длин последовательностей

## Требования

```bash
pip install -r requirements.txt
```

## Использование

### Kaggle Notebook

Откройте `captcha_kaggle_adapted.ipynb` в Kaggle и запустите все ячейки.

### Локальный запуск

```bash
python train.py
```

## Структура проекта

```
captcha_ocr_project/
├── captcha_kaggle_adapted.ipynb  # Kaggle ноутбук
├── train.py                       # Python скрипт для локального запуска
├── requirements.txt              # Зависимости
├── .gitignore                    # Git ignore правила
└── output/                       # Выходные файлы (модели, графики)
```

## Выходные файлы

После обучения модель сохраняется в нескольких форматах:
- `output/model.h5` - Keras H5 формат
- `output/model.keras` - Keras формат
- `output/model/` - SavedModel формат
- `output/model.tflite` - TensorFlow Lite (для мобильных устройств)

## Параметры

- **EPOCHS**: 15 эпох обучения
- **BATCH_SIZE**: 16
- **MAX_SEQUENCE_LENGTH**: 7 символов
- **IMG_WIDTH**: 200px
- **IMG_HEIGHT**: 60px

## Лицензия

MIT
