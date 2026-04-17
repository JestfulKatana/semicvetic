# Техническое саммари по ТЗ

## 1. Архитектура

- Flask + SQLite + Jinja2
- SSR-страницы без фронтенд-фреймворка
- хранение контента и заявок в SQLite
- коробка вынесена отдельно от старого Django-сайта
- проект развёрнут как отдельный сервис `cvetik-box.service`

## 2. Модель данных

Таблицы:

- `pages`
- `programs`
- `teachers`
- `schedule_slots`
- `program_subjects`
- `reviews`
- `leads`
- `events`
- `site_settings`
- отдельная таблица для админ-пользователя

Особенности:

- данные программ, страниц и посадочных блоков хранятся в JSON-полях
- лиды пишутся в SQLite
- проект seeded демо-данными

## 3. Компонентный рендер

- страницы рендерятся из массива блоков в БД
- рендер через `render_block.html`
- можно менять порядок блоков и данные без правки Python-кода

## 4. Деплой

- прод-каталог `/srv/cvetik-box`
- отдельный Unix socket
- отдельный systemd-юнит
- nginx переключен на новый сайт
- HTTPS через существующий сертификат домена
- вместо Docker — стек `systemd + gunicorn + nginx` (сервер слабый)

## 5. Мониторинг

Сделано частично:

- endpoint `/metrics` есть
- подготовлены docker-файлы и grafana/prometheus-шаблоны в репозитории

Не доведено:

- monitoring stack на сервере не поднят
- Docker не ставился
- Grafana/Prometheus/Alertmanager не развёрнуты

## 6. Безопасность

Сделано:

- сайт за nginx
- HTTPS
- `/metrics` закрыт снаружи
- базовый rate limit на лиды

Не доведено:

- CSP headers
- fail2ban
- production backup-rotation для SQLite
- 2FA для админки

## 7. Что не сделано

- Alembic-миграции
- визуальный редактор блоков страниц
- загрузка фото педагогов через UX уровня CMS
- Grafana dashboards в бою
- Alertmanager Telegram alerts
- Nginx exporter / Node exporter / Loki
- автоматические бэкапы SQLite и статики
- CI/CD
- полный production security hardening
