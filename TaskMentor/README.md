# TaskMentor — умный помощник для управления клиентами

TaskMentor — дипломный Django-проект: веб-приложение для учителей/коучей и их учеников.
Система помогает назначать задачи, отслеживать прогресс и использовать интеграции (Google Calendar, push-уведомления).

Подробная бизнес-логика проекта описана в `docs/logic.md`.

---

## Функционал

- Регистрация/вход (учитель и ученик — разные роли и разные кабинеты)
- Заявка ученика учителю и подтверждение учителем
- Управление задачами и приоритетами
- Сортировки задач в кабинете ученика (4 режима)
- Вход через Google (OAuth) для уже созданных пользователей
- (Опционально) push-уведомления через Firebase / Web Push
- (Опционально) интеграция с Google Calendar

---

## Стек технологий

- Python / Django
- SQLite
- HTML / CSS / Bootstrap / JavaScript
- Google OAuth 2.0
- (Опционально) Firebase Cloud Messaging, Web Push

---

## Установка и запуск

1) **Клонировать репозиторий:**
```bash
git clone <repo_url>
cd <repo_folder>
```
2) **Создать и активировать виртуальное окружение:**
```bash
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
Mac/Linux:
```bash
source .venv/bin/activate
```
3) **Установить зависимости:**
```bash
pip install -r requirements.txt
```
4) **Применить миграции:**
```bash
python manage.py migrate
```
5) **Запустить сервер:**
```bash
python manage.py runserver
```

---

## Переменные окружения (.env)

Проект использует переменные окружения через os.getenv().

Пример .env:
```env
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
WEBPUSH_PUBLIC_KEY=
WEBPUSH_PRIVATE_KEY=
FIREBASE_SERVICE_ACCOUNT_PATH=
FCM_ENABLED=true
```

---

## Google OAuth (вход без регистрации)

**Через Google OAuth нельзя зарегистрироваться “с нуля”.**

Правило:
- пользователь должен быть предварительно зарегистрирован в TaskMentor как учитель или ученик
- если выбранный Google e-mail отсутствует в базе TaskMentor — вход не выполнится

---

## Firebase / FCM (опционально):

Для отправки push-уведомлений нужен собственный Firebase проект и service account JSON:
 
- FIREBASE_SERVICE_ACCOUNT_PATH — путь к service-account JSON на вашей машине.
- Если куратор хочет протестировать push, он создаёт свой Firebase проект и прописывает свой путь.

**Если push не требуется для проверки, можно отключить:**
- FCM_ENABLED=false

---

## Автор

Anton B.  
Django Diploma Project, 2026  
TaskMentor — Smart Client Management Assistant


