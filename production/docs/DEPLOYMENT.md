# Развертывание CAPTCHA OCR на Linux сервере

Полное руководство по настройке Flask API сервера и интеграции с Node.js/Puppeteer для автоматизации.

## 📋 Требования

- Linux сервер (Ubuntu, Debian, CentOS и т.д.)
- Python 3.8+
- Node.js 14+
- ~2 GB RAM
- Интернет соединение

## 🚀 Этап 1: Подготовка Linux сервера

### 1.1 Обновить систему
```bash
sudo apt update && sudo apt upgrade -y  # Debian/Ubuntu
sudo yum update -y                       # CentOS/RHEL
```

### 1.2 Установить Python
```bash
sudo apt install python3-pip python3-venv -y  # Debian/Ubuntu
sudo yum install python3-pip python3-venv -y  # CentOS/RHEL

python3 --version  # Проверить версию
```

### 1.3 Установить Node.js
```bash
# Вариант 1: из стандартного репозитория
sudo apt install nodejs npm -y

# Вариант 2: свежая версия
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

node --version
npm --version
```

## 🔧 Этап 2: Развертывание Python Flask API

### 2.1 Скопировать файлы на сервер
```bash
# На локальном компьютере:
scp -r ./* user@server:/home/user/captcha_ocr/

# ИЛИ через Git:
cd /home/user
git clone <repo_url> captcha_ocr
cd captcha_ocr
```

### 2.2 Создать виртуальное окружение Python
```bash
cd /home/user/captcha_ocr
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Запустить Flask API сервер
```bash
# Режим разработки
python captcha_api.py --host 127.0.0.1 --port 5000

# Для внешних подключений (из Node.js)
python captcha_api.py --host 0.0.0.0 --port 5000

# Для использования в production (Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 captcha_api:app
```

### 2.4 Проверить работу API
```bash
# Проверка здоровья
curl http://localhost:5000/health

# Информация об API
curl http://localhost:5000/info

# Тест предсказания с файлом
curl -X POST -F "image=@test.png" http://localhost:5000/predict
```

## 🌐 Этап 3: Node.js интеграция с Puppeteer

### 3.1 Создать Node.js проект
```bash
mkdir /home/user/captcha_bot
cd /home/user/captcha_bot
npm init -y
```

### 3.2 Установить зависимости
```bash
npm install puppeteer form-data
```

### 3.3 Скопировать Node.js клиент
```bash
cp /home/user/captcha_ocr/captcha_client_nodejs.js ./
```

### 3.4 Создать скрипт для загрузки CAPTCHA и предсказания
```javascript
// captcha_solver.js
const puppeteer = require('puppeteer');
const fs = require('fs');
const CaptchaClient = require('./captcha_client_nodejs');

const CAPTCHA_API_URL = 'http://localhost:5000';  // или IP сервера
const client = new CaptchaClient(CAPTCHA_API_URL);

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  
  try {
    // Загрузить страницу с CAPTCHA
    await page.goto('https://is.fssp.gov.ru/');
    
    // Получить скриншот CAPTCHA
    const captchaElement = await page.$('img.captcha');  // Адаптировать селектор
    const screenshot = await captchaElement.screenshot();
    
    // Отправить на предсказание
    console.log('[*] Предсказываю CAPTCHA...');
    const result = await client.predict(screenshot);
    
    if (result.success) {
      console.log(`[OK] Предсказание: ${result.prediction}`);
      
      // Вводим текст в CAPTCHA поле
      await page.type('input[name="captcha"]', result.prediction);
      
      // Отправляем форму
      await page.click('button[type="submit"]');
      await page.waitForNavigation();
      
      console.log('[OK] Форма отправлена!');
    } else {
      console.error(`[ERROR] ${result.error}`);
    }
    
  } finally {
    await browser.close();
  }
})();
```

### 3.5 Запустить скрипт
```bash
node captcha_solver.js
```

## 🔄 Этап 4: Systemd сервис для автозапуска

### 4.1 Создать systemd сервис для Flask API
```bash
sudo nano /etc/systemd/system/captcha-api.service
```

Содержимое:
```ini
[Unit]
Description=CAPTCHA OCR REST API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/captcha_ocr
Environment="PATH=/home/user/captcha_ocr/venv/bin"
ExecStart=/home/user/captcha_ocr/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 captcha_api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.2 Включить и запустить сервис
```bash
sudo systemctl daemon-reload
sudo systemctl enable captcha-api.service
sudo systemctl start captcha-api.service

# Проверить статус
sudo systemctl status captcha-api.service

# Логи
sudo journalctl -u captcha-api.service -f
```

