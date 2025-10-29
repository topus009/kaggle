# CAPTCHA OCR - Kaggle CAPTCHA Recognition Model

Полнофункциональное решение для предсказания текста на CAPTCHA изображениях с использованием TensorFlow и Keras.

## 📊 Производительность

- **Accuracy на Kaggle**: 95%
- **Скорость обработки**: ~0.1-0.2 сек на изображение
- **Поддерживаемые символы**: Русские буквы и цифры
- **Модель**: CTC-based LSTM Neural Network

## 📁 Структура проекта

```
kaggle/
├── final-results/output/
│   └── model.keras              # Обученная модель (95% accuracy)
├── images/                       # Тестовые данные
│   ├── labels.csv              # Метки для тестирования
│   └── images/                 # Изображения CAPTCHA
├── predict.py                  # Скрипт для предсказания
├── test_real_captcha.py        # Скрипт для загрузки и тестирования реальных CAPTCHA
├── requirements.txt            # Зависимости Python
└── README.md                   # Этот файл
```

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Предсказание на локальном изображении
```bash
# Одно изображение
python predict.py --image path/to/image.png --output results

# Папка с изображениями
python predict.py --folder path/to/images --output results
```

### 3. Тестирование на реальных CAPTCHA с FSSP API
```bash
# Загрузить 5 CAPTCHA и протестировать
python test_real_captcha.py --count 5

# Только загрузить без тестирования
python test_real_captcha.py --count 10 --no-test

# С пользовательскими папками
python test_real_captcha.py --count 5 --captcha-folder mycaptchas --output-folder myresults
```

## 📝 Скрипты

### predict.py
Основной скрипт для предсказания текста на CAPTCHA.

**Использование:**
```bash
python predict.py --folder images/images --output results
```

**Аргументы:**
- `--image, -i` - Путь к одному изображению
- `--folder, -f` - Папка с изображениями
- `--model, -m` - Путь к модели (по умолчанию: `final-results/output/model.keras`)
- `--output, -o` - Папка для сохранения результатов

**Выход:**
- Результаты сохраняются в `{output_folder}/predictions.txt`
- Также сохраняются изображения с предсказанием в `{output_folder}/`

### test_real_captcha.py
Скрипт для загрузки реальных CAPTCHA с FSSP API и их тестирования.

**Использование:**
```bash
python test_real_captcha.py --count 5
```

**Аргументы:**
- `--count, -c` - Количество CAPTCHA для загрузки (по умолчанию: 5)
- `--no-test` - Только загрузить, без тестирования
- `--captcha-folder` - Папка для сохранения CAPTCHA (по умолчанию: `test_captchas`)
- `--output-folder` - Папка для результатов (по умолчанию: `real_results`)

**Процесс:**
1. Подключается к FSSP API
2. Загружает CAPTCHA в формате base64
3. Декодирует и сохраняет как PNG
4. Запускает predict.py для предсказания
5. Сохраняет результаты в текстовый файл

## 📊 Результаты

Результаты сохраняются в файл `predictions.txt`:

```
============================================================
РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЙ CAPTCHA
============================================================

Обработано изображений: 6
------------------------------------------------------------

captcha_20251029_234905_164_1.png: б8м6ж
captcha_20251029_234906_140_2.png: лгвжг
captcha_20251029_234957_481_1.png: 2вн45
captcha_20251029_234958_328_2.png: в89с5р
captcha_20251029_235008_239_1.png: сн2лп
captcha_20251029_235009_073_2.png: мрж6гс

============================================================
```

## 🔧 Требования

- Python 3.8+
- TensorFlow >= 2.10.0
- NumPy >= 1.23.0
- Requests >= 2.28.0
- Pillow >= 9.5.0
- OpenCV >= 4.6.0

Все зависимости указаны в `requirements.txt`

## 📂 Папки (в .gitignore)

- `results/` - Результаты локального тестирования
- `test_captchas/` - Загруженные реальные CAPTCHA
- `real_results/` - Результаты на реальных CAPTCHA

## 🔗 API FSSP

Используемый API для загрузки реальных CAPTCHA:
- **Endpoint**: `https://is.fssp.gov.ru/refresh_visual_captcha/`
- **Метод**: GET (JSONP)
- **Формат ответа**: JSONP с base64 encoded PNG изображением в поле `image`

## 💡 Примеры

### Пример 1: Протестировать модель на локальных данных
```bash
python predict.py --folder images/images --output results
cat results/predictions.txt
```

### Пример 2: Загрузить 10 реальных CAPTCHA и протестировать
```bash
python test_real_captcha.py --count 10
cat real_results/predictions.txt
```

### Пример 3: Только загрузить CAPTCHA без тестирования
```bash
python test_real_captcha.py --count 20 --no-test
# CAPTCHA сохранены в test_captchas/
```

## 📋 Примечания

- Модель обучена на русскоязычных CAPTCHA (буквы и цифры)
- Максимальная длина текста: 7 символов
- Размер изображения: 200x60 пикселей
- Используется CTC loss для обучения и CTC декодирование для предсказания
- Скрипты не требуют GUI - все результаты в текстовых файлах

## ⚙️ Архитектура модели

- **Input**: Изображение 200x60 RGB
- **Preprocessing**: Нормализация, транспонирование
- **Architecture**: LSTM-based CNN
- **Output**: CTC-decoded текст (переменная длина)
- **Loss**: CTC Loss (Connectionist Temporal Classification)

## 🎯 Результаты на реальных CAPTCHA

На реальных CAPTCHA с FSSP API модель показывает хорошие результаты:
- Правильно распознает большинство символов
- Справляется с различными стилями написания
- Консистентные предсказания

## 📄 Лицензия

Этот проект создан в образовательных целях.

## 👨‍💻 Технологический стек

- **Framework**: TensorFlow / Keras
- **Language**: Python 3.11+
- **API Client**: Requests
- **Image Processing**: OpenCV, Pillow
- **Data Processing**: NumPy, Pandas
