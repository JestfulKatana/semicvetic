# План сдачи редизайна «Семицветик»

**Дата составления:** 2026-04-17
**Автор:** techlead
**Статус:** ready for auto-run

## 1. Цель и критерии сдачи

Довести сайт `https://cvetik.analystexe.ru/` до соответствия макетам Figma и сдать заказчику (Давыд Сапожников). Работа идёт без надзора пользователя — оркестрация через команду `frontend` / `backend` / `qa`.

Критерии готовности (DoD всего проекта):
- [ ] Все четыре ключевые страницы (`/`, `/o-centre/`, `/pedagogi/`, `/programmy/`) совпадают с соответствующими макетами по структуре, цветам, шрифтам, радиусам.
- [ ] Детальная страница программы (`/<slug>/`) совпадает с макетом `О программе.png` (блоки: расписание с группами, сравнительная таблица, фото-стрип).
- [ ] Все новые блоки адаптивны: `@media (max-width: 860px)` и `520px`.
- [ ] QA-прогон локально зелёный: нет 500, заявка через `/api/lead` работает, honeypot ловит ботов.
- [ ] Прод-деплой успешен: `curl /health` → `{"ok":true}`, главная отдаёт 200, `sitemap.xml` валиден.
- [ ] Нет 500 в логах gunicorn на проде в течение 5 минут после деплоя.

## 2. Текущее состояние

**Архитектура (стабильна):**
- Flask + SQLite + Jinja2 + один `main.css`.
- Контент как JSON-блоки в `Page.content_json` / `Program.landing_json`, рендер через `app/templates/components/render_block.html`.
- Сидирование: `app/demo_seed.py` (первичное) + `update_content.py` (перезапись блоков, безопасно запускать).
- Дизайн-система: палитра и радиусы в `:root` (`main.css:1-42`).

**Реализовано (по `update_content.py`):**
- Главная: hero + programs_grid + top_programs + trust_bar (лепестки) + teachers_grid + how_it_works + form_strip + reviews_grid + gallery + cta_final + faq + contact_panel.
- О центре: hero (с stats_row) + rich_text + advantages + contact_panel.
- Каталог программ: hero + programs_grid (source=all_programs) + contact_panel.
- Педагоги: hero + teachers_grid (show_search + show_chips) + contact_panel.
- Детальная программа: hero + advantages + faq + reviews_grid + cta_final + contact_panel.
- Реальные контакты и адрес зашиты.

**Компоненты в `render_block.html`:** hero, trust_bar, top_programs, form_strip, programs_grid, advantages, results_banner, teachers_grid, reviews_grid, how_it_works, faq, timeline, compare_table, cta_final, gallery, events_grid, articles_grid, prices_table, contact_panel, rich_text (20 шт.).

**Модель данных:** `Program.category`, `Program.teacher`, `ScheduleSlot.group_name`, `ProgramSubject` уже есть. Фильтры по категориям на фронте — не реализованы, хотя поле есть.

**Git:** одна компрометированная коммит (`Initial Semicvetik box solution`), ~2200 строк изменений в рабочем дереве не закоммичено.

## 3. Недостающее (приоритизированный список)

### P0 — блокирующее сдачу
1. **Коммит текущего состояния** — сейчас всё в рабочем дереве, прод рассинхронизирован с репо.
2. **Детальная программа** (`/<slug>/`) — нет блоков из макета `О программе.png`: `program_schedule` (расписание с группами), `compare_table` (сравнение 3 колонки: «мы» vs «садик» vs «репетитор»), `photo_strip` (лента фото).
3. **Фильтры в `/programmy/`** — каталог не фильтруется по категории, хотя поле `Program.category` заполняется.
4. **Страница `/o-centre/`** — сейчас минимум (hero + rich_text + advantages + contact). В макете `О нас (1).png` — фото-блок, ценности-карточки (есть), статистика-лента (нужна).

### P1 — нужно для презентабельного вида
5. **Страница `/pedagogi/`** — фильтры по направлениям (chips есть, но JS не написан), поиск.
6. **Тонкая подгонка главной** — отступы hero, размер лепестков, мобильный breakpoint.
7. **Видео-секция** — сейчас `gallery` с `variant: "video"` рендерится как плейсхолдер, нужно реальное видео или аккуратная заглушка.

### P2 — nice to have
8. **Страница `/kontakty/`** — сейчас hero + contact_panel. Можно усилить картой и формой.
9. **Мероприятия / блог** — оставляем как есть, не входит в финальный проход.

## 4. План по итерациям

Итерации атомарные. `frontend` и `backend` в пределах одной итерации могут идти параллельно. `qa` — всегда после.

### Итерация 0: Санитария (5 мин)

- **Исполнитель:** techlead (сам)
- **Действия:** `git add` + коммит текущего состояния с осмысленным сообщением («figma redesign: home + partial pages»). `git status` должен быть чист перед следующими итерациями.
- **DoD:** рабочее дерево чисто, есть коммит в ветке `main`.
- **Время:** ~5 мин.

### Итерация 1: Детальная программа — схема + блоки (параллельно fe+be, затем qa)

