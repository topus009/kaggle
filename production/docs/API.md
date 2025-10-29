# Архитектура системы CAPTCHA OCR

## ���️ Общая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Node.js Application                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Puppeteer (Virtual Browser)                            │  │
│  │  ├─ Navigate to website                                 │  │
│  │  ├─ Find CAPTCHA element                                │  │
│  │  ├─ Take screenshot                                     │  │
│  │  └─ Pass screenshot to API                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           │ HTTP POST                          │
│                           ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CAPTCHA Client (Node.js)                               │  │
│  │  ├─ Convert image to base64                             │  │
│  │  ├─ Send to Flask API                                   │  │
│  │  └─ Parse JSON response                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           ║
                           ║ REST API (HTTP/JSON)
                           ║
┌─────────────────────────────────────────────────────────────────┐
│                     Python Flask Server                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints:                                    │  │
│  │  ├─ GET  /health      - Health check                   │  │
│  │  ├─ GET  /info        - API information                │  │
│  │  ├─ POST /predict     - Single image prediction        │  │
│  │  └─ POST /predict-batch - Batch predictions            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Image Preprocessing                                    │  │
│  │  ├─ Decode image (PNG/JPEG)                             │  │
│  │  ├─ Normalize colors                                    │  │
│  │  ├─ Transpose (200x60)                                  │  │
│  │  └─ Add batch dimension                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TensorFlow/Keras Model (CTC-LSTM)                      │  │
│  │  ├─ Input: 200x60x3 RGB image                           │  │
│  │  ├─ CNN layers: Feature extraction                      │  │
│  │  ├─ BiLSTM layers: Sequence recognition                │  │
│  │  ├─ CTC layer: Variable-length output                   │  │
│  │  └─ Output: Text (1-7 characters)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CTC Decode & Post-Processing                           │  │
│  │  ├─ Greedy CTC decoding                                 │  │
│  │  ├─ Character mapping (alphabet conversion)             │  │
│  │  ├─ Confidence score                                    │  │
│  │  └─ Return JSON response                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           ║
                           ║ Return JSON (prediction + confidence)
                           ║
┌─────────────────────────────────────────────────────────────────┐
│                        Node.js Application                      │
│  ├─ Receive prediction result                                  │
│  ├─ Type text into CAPTCHA form field                          │
│  ├─ Submit form                                                │
│  └─ Continue scraping                                          │
└─────────────────────────────────────────────────────────────────┘
```

## ��� API Endpoints

### 1. GET /health
**Проверка статуса сервера**
```
Request:  GET /health
Response: {
  "status": "ok",
  "model_loaded": true,
  "version": "1.0"
}
```

### 2. GET /info
**Информация об API**
```
Request:  GET /info
Response: {
  "name": "CAPTCHA OCR API",
  "version": "1.0",
  "description": "REST API for CAPTCHA text recognition",
  "model": {
    "path": "final-results/output/model.keras",
    "image_size": [60, 200],
    "max_sequence_length": 7,
    "accuracy_kaggle": "95%"
  },
  "endpoints": {...}
}
```

### 3. POST /predict
**Предсказание для одного изображения**

**Вариант 1: Загруженный файл**
```
Request:
  Content-Type: multipart/form-data
  Body: image=<binary_image>

Response: {
  "success": true,
  "prediction": "б8м6ж",
  "confidence": 0.95
}
```

**Вариант 2: Base64 JSON**
```
Request:
  Content-Type: application/json
  Body: {
    "image": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
  }

Response: {
  "success": true,
  "prediction": "б8м6ж",
  "confidence": 0.95
}
```

### 4. POST /predict-batch
**Batch предсказание**
```
Request:
  Content-Type: application/json
  Body: {
    "images": [
      "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      ...
    ]
  }

Response: {
  "success": true,
  "total": 3,
  "results": [
    {
      "index": 0,
      "prediction": "б8м6ж",
      "success": true
    },
    ...
  ]
}
```

## ��� Data Flow

### Сценарий 1: Локальное предсказание
```
Python Client → predict.py → Model → predictions.txt
```

### Сценарий 2: API Предсказание (одно изображение)
```
Node.js Client 
  ├─ GET /health (проверка)
  ├─ POST /predict (изображение) 
  └─ Receive prediction
