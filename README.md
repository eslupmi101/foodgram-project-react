# Дипломный проект Foodgram
[![Master deploy Foodgram workflow](https://github.com/eslupmi101/foodgram-project-react/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/eslupmi101/foodgram-project-react/actions/workflows/master.yml)

Сайт доступен по ссылке - https://foodgramajsen.ddns.net/

### **Описание проекта**
Foodgram - это уникальная онлайн-платформа, предназначенная для всех, кто разделяет страсть к кулинарии и ищет бесконечное вдохновение в мире готовки. Наш веб-сайт предоставляет широкие возможности для создания, сохранения и публикации собственных рецептов, а также для вдохновения и обмена идеями с другими кулинарами со всего мира.

Ключевые функции и возможности:

- Создание Рецептов: На "Кулинарном Вдохновении" вы можете создавать собственные уникальные рецепты. Добавляйте ингредиенты, описания этапов приготовления, иллюстрации и многое другое, чтобы поделиться своими кулинарными шедеврами с сообществом.

- Избранное: Сохраняйте свои любимые рецепты в избранное для легкого доступа и быстрого приготовления в будущем. Не нужно больше искать тот рецепт, который вам так понравился.

- Корзина Покупок: Планируйте свои покупки на кухне, добавляя необходимые ингредиенты из рецептов в корзину покупок. Это помогает вам не забыть ни один ингредиент, когда вы идете за продуктами.

- Обмен идеями: Помимо создания и сохранения собственных рецептов, вы можете общаться с другими участниками сообщества, делясь советами, хитростями и вдохновением. Здесь можно найти новых друзей с общим интересом к готовке.

Сайт создан на React + Django REST. Упакован в Docker контейнеры.

Проект запускается через virtualvenv и через Docker compose

### **Стэк используемых основных технологий:**

| программа                     | версия |
|-------------------------------|--------|
| Python                        | 3.10.12|
| npm                           |  9.8.0 |
| node                          | 13.12.0 |
| react                         | 17.0.2 |
| Django                        | 3.2.3  |
| djangorestframework           | 3.12.4  |
| gunicorn                      | 21.2.0  |
| Docker                        | 23.0.2 | 


### **Запускаем проект в localhost и в dev режиме c помощью Docker**
Создаем .env на основе .env.dist и заполняем его
```
mv .env.dist .env
```

Запуск Docker контейнеров через compose
```
docker compose -f docker-compose.production.yml up
```

Собираем статики для админки
```
docker exec foodgram-backend-1 /app/collectstatic
```

Мигрируем данные в бд
```
docker exec foodgram-backend-1 python /app/manage.py migrate
```

Заходим на сайт по порту
```
http://localhost:9000/
```


### **Запускаем проект в localhost и в dev режиме на macOS через venv**
Клонировать репозиторий с GitHub
```
git clone https://github.com/eslupmi101/foodgram-project-react.git
```

#### **Запускаем backend**
Установить виртуальное окружение venv
```
python3 -m venv ./backend/venv
```

Aктивировать виртуальное окружение venv
```
source ./backend/venv/scripts/activate
```

Обновить менеджер пакетов pip
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt
```
pip install -r requirements.txt
```

Создаем .env с аргументом SECRET_KEY="".
Заполняем SECRET_KEY безопасным секретным ключом
```
touch .env

echo "SECRET_KEY="<ваш секретный ключ>"" > .env 
```

Создать миграции
```
python3 ./backend/manage.py makemigrations
```

Выполнить миграции
```
python3 ./backend/manage.py migrate
```

Запустить сервер backend
```
python3 ./backend/manage.py runserver
```

####  **Запускаем фронтенд**

Заходим в директорию с фронтендом
```
cd ./frontend
```

Устанавливаем зависимости
```
npm i
```

Собираем билд
```
npm run build
```

Запускаем сервер фронтенда
```
npm start
```
### **Автор проекта:**
[Айсен Андреев](https://github.com/eslupmi101) - Python-разработчик
