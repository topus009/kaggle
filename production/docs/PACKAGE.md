# ��� Production Ready Package

Финальный набор файлов для развертывания на Linux сервере.

## ���️ Структура для production

```
production/
├── python_api/                    ← Python Flask API
│   ├── captcha_api.py            ← REST API сервер
│   ├── requirements.txt           ← Python зависимости
│   └── models/
│       ├── model.keras           ← Модель (скопировать из final-results/output/)
│       └── labels.csv            ← Метки (скопировать из images/)
│
├── nodejs_client/                 ← Node.js Puppeteer интеграция
│   ├── package.json
│   ├── captcha_client_nodejs.js  ← API клиент
│   └── captcha_solver.js         ← Пример скрипта с Puppeteer
│
├── docker/                        ← Docker конфигурация (опционально)
│   ├── Dockerfile.api
│   ├── Dockerfile.bot
│   └── docker-compose.yml
│
├── config/
│   ├── systemd_service.ini       ← Systemd сервис
│   └── nginx.conf                ← Nginx конфигурация
│
├── docs/
│   ├── DEPLOYMENT.md             ← Инструкции развертывания
│   ├── API.md                    ← API документация
│   └── TROUBLESHOOTING.md        ← Решение проблем
│
└── README.md                      ← Главная инструкция
```

## ��� Что нужно скопировать на сервер

### 1. Python API часть:
```bash
production/python_api/
├── captcha_api.py (готов)
├── requirements.txt (готов)
└── models/
    ├── model.keras (из final-results/output/)
    └── labels.csv (из images/)
```

### 2. Node.js часть:
```bash
production/nodejs_client/
├── captcha_client_nodejs.js (готов)
├── captcha_solver.js (новый)
└── package.json (новый)
```

### 3. Конфигурация:
```bash
production/config/
├── systemd_service.ini
└── nginx.conf
```

### 4. Документация:
```bash
production/docs/
├── DEPLOYMENT.md
├── API.md
└── TROUBLESHOOTING.md
```

## ��� Команды для создания package'а

```bash
# 1. Создать структуру
mkdir -p production/python_api/models
mkdir -p production/nodejs_client
mkdir -p production/config
mkdir -p production/docs

# 2. Скопировать Python файлы
cp captcha_api.py production/python_api/
cp requirements.txt production/python_api/

# 3. Скопировать модель и метки
cp final-results/output/model.keras production/python_api/models/
cp images/labels.csv production/python_api/models/

# 4. Скопировать Node.js файлы
cp captcha_client_nodejs.js production/nodejs_client/

# 5. Скопировать документацию
cp LINUX_DEPLOYMENT.md production/docs/DEPLOYMENT.md
cp ARCHITECTURE.md production/docs/API.md

# 6. Создать архив для отправки
tar -czf captcha_ocr_production.tar.gz production/
```

## ��� Размеры файлов

```
captcha_api.py              ~10 KB
requirements.txt            ~1 KB
model.keras                 ~1.8 MB
labels.csv                  ~50 KB
captcha_client_nodejs.js    ~15 KB
документация                ~200 KB

Итого:                      ~2.1 MB (без зависимостей)
```

## ��� На Linux сервере (быстрое развертывание)

```bash
# 1. Распаковать архив
tar -xzf captcha_ocr_production.tar.gz
cd production/

# 2. Python API
cd python_api/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Проверить модель
python3 -c "import tensorflow; print(tensorflow.__version__)"

# 4. Запустить API
python3 captcha_api.py --host 0.0.0.0 --port 5000

# 5. В другом терминале - Node.js
cd ../nodejs_client/
npm install
node captcha_client_nodejs.js health --url http://localhost:5000
```

## ��� Контрольный список перед развертыванием

- [ ] Модель скопирована в python_api/models/
- [ ] Labels.csv скопирован
- [ ] requirements.txt обновлен
- [ ] captcha_api.py готов
- [ ] captcha_client_nodejs.js готов
- [ ] Все пути в файлах правильные
- [ ] Документация актуальна
- [ ] Архив создан и протестирован

