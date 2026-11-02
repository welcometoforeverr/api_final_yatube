# API для Yatube

REST API социальной сети для публикации дневниковых записей. Позволяет
читать и создавать посты, обсуждать их в комментариях, просматривать
сообщества и подписываться на авторов.

Стек: Python 3.10, Django 3.2, Django REST Framework, Simple JWT,
Djoser и SQLite. Контракт API находится в `yatube_api/static/redoc.yaml`.

## Установка и запуск в Windows PowerShell

```powershell
git clone https://github.com/welcometoforeverr/api_final_yatube.git
cd api_final_yatube
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd yatube_api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Для Linux/macOS окружение создаётся командой `python3.10 -m venv venv`
и активируется командой `source venv/bin/activate`.

Документация: <http://127.0.0.1:8000/redoc/>.
Администрирование пользователей, постов, групп, комментариев и подписок:
<http://127.0.0.1:8000/admin/>. Регистрация пользователей через API отсутствует.

## Авторизация и права

Получите пару JWT-токенов:

```http
POST /api/v1/jwt/create/
Content-Type: application/json

{"username": "leo", "password": "your-password"}
```

В ответе будут `access` и `refresh`. Передавайте access-токен в заголовке
`Authorization: Bearer <access>`. Обновление: `POST /api/v1/jwt/refresh/`
с телом `{"refresh": "<refresh>"}`. Проверка токена:
`POST /api/v1/jwt/verify/` с телом `{"token": "<access>"}`.

Анонимным пользователям доступны чтение постов, комментариев и групп.
Создание контента требует авторизации; автор назначается по токену.
Редактировать и удалять пост или комментарий может только его автор.
Группы доступны через API только для чтения. Подписки доступны только
авторизованным пользователям; каждый видит только свои подписки.

## Примеры запросов

Создание публикации (поле `group` и изображение необязательны):

```http
POST /api/v1/posts/
Authorization: Bearer <access>
Content-Type: application/json

{"text": "Моя первая запись", "group": 1}
```

```json
{
  "id": 1,
  "text": "Моя первая запись",
  "author": "leo",
  "image": null,
  "group": 1,
  "pub_date": "2026-11-02T12:00:00Z"
}
```

- `GET /api/v1/posts/` — список всех публикаций, новые первыми.
- `GET /api/v1/posts/?limit=10&offset=10` — страница публикаций;
  ответ содержит `count`, `next`, `previous`, `results`.
- `GET /api/v1/posts/1/` — отдельная публикация.
- `PUT/PATCH/DELETE /api/v1/posts/1/` — изменение или удаление своей записи.
- `GET /api/v1/groups/` и `GET /api/v1/groups/1/` — сообщества.
- `GET/POST /api/v1/posts/1/comments/` — комментарии; для создания
  передайте `{"text": "Спасибо за запись!"}`.
- `GET/PUT/PATCH/DELETE /api/v1/posts/1/comments/1/` — отдельный комментарий.
- `GET /api/v1/follow/` — собственные подписки.
- `GET /api/v1/follow/?search=leo` — поиск по имени автора среди подписок.
- `POST /api/v1/follow/` с телом `{"following": "leo"}` — подписка.

Повторная подписка и подписка на себя возвращают `400` с описанием ошибки.
Невалидный или отсутствующий токен при защищённой операции даёт `401`,
изменение чужого контента — `403`, отсутствующий объект — `404`.

## Проверка

Из корня репозитория в активированном окружении:

```powershell
pytest
python yatube_api/manage.py check
python yatube_api/manage.py makemigrations --check --dry-run
```

Коллекция для проверки HTTP-запросов лежит в `postman_collection/`.
Исходная заготовка и учебные тесты предоставлены Яндекс Практикумом.
