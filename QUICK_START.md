# ��� Быстрый старт

## За 30 секунд до первого результата

### 1️⃣ Локальное тестирование
```bash
python predict.py --folder images/images --output results
cat results/predictions.txt
```

### 2️⃣ Тестирование на реальных CAPTCHA
```bash
python test_real_captcha.py --count 5
cat real_results/predictions.txt
```

## Примеры команд

### Загрузить 10 CAPTCHA с FSSP API
```bash
python test_real_captcha.py --count 10
```

### Загрузить CAPTCHA без тестирования
```bash
python test_real_captcha.py --count 20 --no-test
```

### Тестировать одно изображение
```bash
python predict.py --image path/to/image.png --output results
```

### С пользовательскими папками
```bash
python test_real_captcha.py --count 5 --captcha-folder mycaptchas --output-folder myresults
```

## Результаты

Все результаты сохраняются в `predictions.txt`:
- Имя файла
- Предсказанный текст

```
captcha_20251029_234905_164_1.png: б8м6ж
captcha_20251029_234906_140_2.png: лгвжг
```

## Системные требования

- Python 3.8+
- 500 MB RAM
- Интернет для загрузки CAPTCHA с API

## Проблемы?

- Убедитесь что модель есть в `final-results/output/model.keras`
- Проверьте что установлены все зависимости: `pip install -r requirements.txt`
- Проверьте интернет при использовании FSSP API

