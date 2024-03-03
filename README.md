# Yatube

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

## Yatube
Yatube - социальная сеть для блогеров. 

## Технологии
Python, Django, HTML/CSS, Django ORM

## Функциональность
Регистрация и аутентификация пользователей.
Создание, редактирование и удаление собственных постов.
Комментирование постов других пользователей.
Возможность подписки на интересующих авторов.
Восстановление пароля в случае утери доступа.

## Как запустить проект на тестовом сервере:
<details><summary> Linux </summary>

Клонировать репозиторий, перейти в директорию с проектом.

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 yatube/manage.py migrate
```

Запустить проект:

```
python3 yatube/manage.py runserver
```
Сайт будет доступен по адресу:
```
http://127.0.0.1:8000/
```
</details>

<details><summary> Windows </summary>

Клонировать репозиторий, перейти в директорию с проектом.

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python yatube/manage.py migrate
```

Запустить проект:

```
python yatube/manage.py runserver
```
Сайт будет доступен по адресу:
```
http://127.0.0.1:8000/
```
</details>

## Автор
Автор проета - Тихомиров Алексей
Telegram: @tav_ajax