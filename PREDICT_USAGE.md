# 🔮 Использование скрипта предсказаний

## Описание
Скрипт `predict.py` предназначен для тестирования обученной модели CAPTCHA OCR на новых изображениях.

## Требования
- Обученная модель в формате `.keras` (по умолчанию: `output/model.keras`)
- Python 3.7+ с установленными зависимостями из `requirements.txt`

## Установка зависимостей
```bash
pip install -r requirements.txt
```

## Использование

### 1. Предсказание для одного изображения
```bash
python3 predict.py --image path/to/image.png
```

### 2. Предсказание для папки с изображениями
```bash
python3 predict.py --folder path/to/images/
```

### 3. Сохранение результатов
```bash
python3 predict.py --folder data/images --output results/
```

### 4. Показать изображения с предсказаниями
```bash
python3 predict.py --folder data/images --show
```

### 5. Использование другой модели
```bash
python3 predict.py --image test.png --model path/to/your/model.keras
```

## Параметры

- `--image, -i` - путь к одному изображению
- `--folder, -f` - папка с изображениями
- `--model, -m` - путь к модели (по умолчанию: `output/model.keras`)
- `--output, -o` - папка для сохранения результатов
- `--show` - показать изображения с предсказаниями

## Поддерживаемые форматы
- PNG
- JPEG/JPG
- BMP
- TIFF

## Примеры

### Тестирование на тестовых данных
```bash
# Если у вас есть папка data/images с тестовыми CAPTCHA
python3 predict.py --folder data/images --output results --show
```

### Тестирование одного изображения
```bash
python3 predict.py --image my_captcha.png --show
```

## Результаты
- Консольный вывод с предсказанным текстом
- При использовании `--output` - сохранение изображений с подписями
- При использовании `--folder` - файл `predictions.txt` с результатами

## Примечания
- Модель должна быть обучена на том же алфавите символов
- Изображения автоматически масштабируются до 200x60 пикселей
- Поддерживается автоматическое декодирование CTC предсказаний