- **Backend:** добавить в `render_block.html` и `update_content.py` три новых блока:
  - `program_schedule` — рендерит `data.groups[]` (title + slots[] с `day`/`time`). Источник: `source: "program_schedule"` → `hydrate_blocks` тянет `current_program.schedule_slots` и группирует по `group_name`.
  - `compare_table` — 3 колонки (`columns[]` с `title` + `items[]`). Статические данные в `update_content.py`.
  - `photo_strip` — полоса из N фото (`images[]`). Плейсхолдеры из `app/static/img/mockup/`.
  - Добавить эти блоки в `program_landing_blocks()` между `advantages` и `faq`.
  - `python update_content.py` → перезалить.
- **Frontend:** добавить CSS для `program_schedule`, `compare_table`, `photo_strip`. Использовать существующие переменные. Адаптив обязателен.
- **DoD:** `/podgotovka-k-shkole/` рендерит новые блоки без 500, верстка совпадает с `О программе.png` по структуре.
- **QA:** smoke все 4 детальные программы + проверка адаптива по CSS media-queries.
- **Время:** ~40 мин fe + ~25 мин be + 10 мин qa.

### Итерация 2: Каталог программ — фильтры по категориям

- **Backend:** убедиться, что у всех программ заполнена `category`. Если нет — дозаполнить через `update_content.py` (добавить маппинг slug→category).
- **Frontend:** добавить в `programs_grid` чипы-фильтры (когда `data.show_filters: true`). Минимальный JS в `app/static/js/main.js`: на клик по чипу — hide/show карточек по `data-category`. Default — «Все».
- **DoD:** `/programmy/` показывает чипы, клик фильтрует. Без JS (disabled) — все программы видны.
- **QA:** `curl /programmy/` → 200; визуально чипы есть; JS переключает.
- **Время:** ~30 мин fe + 10 мин be + 5 мин qa.

### Итерация 3: Страница «О центре» — ценности, статы, фото

- **Backend:** в `about_blocks()` добавить:
  - `stats_row` компонент (или переиспользовать `trust_bar` с варинтом) — 3 крупных числа из макета.
  - `gallery` или `photo_strip` для фото центра.
- **Frontend:** при необходимости новый вариант CSS для статов О-центра (2–3 крупных числа в линию, без цветных лепестков).
- **DoD:** `/o-centre/` по структуре совпадает с `О нас (1).png`.
- **QA:** smoke + визуальная сверка с компактным макетом.
- **Время:** ~25 мин fe + 15 мин be + 5 мин qa.

### Итерация 4: Страница «Педагоги» — фильтры + поиск

- **Frontend:** JS-фильтрация по chip-категориям (похоже на итерацию 2, но для teachers). Поиск по имени/роли — по `input[type=search]`.
- **Backend:** если нужно — добавить `Teacher.category` или использовать `Teacher.specialization` для фильтрации. Обсудить внутри итерации; по умолчанию использовать существующее поле.
- **DoD:** `/pedagogi/` — поиск и чипы работают, все педагоги видны по умолчанию.
- **QA:** smoke + адаптив.
- **Время:** ~30 мин fe + 10 мин be + 5 мин qa.

### Итерация 5: Полировка + предпрод QA

- **Frontend:** пройти по главной, подогнать отступы, мобильный breakpoint, проверить, что video-секция (или её заглушка) выглядит опрятно. Убрать дубли/мусор.
- **QA:** полный чеклист (раздел 6 этого плана + ниже).
- **DoD:** QA-лог со статусом `passed`, 0 P0-багов, ≤2 P1.
- **Время:** ~20 мин fe + 20 мин qa.

### Итерация 6: Деплой + пост-деплой проверки

- **Исполнитель:** techlead.
- **Действия:** см. разделы 7 и 8.
- **DoD:** прод зелёный, отчёт пользователю.
- **Время:** ~15 мин.

## 5. Консультации с командой

*(Кастомные subagent_type пока не зарегистрированы в сессии — имитирую консультацию, опираясь на роль-файлы.)*

### frontend сказал:
- Главная готова на ~90%, но в макете `Главная-1.png` контакт-панель выглядит более цельно (карта + форма + адрес единым блоком) — проверить `.contact-panel` на адаптиве.
- Для детальной программы нужны три новых CSS-блока: `.program-schedule` (акцентные карточки групп с временами), `.compare-grid` (3 равные колонки с bullets), `.photo-strip` (горизонтальный скролл на мобилке, сетка на десктопе).
- В `teachers_grid` уже есть чипы, но без JS они декоративные — нужен минимальный `main.js` на фильтрацию.
- Все новые блоки должны использовать `--surface`, `border-radius: 28px`, `box-shadow: var(--shadow)`.
- **Риск:** `.compact-grid-3` ломается на 860px — нужно явное правило `grid-template-columns: 1fr` для `compare-grid` на мобилке.

