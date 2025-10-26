#!/bin/bash
# Скрипт для быстрого обновления кода на GitHub

echo "==================================="
echo "Обновление кода CAPTCHA OCR"
echo "==================================="

# Путь к проекту
PROJECT_DIR="/home/sergey-topolov/Рабочий стол/kaggle"

cd "$PROJECT_DIR"

# Проверка статуса
echo ""
echo "📊 Текущий статус:"
git status

echo ""
echo "📦 Добавление всех изменений..."
git add .

echo ""
read -p "💬 Введите сообщение коммита: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Update code"
fi

echo ""
echo "💾 Создание коммита: $commit_message"
git commit -m "$commit_message"

echo ""
echo "🚀 Отправка на GitHub..."
git push origin main

echo ""
echo "==================================="
echo "✅ Готово! Код обновлен на GitHub"
echo "==================================="
