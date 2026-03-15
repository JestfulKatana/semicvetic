from __future__ import annotations

from datetime import date, timedelta

from .extensions import db
from .models import (
    AdminUser,
    Event,
    Page,
    Program,
    ProgramSubject,
    Review,
    ScheduleSlot,
    SiteSetting,
    Teacher,
)


def page_blocks_home():
    return [
        {
            "component": "hero",
            "data": {
                "title": "Детский центр Семицветик",
                "subtitle": "Понятная коробка для центра развития: страницы, программы, педагоги, цены, события и заявки уже собраны в рабочий контур.",
                "stats": [
                    {"value": "2009", "label": "год старта"},
                    {"value": "1500+", "label": "выпускников"},
                    {"value": "10+", "label": "программ"},
                ],
                "cta_text": "Записаться на пробное занятие",
                "cta_target": "lead-form",
                "eyebrow": "Сергиев Посад",
            },
        },
        {
            "component": "trust_bar",
            "data": {
                "items": [
                    {"icon": "01", "text": "SEO-ready SSR на Jinja2"},
                    {"icon": "02", "text": "Контент из SQLite"},
                    {"icon": "03", "text": "Заявки сразу в Telegram"},
                    {"icon": "04", "text": "Админка на /admin/"},
                ]
            },
        },
        {
            "component": "form_strip",
            "data": {
                "title": "Нужно быстро показать решение заказчику?",
                "subtitle": "Оставьте телефон и мы смоделируем путь родителя от главной страницы до заявки.",
                "color": "mint",
                "source_block": "hero_cta",
            },
        },
        {
            "component": "programs_grid",
            "data": {
                "title": "Ключевые программы",
                "subtitle": "Карточки уже завязаны на цену, возраст, преподавателя и расписание.",
                "source": "featured_programs",
                "limit": 4,
            },
        },
        {
            "component": "advantages",
            "data": {
                "title": "Почему коробка годится под следующий центр",
                "items": [
                    {"icon": "A", "title": "Контентный каркас", "text": "Страницы и лендинги собираются из JSON-блоков без правки шаблонов."},
                    {"icon": "B", "title": "Понятная навигация", "text": "Есть каталог программ, цены, педагоги, события, блог и контакты."},
                    {"icon": "C", "title": "SEO-база", "text": "SSR, meta, Open Graph, sitemap.xml, robots.txt и schema.org уже на месте."},
                    {"icon": "D", "title": "Контроль заявок", "text": "Каждая форма сохраняет лид с источником страницы и блока."},
                ],
            },
        },
        {
            "component": "teachers_grid",
            "data": {
                "title": "Команда, которую видно сразу",
                "subtitle": "Не прячем педагогов в футере: это отдельная понятная страница и мощный блок доверия.",
                "source": "all_teachers",
            },
        },
        {
            "component": "reviews_grid",
            "data": {
                "title": "Отзывы родителей",
                "source": "featured_reviews",
                "limit": 3,
            },
        },
        {
            "component": "how_it_works",
            "data": {
                "title": "Как проходит путь пользователя",
                "steps": [
                    {"icon": "1", "title": "Смотрит программу", "text": "Находит нужный возраст, формат и цену."},
                    {"icon": "2", "title": "Проверяет педагога", "text": "Сразу видит лицо, специализацию и опыт."},
                    {"icon": "3", "title": "Оставляет телефон", "text": "Форма короткая и не требует регистрации."},
                    {"icon": "4", "title": "Директор получает лид", "text": "Заявка уходит в SQLite и дублируется в Telegram."},
                ],
            },
        },
        {
            "component": "faq",
            "data": {
                "title": "Что уже можно показывать",
                "items": [
                    {"q": "Это уже рабочий сайт?", "a": "Да. Можно открыть страницы, посмотреть маршруты, протестировать форму и зайти в админку."},
                    {"q": "Это финальный дизайн?", "a": "Нет. Сейчас собран архитектурный каркас и UX-структура, на которые потом натянется визуальный дизайн."},
                    {"q": "Контент можно менять без разработчика?", "a": "Да. Программы, цены, тексты, события и блоки страниц редактируются через админку."},
                ],
            },
        },
        {
            "component": "cta_final",
            "data": {
                "title": "Готово к просмотру и обсуждению",
                "subtitle": "Откройте страницы, проверьте админку и походите по пользовательскому сценарию целиком.",
                "color": "peach",
                "phone": "+7 (926) 123-45-67",
                "source_block": "final_cta",
            },
        },
    ]