### backend сказал:
- `ScheduleSlot.group_name` уже есть — для `program_schedule` нужно только добавить группировку в `hydrate_blocks` при `source: "program_schedule"`: `groupby(slots, key=group_name)` и собрать `[{title: group, slots: [...]}, ...]`.
- `compare_table` в render_block.html уже есть (проверил grep) — нужно только убедиться, что структура `data.columns[]` совместима, и использовать его в `program_landing_blocks()`.
- `photo_strip` — новый тип, достаточно массива `images[]` с URL. Плейсхолдеры нужно положить в `app/static/img/mockup/` (директория уже есть как untracked).
- Для фильтров по категориям — поле `Program.category` уже в модели. Нужно просто убедиться, что все программы в `demo_seed.py` имеют непустую `category`, иначе фильтры покажут пусто.
- **Риск:** SQLite в проде — если меняем модель (не меняем, только JSON-блоки), миграций не нужно. Но `update_content.py` на проде нужно запустить явно после деплоя.

### qa сказал:
- Smoke-URL: `/`, `/o-centre/`, `/pedagogi/`, `/programmy/`, `/podgotovka-k-shkole/`, `/logoped/`, `/anglijskij/`, `/rannee-razvitie/`, `/kontakty/`, `/sitemap.xml`, `/robots.txt`, `/health`, `/blog/<любой slug>/`.
- Регрессионный риск: главная уже живая — любые правки `render_block.html` могут сломать уже работающие блоки. Предлагаю после каждой итерации прогонять все smoke-URL, не только затронутые.
- `/api/lead` — тестить POST с валидным телефоном (ожидание 200), с honeypot (company=spam, ожидание 200 но lead не создался), с битым телефоном (400).
- На проде — обязательно WebFetch главной после деплоя, gunicorn логи `journalctl -u cvetik -n 50` на 500.
- **Риск:** если `hydrate_blocks` не обработает новый `source` — блок отрендерится с пустыми данными, но не упадёт. Проверить явно, что данные приходят.

## 6. Риски

1. **PNG-макеты > 1.5 МБ** — нельзя читать напрямую, компактные версии покрывают только главную и педагогов. Для `О программе.png` (1.9 МБ) — идём по описанию в памяти и по структуре макета из этого плана.
2. **Регрессия главной** — любое изменение `render_block.html` или `main.css` может сломать уже живые блоки. Мера: QA smoke после каждой итерации.
3. **SQLite на проде** — если случайно изменится модель, нужен ALTER TABLE. Меры: не трогаем модель, только JSON-блоки и CSS.
4. **Custom subagent_type не зарегистрированы в текущей сессии** — `.claude/agents/*.md` есть на диске, но рантайм их не подтянул. Следующая сессия должна быть перезапущена (или вызывать general-purpose с инлайн-персоной).
5. **Флуд логов** — много итераций, логи могут распухнуть. Каждая итерация пишет один лог, не больше.

## 7. Деплой

Команды в порядке выполнения:

```bash
# 0. Локально: убедиться, что всё закоммичено
cd /home/mironov/storage/mironov/semicvetic
git status                           # должно быть чисто
git push origin main

# 1. На прод-сервер
ssh root@45.141.102.227
cd /srv/cvetik-box
git pull origin main

# 2. Окружение
source .venv/bin/activate
pip install -r requirements.txt      # если менялись зависимости

# 3. Контент (если менялся update_content.py)
python update_content.py

# 4. Перезапуск сервиса
systemctl restart cvetik

# 5. Быстрый чек
curl -s https://cvetik.analystexe.ru/health
# → {"ok": true}
```

Ожидаемый даунтайм: 2–5 секунд при `systemctl restart`.

## 8. Пост-деплой проверки

- [ ] `curl -s https://cvetik.analystexe.ru/health` → `{"ok":true}`.
- [ ] `curl -s -o /dev/null -w "%{http_code}\n" https://cvetik.analystexe.ru/` → `200`.
- [ ] WebFetch главной — убедиться, что hero, programs_grid, trust_bar отрисовались.
- [ ] WebFetch `/o-centre/`, `/pedagogi/`, `/programmy/`, `/podgotovka-k-shkole/` — все `200`, есть ожидаемые блоки.
- [ ] `curl -s https://cvetik.analystexe.ru/sitemap.xml | head -30` — валидный XML, есть `<loc>` для всех страниц и программ.
- [ ] POST `/api/lead` с тестовым телефоном → `200` + `{"ok":true}`.
- [ ] `journalctl -u cvetik -n 50 --no-pager` на прод-сервере — нет 500, нет traceback.
- [ ] Отчитаться пользователю с ссылкой на прод и перечнем внесённых изменений.

## 9. Точка входа для следующей сессии

1. Прочитать этот файл.
2. Прочитать последний лог техлида: `ls -t .claude/logs/techlead/ | head -1`.
3. Если subagent_type не работают — использовать general-purpose Agent с инлайн-персоной (копировать роль из `.claude/agents/{frontend,backend,qa}.md` в системный промпт агента).
4. Начать с Итерации 0 (санитария/коммит), затем Итерация 1.
5. После каждой итерации — QA + лог + решение «идём дальше или откатываем».
6. После Итерации 5 — деплой по разделу 7.