## 🔐 Этап 5: Reverse Proxy с Nginx (опционально)

### 5.1 Установить Nginx
```bash
sudo apt install nginx -y
```

### 5.2 Конфигурация
```bash
sudo nano /etc/nginx/sites-available/captcha-api
```

Содержимое:
```nginx
upstream flask_api {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://flask_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5.3 Включить конфигурацию
```bash
sudo ln -s /etc/nginx/sites-available/captcha-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Мониторинг и логирование

### Логи Flask API
```bash
# В реальном времени
sudo journalctl -u captcha-api.service -f

# Последние 100 строк
sudo journalctl -u captcha-api.service -n 100
```

### Проверка портов
```bash
# Проверить если Flask слушает
netstat -tlnp | grep 5000
ss -tlnp | grep 5000

# Проверить соединение
curl http://localhost:5000/health
```

## 🐛 Решение проблем

### Flask не запускается
```bash
# Проверить синтаксис Python
python -m py_compile captcha_api.py

# Запустить с debug
python captcha_api.py --debug
```

### Puppeteer не может найти браузер
```bash
# Установить зависимости Chrome/Chromium
sudo apt-get install -y \
  libglib2.0-0 \
  libgconf-2-4 \
  libappindicator1 \
  libappindicator3-1 \
  libappindicator-gtk3-1 \
  fonts-liberation \
  libappindicator1 \
  libappindicator3-1

# ИЛИ использовать системный браузер
const browser = await puppeteer.launch({
  executablePath: '/usr/bin/chromium-browser',
  headless: 'new',
  args: ['--no-sandbox']
});
```

### Ошибки памяти
```bash
# Проверить свободную память
free -h

# Увеличить swap если нужно
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 Оптимизация для production

### 1. Использовать Gunicorn с несколькими workers
```bash
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 captcha_api:app
```

### 2. Использовать Redis для кеша
```bash
# Установить Redis
sudo apt install redis-server -y

# Использовать в API (требует flask-caching)
pip install flask-caching redis
```

### 3. Load balancing с несколькими API сервисами
```bash
# Запустить на разных портах
python captcha_api.py --port 5000
python captcha_api.py --port 5001
python captcha_api.py --port 5002
```

Затем настроить Nginx для load balancing:
```nginx
upstream api_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}
```

## 🎯 Тестирование

### Тест производительности
```bash
# Установить Apache Bench
sudo apt install apache2-utils -y

# Нагрузочный тест
ab -n 1000 -c 10 http://localhost:5000/health
```

### Тест Node.js клиента
```bash
node captcha_client_nodejs.js health --url http://localhost:5000
node captcha_client_nodejs.js info --url http://localhost:5000
node captcha_client_nodejs.js predict test.png --url http://localhost:5000
```

## 📚 Примеры использования

### Python клиент
```python
import requests

url = 'http://localhost:5000/predict'
with open('captcha.png', 'rb') as f:
    files = {'image': f}
    response = requests.post(url, files=files)
    result = response.json()
    print(f"Prediction: {result['prediction']}")
```

### Node.js с async/await
```javascript
const CaptchaClient = require('./captcha_client_nodejs');
const client = new CaptchaClient('http://localhost:5000');

async function solveCaptcha(imagePath) {
  try {
    const result = await client.predictFile(imagePath);
    console.log(`Solved: ${result.prediction}`);
    return result.prediction;
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

solveCaptcha('captcha.png');
```

### Batch обработка
```javascript
const CaptchaClient = require('./captcha_client_nodejs');
const client = new CaptchaClient('http://localhost:5000');

async function solveBatch(imagePaths) {
  try {
    const result = await client.predictBatch(imagePaths);
    result.results.forEach(r => {
      console.log(`${r.index}: ${r.prediction}`);
    });
    return result;
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

solveBatch(['img1.png', 'img2.png', 'img3.png']);
```

## 🎓 Дополнительная информация

- Flask документация: https://flask.palletsprojects.com/
- Puppeteer документация: https://github.com/puppeteer/puppeteer
- Gunicorn документация: https://gunicorn.org/
- Nginx документация: https://nginx.org/

---

**Готово! Система готова для production использования на Linux сервере.** ✨
