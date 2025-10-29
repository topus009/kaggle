#!/usr/bin/env node
/**
 * CAPTCHA OCR API Client для Node.js
 * 
 * Пример использования:
 *   const CaptchaClient = require('./captcha_client_nodejs');
 *   const client = new CaptchaClient('http://localhost:5000');
 *   
 *   // Одно изображение
 *   client.predict('image.png').then(result => console.log(result));
 *   
 *   // Batch
 *   client.predictBatch(['image1.png', 'image2.png']).then(results => console.log(results));
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const FormData = require('form-data');

class CaptchaClient {
  constructor(baseUrl = 'http://localhost:5000', options = {}) {
    this.baseUrl = baseUrl;
    this.timeout = options.timeout || 30000;
    this.debug = options.debug || false;
  }

  /**
   * Отправить HTTP запрос
   */
  async request(method, endpoint, data = null, isFormData = false) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.baseUrl + endpoint);
      const protocol = url.protocol === 'https:' ? https : http;

      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        timeout: this.timeout
      };

      if (isFormData && data) {
        options.headers = data.getHeaders();
      } else if (data && !isFormData) {
        options.headers = {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(JSON.stringify(data))
        };
      }

      if (this.debug) {
        console.log(`[DEBUG] ${method} ${url}`);
      }

      const req = protocol.request(options, (res) => {
        let responseData = '';

        res.on('data', chunk => {
          responseData += chunk;
        });

        res.on('end', () => {
          try {
            const parsed = JSON.parse(responseData);

            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(parsed);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${parsed.error || 'Unknown error'}`));
            }
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${responseData}`));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      if (isFormData && data) {
        data.pipe(req);
      } else if (data && !isFormData) {
        req.write(JSON.stringify(data));
        req.end();
      } else {
        req.end();
      }
    });
  }

  /**
   * Проверка статуса сервера
   */
  async health() {
    return this.request('GET', '/health');
  }

  /**
   * Получить информацию о API
   */
  async info() {
    return this.request('GET', '/info');
  }

  /**
   * Предсказать текст для одного изображения из файла
   */
  async predictFile(filePath) {
    return new Promise((resolve, reject) => {
      fs.stat(filePath, (err) => {
        if (err) {
          reject(new Error(`File not found: ${filePath}`));
          return;
        }

        const form = new FormData();
        form.append('image', fs.createReadStream(filePath));

        const url = new URL(this.baseUrl + '/predict');
        const protocol = url.protocol === 'https:' ? https : http;

        const options = {
          hostname: url.hostname,
          port: url.port,
          path: url.pathname,
          method: 'POST',
          headers: form.getHeaders(),
          timeout: this.timeout
        };

        if (this.debug) {
          console.log(`[DEBUG] POST ${url} (file: ${filePath})`);
        }

        const req = protocol.request(options, (res) => {
          let responseData = '';

          res.on('data', chunk => {
            responseData += chunk;
          });

          res.on('end', () => {
            try {
              const parsed = JSON.parse(responseData);
              resolve(parsed);
            } catch (e) {
              reject(new Error(`Invalid JSON: ${responseData}`));
            }
          });
        });

        req.on('error', reject);
        req.on('timeout', () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });

        form.pipe(req);
      });
    });
  }

  /**
   * Предсказать текст для изображения в памяти (Buffer)
   */
  async predict(imageBuffer) {
    // Если это строка (путь к файлу), используем predictFile
    if (typeof imageBuffer === 'string') {
      return this.predictFile(imageBuffer);
    }

    // Иначе это Buffer или base64
    let base64;
    if (Buffer.isBuffer(imageBuffer)) {
      base64 = imageBuffer.toString('base64');
    } else if (typeof imageBuffer === 'string') {
      base64 = imageBuffer;
    } else {
      throw new Error('Expected Buffer or string');
    }

    const data = {
      image: base64
    };

    return this.request('POST', '/predict', data);
  }

  /**
   * Batch предсказание для нескольких изображений
   */
  async predictBatch(imageBuffers) {
    const images = [];

    for (const img of imageBuffers) {
      let base64;

      if (typeof img === 'string' && fs.existsSync(img)) {
        // Это путь к файлу
        const buffer = fs.readFileSync(img);
        base64 = buffer.toString('base64');
      } else if (Buffer.isBuffer(img)) {
        base64 = img.toString('base64');
      } else if (typeof img === 'string') {
        base64 = img;
      } else {
        throw new Error('Expected file path, Buffer, or base64 string');
      }

      images.push(base64);
    }

    const data = {
      images: images
    };

    return this.request('POST', '/predict-batch', data);
  }

  /**
   * Предсказать из URL
   */
  async predictUrl(imageUrl) {
    return new Promise((resolve, reject) => {
      const protocol = imageUrl.startsWith('https') ? https : http;

      protocol.get(imageUrl, (res) => {
        let imageData = '';
        res.setEncoding('binary');

        res.on('data', chunk => {
          imageData += chunk;
        });

        res.on('end', () => {
          const buffer = Buffer.from(imageData, 'binary');
          this.predict(buffer)
            .then(resolve)
            .catch(reject);
        });
      }).on('error', reject);
    });
  }
}

// Экспортируем для использования как модуль
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CaptchaClient;
}

// CLI использование
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
CAPTCHA OCR API Client - CLI

Usage:
  node captcha_client_nodejs.js health [--url http://localhost:5000]
  node captcha_client_nodejs.js info [--url http://localhost:5000]
  node captcha_client_nodejs.js predict <image_file> [--url http://localhost:5000]
  node captcha_client_nodejs.js batch <image1> <image2> ... [--url http://localhost:5000]

Examples:
  node captcha_client_nodejs.js health
  node captcha_client_nodejs.js predict test.png
  node captcha_client_nodejs.js batch image1.png image2.png image3.png
  node captcha_client_nodejs.js predict test.png --url http://192.168.1.100:5000
    `);
    return;
  }

  const urlIndex = args.indexOf('--url');
  const apiUrl = urlIndex !== -1 ? args[urlIndex + 1] : 'http://localhost:5000';
  const client = new CaptchaClient(apiUrl, { debug: true });

  const command = args[0];

  (async () => {
    try {
      if (command === 'health') {
        const result = await client.health();
        console.log('[OK] Server is healthy');
        console.log(JSON.stringify(result, null, 2));
      } else if (command === 'info') {
        const result = await client.info();
        console.log('[OK] API Information');
        console.log(JSON.stringify(result, null, 2));
      } else if (command === 'predict') {
        const filePath = args[1];
        if (!filePath) {
          console.error('[ERROR] Please specify image file');
          process.exit(1);
        }
        console.log(`[*] Predicting: ${filePath}`);
        const result = await client.predictFile(filePath);
        console.log('[OK] Prediction result:');
        console.log(JSON.stringify(result, null, 2));
      } else if (command === 'batch') {
        const files = args.slice(1).filter(f => f !== '--url' && !f.startsWith('http'));
        if (files.length === 0) {
          console.error('[ERROR] Please specify image files');
          process.exit(1);
        }
        console.log(`[*] Batch predicting: ${files.join(', ')}`);
        const result = await client.predictBatch(files);
        console.log('[OK] Batch results:');
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.error(`[ERROR] Unknown command: ${command}`);
        process.exit(1);
      }
    } catch (error) {
      console.error(`[ERROR] ${error.message}`);
      process.exit(1);
    }
  })();
}