def program_landing(name: str, tagline: str):
    return [
        {
            "component": "hero",
            "data": {
                "source": "current_program",
                "eyebrow": "Программа центра",
                "title": name,
                "subtitle": tagline,
                "cta_text": "Записаться на пробное",
                "cta_target": "lead-form",
            },
        },
        {
            "component": "advantages",
            "data": {
                "title": "Что родители понимают с этой страницы",
                "items": [
                    {"icon": "01", "title": "Кому подходит", "text": "Возраст, длительность и формат показаны сразу в первом экране."},
                    {"icon": "02", "title": "Что входит", "text": "Предметы и результаты собраны в одном потоке, без скачков по сайту."},
                    {"icon": "03", "title": "Кто ведёт", "text": "Педагог связан с программой, поэтому доверие не теряется."},
                    {"icon": "04", "title": "Сколько стоит", "text": "Цена открыта и не спрятана в звонке менеджеру."},
                ],
            },
        },
        {
            "component": "timeline",
            "data": {
                "title": "Типовой прогресс ребёнка",
                "items": [
                    {"icon": "1", "title": "1 месяц", "text": "Адаптация к формату, диагностика навыков, понятный старт."},
                    {"icon": "2", "title": "2-3 месяц", "text": "Появляется регулярность, родители видят первые результаты."},
                    {"icon": "3", "title": "4-6 месяц", "text": "Закрепляются предметные навыки и самостоятельность."},
                ],
            },
        },
        {"component": "reviews_grid", "data": {"title": "Отзывы по программе", "source": "program_reviews"}},
        {
            "component": "cta_final",
            "data": {
                "title": "Пробное занятие можно оформить прямо со страницы программы",
                "subtitle": "Телефон, возраст ребёнка и сразу понятный источник лида в CRM-логике.",
                "color": "lavender",
                "source_block": "program_final_cta",
            },
        },
    ]


