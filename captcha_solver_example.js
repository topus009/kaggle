#!/usr/bin/env node
/**
 * CAPTCHA Solver Bot Example
 * Использует Puppeteer для автоматизации браузера и Flask API для решения CAPTCHA
 * 
 * Использование:
 *   node captcha_solver_example.js --url http://localhost:5000
 */

const puppeteer = require('puppeteer');
const CaptchaClient = require('./captcha_client_nodejs');

// Конфигурация
const API_URL = process.argv.includes('--url') 
  ? process.argv[process.argv.indexOf('--url') + 1] 
  : 'http://localhost:5000';

const TARGET_URL = process.argv.includes('--target')
  ? process.argv[process.argv.indexOf('--target') + 1]
  : 'https://is.fssp.gov.ru/';  // Пример: FSSP сайт

console.log(`[*] API URL: ${API_URL}`);
console.log(`[*] Target URL: ${TARGET_URL}`);

const client = new CaptchaClient(API_URL, { debug: true });

/**
 * Найти и решить CAPTCHA
 */
async function solveCaptchaOnPage(page) {
  try {
    // Ожидаем загрузки страницы
    await page.waitForNavigation({ waitUntil: 'networkidle2' }).catch(() => {});
    
    // Получаем скриншот CAPTCHA элемента
    // ВАЖНО: адаптировать селектор под конкретный сайт!
    const captchaSelectors = [
      'img.captcha',
      'img#captcha',
      'img[src*="captcha"]',
      'div.captcha img',
      '[data-captcha] img'
    ];
    
    let captchaElement = null;
    for (const selector of captchaSelectors) {
      try {
        captchaElement = await page.$(selector);
        if (captchaElement) {
          console.log(`[OK] Найден CAPTCHA элемент: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    if (!captchaElement) {
      console.error('[ERROR] CAPTCHA элемент не найден на странице');
      return null;
    }
    
    // Получаем скриншот CAPTCHA
    console.log('[*] Получаем скриншот CAPTCHA...');
    const screenshot = await captchaElement.screenshot();
    
    // Отправляем на предсказание
    console.log('[*] Отправляем на API...');
    const result = await client.predict(screenshot);
    
    if (!result.success) {
      console.error(`[ERROR] API ошибка: ${result.error}`);
      return null;
    }
    
    const prediction = result.prediction;
    console.log(`[OK] CAPTCHA решена: "${prediction}" (confidence: ${result.confidence?.toFixed(2)})`);
    
    return prediction;
    
  } catch (error) {
    console.error(`[ERROR] Ошибка при решении CAPTCHA: ${error.message}`);
    return null;
  }
}

/**
 * Ввести текст CAPTCHA в форму
 */
async function enterCaptchaInForm(page, captchaText) {
  try {
    // ВАЖНО: адаптировать селекторы под конкретный сайт!
    const inputSelectors = [
      'input[name="captcha"]',
      'input#captcha',
      'input[placeholder*="captcha" i]',
      'input[placeholder*="код" i]',
      'input[data-captcha]'
    ];
    
    let inputElement = null;
    for (const selector of inputSelectors) {
      try {
        inputElement = await page.$(selector);
        if (inputElement) {
          console.log(`[OK] Найдено поле ввода: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (!inputElement) {
      console.error('[ERROR] Поле ввода CAPTCHA не найдено');
      return false;
    }
    
    // Вводим текст
    await inputElement.type(captchaText, { delay: 50 });
    console.log(`[OK] Введен текст: ${captchaText}`);
    
    // Ищем кнопку отправки
    const submitSelectors = [
      'button[type="submit"]',
      'button:contains("Отправить")',
      'button:contains("Submit")',
      'input[type="submit"]',
      'a.btn-submit'
    ];
    
    let submitButton = null;
    for (const selector of submitSelectors) {
      try {
        submitButton = await page.$(selector);
        if (submitButton) {
          console.log(`[OK] Найдена кнопка отправки: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (submitButton) {
      console.log('[*] Нажимаем кнопку отправки...');
      await submitButton.click();
      
      // Ожидаем перенаправления
      await page.waitForNavigation({ waitUntil: 'networkidle2' })
        .catch(() => console.log('[!] Страница не переместилась'));
    }
    
    return true;
    
  } catch (error) {
    console.error(`[ERROR] Ошибка при вводе CAPTCHA: ${error.message}`);
    return false;
  }
}

/**
 * Главная функция
 */
async function main() {
  let browser = null;
  
  try {
    console.log('=' * 60);
    console.log('*** CAPTCHA Solver Bot ***');
    console.log('=' * 60);
    
    // Проверяем API
    console.log('[*] Проверяем API сервер...');
    const health = await client.health();
    if (!health.model_loaded) {
      console.error('[ERROR] Модель не загружена на сервере');
      process.exit(1);
    }
    console.log('[OK] API сервер готов');
    
    // Запускаем браузер
    console.log('[*] Запускаем браузер...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    
    const page = await browser.newPage();
    
    // Устанавливаем User-Agent
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    );
    
    console.log(`[*] Переходим на сайт: ${TARGET_URL}`);
    await page.goto(TARGET_URL, { waitUntil: 'networkidle2' });
    
    // Решаем CAPTCHA
    const captchaText = await solveCaptchaOnPage(page);
    
    if (!captchaText) {
      console.error('[ERROR] Не удалось решить CAPTCHA');
      await browser.close();
      process.exit(1);
    }
    
    // Вводим CAPTCHA и отправляем форму
    const success = await enterCaptchaInForm(page, captchaText);
    
    if (success) {
      console.log('[OK] Форма успешно отправлена!');
      
      // Даем время на обработку
      await page.waitForTimeout(3000);
      
      // Получаем содержимое страницы
      const content = await page.content();
      if (content.includes('успеш') || content.includes('success') || content.includes('ok')) {
        console.log('[OK] Форма была успешно обработана сервером!');
      } else {
        console.log('[!] Форма была отправлена, но результат неизвестен');
      }
    } else {
      console.error('[ERROR] Не удалось отправить форму');
    }
    
    await browser.close();
    console.log('\n[OK] Готово!');
    
  } catch (error) {
    console.error(`[ERROR] Критическая ошибка: ${error.message}`);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

// Запуск
if (require.main === module) {
  main().catch(err => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { solveCaptchaOnPage, enterCaptchaInForm };
