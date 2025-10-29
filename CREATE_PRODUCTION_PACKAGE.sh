#!/bin/bash
# Скрипт для создания production package

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Создание Production Package для CAPTCHA OCR                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Настройки
PRODUCTION_DIR="production"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="captcha_ocr_production_${TIMESTAMP}.tar.gz"

echo ""
echo "[*] Создаем структуру директорий..."
mkdir -p "$PRODUCTION_DIR/python_api/models"
mkdir -p "$PRODUCTION_DIR/nodejs_client"
mkdir -p "$PRODUCTION_DIR/config"
mkdir -p "$PRODUCTION_DIR/docs"

echo "[*] Копируем Python файлы..."
cp captcha_api.py "$PRODUCTION_DIR/python_api/" || echo "[ERROR] captcha_api.py не найден"
cp requirements.txt "$PRODUCTION_DIR/python_api/" || echo "[ERROR] requirements.txt не найден"

echo "[*] Копируем модель и метки..."
if [ -f "final-results/output/model.keras" ]; then
    cp "final-results/output/model.keras" "$PRODUCTION_DIR/python_api/models/"
    echo "[OK] Модель скопирована"
else
    echo "[ERROR] Модель не найдена в final-results/output/model.keras"
fi

if [ -f "images/labels.csv" ]; then
    cp "images/labels.csv" "$PRODUCTION_DIR/python_api/models/"
    echo "[OK] Labels.csv скопирован"
else
    echo "[ERROR] Labels.csv не найден в images/labels.csv"
fi

echo "[*] Копируем Node.js файлы..."
cp captcha_client_nodejs.js "$PRODUCTION_DIR/nodejs_client/" || echo "[ERROR] captcha_client_nodejs.js не найден"
cp package.json "$PRODUCTION_DIR/nodejs_client/" || echo "[ERROR] package.json не найден"
cp captcha_solver_example.js "$PRODUCTION_DIR/nodejs_client/" 2>/dev/null || echo "[!] captcha_solver_example.js (optional)"

echo "[*] Копируем документацию..."
cp LINUX_DEPLOYMENT.md "$PRODUCTION_DIR/docs/DEPLOYMENT.md" 2>/dev/null || echo "[!] LINUX_DEPLOYMENT.md (optional)"
cp ARCHITECTURE.md "$PRODUCTION_DIR/docs/API.md" 2>/dev/null || echo "[!] ARCHITECTURE.md (optional)"
cp PRODUCTION_PACKAGE.md "$PRODUCTION_DIR/docs/PACKAGE.md" 2>/dev/null || echo "[!] PRODUCTION_PACKAGE.md (optional)"

echo ""
echo "[*] Создаем README для production..."
cat > "$PRODUCTION_DIR/README.md" << 'PROD_README'
# CAPTCHA OCR - Production Ready

Это финальный production package готовый к развертыванию на Linux сервере.

## Структура

```
production/
├── python_api/          - Flask REST API
│   ├── captcha_api.py
│   ├── requirements.txt
│   └── models/
│       ├── model.keras
│       └── labels.csv
├── nodejs_client/       - Node.js интеграция с Puppeteer
│   ├── captcha_client_nodejs.js
│   ├── captcha_solver_example.js
│   └── package.json
├── docs/               - Документация
└── README.md
```

## Быстрый старт

### 1. Python API

```bash
cd production/python_api/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 captcha_api.py --host 0.0.0.0 --port 5000
```

### 2. Node.js Bot

```bash
cd production/nodejs_client/
npm install
node captcha_solver_example.js --url http://localhost:5000
```

## API Endpoints

- `GET /health` - Health check
- `GET /info` - API информация
- `POST /predict` - Single prediction
- `POST /predict-batch` - Batch predictions

## Документация

Смотри файлы в `docs/` папке для подробной информации.

## Production Deployment

Для развертывания на production сервере:

1. Распакуй архив
2. Установи зависимости (see docs/DEPLOYMENT.md)
3. Настрой systemd services
4. Настрой Nginx reverse proxy
5. Добавь SSL сертификат

Good luck! ���
PROD_README

echo "[OK] README создан"

echo ""
echo "[*] Создаем структуру файлов..."
tree "$PRODUCTION_DIR" 2>/dev/null || find "$PRODUCTION_DIR" -type f | sort

echo ""
echo "[*] Проверяем размеры файлов..."
du -sh "$PRODUCTION_DIR"

echo ""
echo "[*] Создаем архив: $ARCHIVE_NAME"
tar -czf "$ARCHIVE_NAME" "$PRODUCTION_DIR/"

if [ $? -eq 0 ]; then
    echo "[OK] Архив создан успешно"
    ls -lh "$ARCHIVE_NAME"
    echo ""
    echo "��� Production package готов!"
    echo ""
    echo "Для использования:"
    echo "  1. Скопируй $ARCHIVE_NAME на сервер"
    echo "  2. tar -xzf $ARCHIVE_NAME"
    echo "  3. Следуй инструкциям в docs/DEPLOYMENT.md"
else
    echo "[ERROR] Ошибка при создании архива"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Production Package создан успешно!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

