# Инструкция по подключению к GitHub

## Шаг 1: Создать репозиторий на GitHub

1. Откройте [github.com](https://github.com)
2. Нажмите кнопку **"New"** (зеленая кнопка создания нового репозитория)
3. Имя репозитория: `kaggle`
4. Описание: "CAPTCHA OCR Model with CNN-LSTM for Russian text recognition"
5. Выберите **Public** (или Private если хотите)
6. **НЕ** добавляйте README, .gitignore или лицензию (уже есть)
7. Нажмите **"Create repository"**

## Шаг 2: Подключить локальный репозиторий к GitHub

Откройте терминал в папке проекта и выполните:

```bash
cd "/home/sergey-topolov/Рабочий стол/kaggle"

# Добавить удаленный репозиторий (замените YOUR_USERNAME на свой GitHub username)
git remote add origin https://github.com/topus009/kaggle.git

# Переименовать ветку в main (опционально, но рекомендуется)
git branch -M main

# Отправить код на GitHub
git push -u origin main
```

## Шаг 3: Подключить Kaggle к репозиторию

### Вариант 1: Автоматический GitHub Integration (Kaggle)

1. Откройте ваш ноутбук на Kaggle
2. В правом меню нажмите **"Add-ons"** → **"GitHub"**
3. Включите GitHub Integration
4. Авторизуйтесь через GitHub
5. Выберите репозиторий `kaggle`
6. Укажите ветку: `master`
7. Нажмите **"Save"**

После этого каждый раз когда вы запускаете ноутбук и делаете commit, изменения автоматически отправляются на GitHub.

### Вариант 2: Ручное обновление (с телефона)

Когда хотите обновить код с телефона:

```bash
# В Kaggle ноутбуке создайте новую ячейку:
git clone https://github.com/topus009/kaggle.git
cd kaggle

# Делайте изменения...

# Добавьте изменения
git add .
git commit -m "описание изменений"
git push
```

## Команды для работы

### Обновить код на GitHub после изменений

```bash
cd "/home/sergey-topolov/Рабочий стол/kaggle"
git add .
git commit -m "описание изменений"
git push
```

### Получить обновления с GitHub

```bash
git pull origin main
```

### Посмотреть статус

```bash
git status
git log --oneline  # история коммитов
```

## Полезные ссылки

- Проект: `/home/sergey-topolov/Рабочий стол/kaggle`
- GitHub репозиторий: `https://github.com/topus009/kaggle`

## Решение проблем

### Если забыли username

```bash
git config user.name
git config user.email
```

### Если нужно изменить remote URL

```bash
git remote set-url origin https://github.com/topus009/kaggle.git
```

### Если проблемы с авторизацией GitHub

Используйте Personal Access Token вместо пароля:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. Используйте токен вместо пароля при push
