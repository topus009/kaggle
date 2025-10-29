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
