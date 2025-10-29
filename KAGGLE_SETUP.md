# 🚀 Настройка для Kaggle

## Описание
Этот набор файлов позволяет запустить предсказания CAPTCHA OCR на Kaggle с использованием обученной модели.

## Файлы

### 1. `predict_kaggle.ipynb` - Основной notebook для Kaggle
- Загружает модель из `input/model.keras`
- Обрабатывает изображения из `input/test_images/`
- Сохраняет результаты в `output/`
- Показывает визуализацию предсказаний

### 2. `prepare_kaggle_data.py` - Скрипт подготовки данных
- Создает архив с моделью и тестовыми данными
- Готовит структуру для загрузки в Kaggle

## 📋 Пошаговая инструкция

### Шаг 1: Подготовка данных
```bash
# Создаем пакет данных для Kaggle
python3 prepare_kaggle_data.py

# Или с кастомными путями
python3 prepare_kaggle_data.py --model output/model.keras --images data/images --output my_kaggle_package
```

### Шаг 2: Загрузка в Kaggle
1. Зайдите на [Kaggle Datasets](https://www.kaggle.com/datasets)
2. Нажмите "New Dataset"
3. Загрузите созданный архив `kaggle_package.zip`
4. Назовите dataset (например: "captcha-ocr-model-and-test-data")

### Шаг 3: Создание Kaggle Notebook
1. Зайдите на [Kaggle Notebooks](https://www.kaggle.com/code)
2. Нажмите "New Notebook"
3. В настройках:
   - **Internet**: ON (для установки зависимостей)
   - **GPU**: ON (опционально, для ускорения)
4. Загрузите `predict_kaggle.ipynb` или скопируйте код

### Шаг 4: Настройка путей в notebook
В ячейке с настройками измените пути:
```python
# Пути к данным (адаптируйте под ваш dataset)
MODEL_PATH = "/kaggle/input/your-dataset-name/model/model.keras"
TEST_IMAGES_PATH = "/kaggle/input/your-dataset-name/test_images/"
```

### Шаг 5: Запуск
1. Запустите все ячейки notebook
2. Результаты сохранятся в `/kaggle/working/predictions/`
3. Скачайте результаты из папки output

## 📁 Структура данных для Kaggle

```
kaggle_package/
├── README.md
├── model/
│   └── model.keras          # Обученная модель
└── test_images/             # Тестовые CAPTCHA
    ├── captcha_001.png
    ├── captcha_002.png
    └── ...
```

## 🔧 Настройки notebook

### Пути к данным
```python
MODEL_PATH = "/kaggle/input/your-dataset-name/model/model.keras"
TEST_IMAGES_PATH = "/kaggle/input/your-dataset-name/test_images/"
OUTPUT_PATH = "/kaggle/working/predictions/"
```

### Параметры модели
```python
IMG_WIDTH = 200
IMG_HEIGHT = 60
MAX_SEQUENCE_LENGTH = 7
```

## 📊 Результаты

Notebook создает:
- `predictions.csv` - таблица с результатами
- `predictions.txt` - текстовый файл с результатами  
- `result_*.png` - изображения с предсказаниями
- Статистику точности и примеры

## 🚨 Возможные проблемы

### 1. Модель не загружается
- Проверьте путь к модели в `MODEL_PATH`
- Убедитесь, что файл `model.keras` загружен в dataset

### 2. Изображения не найдены
- Проверьте путь к изображениям в `TEST_IMAGES_PATH`
- Убедитесь, что папка `test_images` загружена в dataset

### 3. Ошибки предсказания
- Проверьте совместимость версий TensorFlow
- Убедитесь, что модель обучена на том же алфавите

## 💡 Советы

1. **Производительность**: Включите GPU для ускорения предсказаний
2. **Память**: Для больших датасетов увеличьте лимит памяти
3. **Результаты**: Скачайте результаты до истечения времени сессии
4. **Отладка**: Используйте первые несколько изображений для тестирования

## 🔗 Полезные ссылки

- [Kaggle Notebooks](https://www.kaggle.com/code)
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [TensorFlow на Kaggle](https://www.kaggle.com/docs/efficient-gpu-usage)