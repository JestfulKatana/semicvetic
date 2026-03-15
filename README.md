# Semicvetik Box

Коробочное решение для сайта детского центра на `Flask + SQLite + Jinja2`.

Что уже есть:

- рабочие страницы: главная, программы, программа, педагоги, о центре, цены, мероприятия, контакты, блог;
- JSON-компоненты страниц из базы;
- админка на `/admin/`;
- сохранение лидов через `/api/lead`;
- `robots.txt`, `sitemap.xml`, schema.org;
- Docker-контур с `nginx + prometheus + grafana + alertmanager`.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
flask --app wsgi.py run
```

Открыть:

- сайт: `http://127.0.0.1:5000/`
- админка: `http://127.0.0.1:5000/admin/`
- логин: `admin`
- пароль: `admin123`

## Docker

```bash
Copy-Item .env.example .env
docker compose up --build
```

Открыть:

- сайт: `http://127.0.0.1:8080/`
- grafana: `http://127.0.0.1:3000/`
- prometheus: `http://127.0.0.1:9090/`