```

### Сценарий 3: Batch API Предсказание
```
Node.js Client
  ├─ GET /health (проверка)
  ├─ POST /predict-batch (все изображения)
  └─ Receive results array
```

### Сценарий 4: Puppeteer + API
```
Node.js (Puppeteer)
  ├─ Launch browser
  ├─ Navigate to website
  ├─ Find CAPTCHA element
  ├─ Screenshot CAPTCHA
  ├─ Convert to base64
  ├─ POST /predict (to Flask API)
  ├─ Type prediction into form
  ├─ Submit form
  └─ Close browser
```

## ��� Model Architecture

```
Input: 200x60x3 RGB Image
   │
   ├─ Normalization (0-1 range)
   │
   ├─ Transpose (200, 60, 3)
   │
   ├─ Conv2D Layer 1 (32 filters, 3x3 kernel)
   │  └─ MaxPooling(2x2)
   │
   ├─ Conv2D Layer 2 (64 filters, 3x3 kernel)
   │  └─ MaxPooling(2x2)
   │
   ├─ Flatten
   │
   ├─ Reshape to sequence format (time_steps, features)
   │
   ├─ Bidirectional LSTM (256 units)
   │
   ├─ Dense Layer (alphabet_size)
   │
   ├─ CTC Layer (Variable-length output)
   │
   └─ Output: 1-7 characters (б, в, г, д, ж, к, л, м, н, п, р, с, т, 2-9)
```

## ��� Security Considerations

### 1. API Authentication
```python
# Add API key validation
@app.before_request
def check_api_key():
    if request.method != 'OPTIONS':
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    ...
```

### 3. CORS Configuration
```python
CORS(app, 
     origins=["http://localhost:3000", "http://your-domain.com"],
     methods=["GET", "POST"],
     allow_headers=["Content-Type", "X-API-Key"]
)
```

## ��� Deployment Options

### Option 1: Single Server
```
One Linux server:
├─ Python Flask API (port 5000)
└─ Node.js + Puppeteer (localhost connection)
```

### Option 2: Distributed
```
API Server:      Flask API on Linux
Bot Server:      Node.js + Puppeteer on separate Linux
Communication:   HTTP over network
```

### Option 3: Load Balanced
```
                    ┌─ API Server 1 (port 5000)
Nginx Load Balancer ├─ API Server 2 (port 5000)
(port 80/443)       └─ API Server 3 (port 5000)
```

### Option 4: Docker
```
Docker Container 1: Flask API (Python)
Docker Container 2: Node.js + Puppeteer
Docker Network:     Internal communication
```

## ��� Performance Metrics

| Metric | Value |
|--------|-------|
| Model Size | ~1.8 MB |
| Inference Time | 100-200 ms |
| Throughput (single) | 5-10 req/sec |
| Throughput (batch 10) | 50-100 req/sec |
| Memory Usage | 500 MB - 1 GB |
| Max Image Size | 500 KB |
| Supported Format | PNG, JPEG, BMP, TIFF |

## ��� Configuration Files

### Flask API (captcha_api.py)
- Model path: `final-results/output/model.keras`
- Labels path: `images/labels.csv`
- Image size: 200x60
- Max sequence: 7 characters
- Default host: 127.0.0.1
- Default port: 5000

### Node.js Client (captcha_client_nodejs.js)
- API URL: configurable
- Timeout: 30 seconds
- Supported formats: PNG, JPEG, Buffer, Base64
- Methods: predict, predictFile, predictBatch, predictUrl

## ��� Integration Examples

### Python to Flask
```python
import requests
response = requests.post('http://api:5000/predict', 
                        files={'image': open('img.png', 'rb')})
```

### Node.js to Flask
```javascript
const client = new CaptchaClient('http://api:5000');
const result = await client.predictFile('img.png');
```

### cURL
```bash
curl -X POST -F "image=@test.png" http://localhost:5000/predict
```

---

**Архитектура готова для production развертывания** ✨