def seed_database() -> None:
    if SiteSetting.query.count():
        return

    settings = {
        "site_name": "Семицветик",
        "site_description": "Детский центр развития в Сергиевом Посаде. Готовая коробка сайта с программами, педагогами, ценами и заявками.",
        "phone_1": "+7 (926) 123-45-67",
        "phone_2": "+7 (496) 123-45-67",
        "address": "Сергиев Посад, ул. Вознесенская, 12",
        "hours": "Пн-Сб 09:00-20:00",
        "hero_title": "Сайт детского центра, который можно показывать сразу",
        "hero_subtitle": "Без финального дизайна, но с рабочей логикой контента, SEO и заявок.",
        "yandex_metrika_id": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "years_working": "17",
        "graduates": "1500+",
        "programs_count": "10+",
    }
    for key, value in settings.items():
        db.session.add(SiteSetting(key=key, value=value))

    teacher_1 = Teacher(
        name="Ирина Бурова",
        role="Педагог подготовки к школе",
        specialization="Чтение, математика, развитие логики",
        bio="15 лет помогает детям мягко входить в учебную нагрузку и формировать уверенность перед школой.",
        emoji="🎓",
        sort_order=1,
    )
    teacher_2 = Teacher(
        name="Мария Степанова",
        role="Логопед-дефектолог",
        specialization="Речь, звукопроизношение, фонематический слух",
        bio="Работает с речевыми задержками и помогает родителям видеть динамику по этапам.",
        emoji="🗣️",
        sort_order=2,
    )
    teacher_3 = Teacher(
        name="Ольга Савельева",
        role="Педагог раннего развития",
        specialization="Сенсорика, внимание, запуск речи",
        bio="Собирает занятия так, чтобы ребёнок удерживал интерес и не уставал от формата.",
        emoji="🌱",
        sort_order=3,
    )
    db.session.add_all([teacher_1, teacher_2, teacher_3])
    db.session.flush()

    programs = [
        Program(slug="podgotovka-k-shkole", name="Подготовка к школе", tagline="Комплексная программа для детей 5–7 лет: чтение, математика, логика, письмо и уверенность перед школой.", description="Комплексная подготовка к школе в малых группах. Ребёнок постепенно осваивает чтение, математику, логику и учебную дисциплину.", emoji="📘", color="#F4B400", age_min=5, age_max=7, duration_min=90, frequency="2 раза в неделю", price=6800, price_unit="мес", has_landing=True, category="school", teacher_id=teacher_1.id, sort_order=1),
        Program(slug="logoped", name="Логопедия", tagline="Индивидуальные и мини-групповые занятия для постановки звуков и развития речи.", description="Диагностика речи, постановка звуков, упражнения на понимание и чистую речь.", emoji="🗣️", color="#6EC5FF", age_min=3, age_max=8, duration_min=45, frequency="1-2 раза в неделю", price=2200, price_unit="занятие", has_landing=True, category="speech", teacher_id=teacher_2.id, sort_order=2),
        Program(slug="anglijskij", name="Английский", tagline="Игровой английский для детей 4–9 лет с упором на речь и понимание на слух.", description="Учим через короткие игровые циклы, песни, карточки и небольшие диалоги.", emoji="🇬🇧", color="#85C88A", age_min=4, age_max=9, duration_min=60, frequency="2 раза в неделю", price=5400, price_unit="мес", has_landing=True, category="english", teacher_id=teacher_1.id, sort_order=3),
        Program(slug="rannee-razvitie", name="Раннее развитие", tagline="Мягкий старт для малышей 1–3 лет: сенсорика, движение, внимание, первые слова.", description="Формат для самых маленьких: короткие смены активности, работа с родителями и развитие бытовых навыков.", emoji="🌈", color="#FF9E7A", age_min=1, age_max=3, duration_min=40, frequency="2 раза в неделю", price=4600, price_unit="мес", has_landing=True, category="early", teacher_id=teacher_3.id, sort_order=4),
    ]
    for program in programs:
        program.landing_blocks = program_landing(program.name, program.tagline)
        db.session.add(program)
    db.session.flush()

    for row in [
        (programs[0].id, "Лучики", "Вт / Чт", "17:30", "19:00"),
        (programs[0].id, "Звёздочки", "Сб", "10:00", "11:30"),
        (programs[1].id, "Индивидуально", "Пн-Пт", "по записи", "по записи"),
        (programs[2].id, "Starter", "Пн / Ср", "18:00", "19:00"),
        (programs[3].id, "Малыши", "Вт / Пт", "11:00", "11:40"),
    ]:
        db.session.add(ScheduleSlot(program_id=row[0], group_name=row[1], day_of_week=row[2], time_start=row[3], time_end=row[4]))

    for row in [
        (programs[0].id, "Чтение", "2 раза в неделю", "📖"),
        (programs[0].id, "Математика", "2 раза в неделю", "🔢"),
        (programs[0].id, "Логика", "1 раз в неделю", "🧩"),
        (programs[1].id, "Постановка звуков", "индивидуально", "🎤"),
        (programs[1].id, "Развитие речи", "каждое занятие", "💬"),
        (programs[2].id, "Игровой словарь", "каждое занятие", "🗺️"),
        (programs[3].id, "Сенсорика", "каждое занятие", "🧸"),
    ]:
        db.session.add(ProgramSubject(program_id=row[0], name=row[1], frequency=row[2], emoji=row[3]))

    db.session.add_all([
        Review(author_name="Анна М.", author_initials="АМ", child_info="дочь Полина, выпуск 2025", text="Шли за подготовкой к школе, а получили ещё и уверенность ребёнка. На сайте сразу было понятно, кто ведёт курс и сколько он стоит.", rating=5, program_id=programs[0].id),
        Review(author_name="Екатерина С.", author_initials="ЕС", child_info="сын Артём, 6 лет", text="По логопедии понравилось, что можно увидеть путь занятий и быстро оставить заявку без длинной анкеты.", rating=5, program_id=programs[1].id),
        Review(author_name="Наталья К.", author_initials="НК", child_info="дочь Лиза, 2 года", text="Страница раннего развития отвечает на все базовые вопросы родителей: возраст, формат, педагог, цена и что будет на занятиях.", rating=5, program_id=programs[3].id),
    ])

    db.session.add_all([
        Event(type="event", title="День открытых дверей", slug="den-otkrytyh-dverej", excerpt="Покажем аудитории, как устроены занятия, познакомим с педагогами и ответим на вопросы родителей.", content="### Что будет\n\n- мини-экскурсия\n- знакомство с программами\n- ответы на вопросы родителей", category="open_day", event_date=date.today() + timedelta(days=6), event_time="11:00-13:00"),
        Event(type="event", title="Бесплатная диагностика готовности к школе", slug="diagnostika-gotovnosti-k-shkole", excerpt="Разберём сильные и слабые стороны ребёнка и предложим программу подготовки.", content="### Кому подойдёт\n\nДля детей 5-7 лет перед поступлением в школу.", category="diagnostic", event_date=date.today() + timedelta(days=10), event_time="16:00-19:00"),
        Event(type="article", title="Как понять, что ребёнок готов к подготовке к школе", slug="kak-ponyat-chto-rebenok-gotov-k-podgotovke-k-shkole", excerpt="Короткий гайд для родителей: какие навыки уже должны быть, а какие можно спокойно развивать в центре.", content="## На что смотреть\n\n1. Удерживает внимание 15-20 минут.\n2. Слышит инструкцию и выполняет её.\n3. Проявляет интерес к буквам, числам и заданиям.\n\n## Что не является проблемой\n\nНельзя ждать идеальной готовности: часть навыков ребёнок как раз и добирает на занятиях.", category="seo"),
        Event(type="article", title="Зачем странице программы открытая цена и педагог", slug="zachem-stranice-programmy-otkrytaya-cena-i-pedagog", excerpt="Разбор конверсионной логики сайта детского центра: что сокращает сомнения родителей до звонка.", content="## Главное\n\nРодители не хотят собирать сайт как пазл. Цена, педагог, возраст и результаты должны быть рядом.", category="seo"),
    ])

    pages = [
        Page(slug="home", title="Главная", meta_title="Семицветик | Коробочный сайт детского центра", meta_description="Рабочий прототип коробочного сайта детского центра: программы, педагоги, цены, блог и формы записи.", hero_subtitle="Коробка, которую можно открыть и показать сразу.", sort_order=0),
        Page(slug="programmy", title="Программы", meta_title="Программы | Семицветик", meta_description="Каталог программ центра с ценами, возрастом, расписанием и быстрым переходом на посадочные страницы.", hero_subtitle="Хаб всех программ и услуг центра.", sort_order=1),
        Page(slug="pedagogi", title="Педагоги", meta_title="Педагоги | Семицветик", meta_description="Команда центра, роли, специализация и связь с программами.", hero_subtitle="Педагоги как отдельный слой доверия.", sort_order=2),
        Page(slug="o-centre", title="О центре", meta_title="О центре | Семицветик", meta_description="История центра, подход к обучению, цифры, атмосфера и путь ребёнка.", hero_subtitle="Страница, которая объясняет, почему центру можно доверять.", sort_order=3),
        Page(slug="ceny", title="Цены", meta_title="Цены | Семицветик", meta_description="Открытая таблица цен и расписания по программам.", hero_subtitle="Цены не спрятаны за звонком.", sort_order=4),
        Page(slug="meropriyatiya", title="Мероприятия", meta_title="Мероприятия и статьи | Семицветик", meta_description="События центра и статьи для SEO-трафика.", hero_subtitle="События для заявок и статьи для органики.", sort_order=5),
        Page(slug="kontakty", title="Контакты", meta_title="Контакты | Семицветик", meta_description="Телефоны, адрес, режим работы и быстрая форма записи.", hero_subtitle="Короткий путь до звонка или заявки.", sort_order=6),
    ]

    pages[0].blocks = page_blocks_home()
    pages[1].blocks = [
        {"component": "hero", "data": {"title": "Программы центра", "subtitle": "Хаб-страница, которая собирает все программы, возрастные группы, цены и переходы на посадочные.", "cta_text": "Оставить телефон", "cta_target": "lead-form", "eyebrow": "Каталог"}},
        {"component": "programs_grid", "data": {"title": "Все программы", "subtitle": "Карточки уже привязаны к цене, возрасту и основному педагогу.", "source": "all_programs"}},
        {"component": "compare_table", "data": {"title": "Почему родителям проще принять решение", "columns": ["Что важно", "На этой коробке", "Обычный хаотичный сайт"], "rows": [["Цены", "Открыты на карточках и в таблице", "Часто только по звонку"], ["Педагоги", "Есть отдельная страница и связь с программой", "Разбросаны по сайту"], ["Заявка", "Форма на каждом ключевом экране", "Одна форма внизу"], ["SEO", "Страницы рендерятся на сервере", "Много скрытого контента"]]}},
        {"component": "cta_final", "data": {"title": "Можно пройти путь родителя целиком", "subtitle": "Каталог -> программа -> форма записи.", "color": "mint", "source_block": "programs_hub_cta"}},
    ]
    pages[2].blocks = [
        {"component": "hero", "data": {"title": "Педагоги центра", "subtitle": "Родитель должен увидеть не только программу, но и человека, который будет работать с ребёнком.", "cta_text": "Записаться на консультацию", "cta_target": "lead-form", "eyebrow": "Команда"}},
        {"component": "teachers_grid", "data": {"title": "Ключевые педагоги", "source": "all_teachers"}},
        {"component": "results_banner", "data": {"quote": "В детском центре доверие продаёт лучше любых общих слов.", "author": "Принцип этой коробки", "stats": [{"value": "3", "label": "педагога в демо"}, {"value": "4", "label": "программы связаны"}, {"value": "1", "label": "админка для редактирования"}]}},
    ]
    pages[3].blocks = [
        {"component": "hero", "data": {"title": "О центре", "subtitle": "Страница собирает историю, подход, цифры и атмосферу центра в одном потоке.", "cta_text": "Оставить телефон", "cta_target": "lead-form", "eyebrow": "История"}},
        {"component": "rich_text", "data": {"title": "Что здесь важно", "content": "С 2009 года центр работает с детьми от 1 до 12 лет. В коробке уже предусмотрены страницы для программ, педагогов, мероприятий, цен и блога. Это не одноразовая посадочная, а переносимый шаблон."}},
        {"component": "timeline", "data": {"title": "Как центр растёт вместе с ребёнком", "items": [{"icon": "1", "title": "1-3 года", "text": "Раннее развитие и запуск базовых навыков."}, {"icon": "2", "title": "4-5 лет", "text": "Английский, логика, развитие речи и уверенности."}, {"icon": "3", "title": "5-7 лет", "text": "Подготовка к школе и диагностика готовности."}]}},
        {"component": "gallery", "data": {"title": "Что потом ляжет в дизайн", "images": [{"emoji": "🏫", "label": "Фотографии центра"}, {"emoji": "👩‍🏫", "label": "Педагоги и занятия"}, {"emoji": "🎨", "label": "Работы детей"}, {"emoji": "🎉", "label": "Мероприятия и праздники"}]}},
    ]
    pages[4].blocks = [
        {"component": "hero", "data": {"title": "Цены", "subtitle": "Открытая таблица цен и регулярности занятий. Без скрытых условий и обязательного звонка.", "cta_text": "Получить консультацию", "cta_target": "lead-form", "eyebrow": "Стоимость"}},
        {"component": "prices_table", "data": {"title": "Текущие цены и расписание", "source": "all_prices"}},
    ]
    pages[5].blocks = [
        {"component": "hero", "data": {"title": "Мероприятия и статьи", "subtitle": "События дают быстрые лиды, статьи закрывают SEO-запросы родителей.", "cta_text": "Оставить заявку", "cta_target": "lead-form", "eyebrow": "Контент-маркетинг"}},
        {"component": "events_grid", "data": {"title": "Ближайшие мероприятия", "source": "all_events"}},
        {"component": "articles_grid", "data": {"title": "Статьи для органического трафика", "source": "all_articles"}},
    ]
    pages[6].blocks = [
        {"component": "hero", "data": {"title": "Контакты", "subtitle": "Страница не заставляет искать телефон в футере: всё ключевое вынесено наверх.", "cta_text": "Заказать звонок", "cta_target": "lead-form", "eyebrow": "Связь"}},
        {"component": "contact_panel", "data": {"title": "Как связаться", "source": "contact_data"}},
        {"component": "cta_final", "data": {"title": "Оставьте телефон и мы перезвоним", "subtitle": "Форма такая же, как и на остальных ключевых страницах.", "color": "mint", "source_block": "contacts_cta"}},
    ]
    db.session.add_all(pages)

    admin = AdminUser(username="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    db.session.commit()
