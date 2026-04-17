"""Update page blocks and program landings in the existing DB to match Figma mockups.

Usage:
    python update_content.py            # updates pages, programs, settings

Safe to re-run: always overwrites page.blocks / program.landing_blocks.
Keeps existing teacher/review/event data intact.
"""
from __future__ import annotations

from app import create_app
from app.extensions import db
from app.models import Page, Program, ScheduleSlot, SiteSetting, Teacher


def home_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Детский центр, где\u00a0главное\u00a0— развивающая среда и\u00a0забота о\u00a0ребёнке",
                "subtitle": "",
                "stats": [
                    {"value": "15\u00a0лет", "label": "Работаем и\u00a0развиваем детей в\u00a0Сергиевом Посаде"},
                    {"value": "10\u00a0лет", "label": "Средний стаж у\u00a0педагогов"},
                    {"value": "3000+", "label": "Выпускников учатся в\u00a0школах, лицеях, гимназиях"},
                ],
                "cta_text": "Записаться",
                "cta_target": "contact-panel",
                "source_block": "hero",
            },
        },
        {
            "component": "programs_grid",
            "data": {"title": "Развивающие программы", "subtitle": "Почему выбирают нас?", "source": "featured_programs", "limit": 4},
        },
        {
            "component": "top_programs",
            "data": {
                "title": "Топ-программы",
                "subtitle": "Другие программы нашего центра",
                "tabs": [
                    {
                        "slug": "anglijskij",
                        "name": "Английский язык",
                        "tags": ["5–15 лет", "1 час", "2–5 занятий в неделю"],
                        "description": "Разговорный английский, лексика, грамматика, фонетика, подготовка к\u00a0олимпиадам Junior Jack",
                        "groups": [
                            {"title": "Группа 5–6 лет, малыши", "slots": [
                                {"day": "Среда", "time": "18:00–19:00"},
                                {"day": "Суббота", "time": "10:00–11:00"},
                            ]},
                            {"title": "Группа 1 класс, малыши", "slots": [
                                {"day": "Понедельник\u00a0– Четверг", "time": "16:00–17:00"},
                            ]},
                            {"title": "Группа 2 класс, углублённый уровень", "slots": [
                                {"day": "Вторник\u00a0– Пятница", "time": "15:00–16:00"},
                            ]},
                            {"title": "Группа 3 класс, углублённый уровень", "slots": [
                                {"day": "Вторник\u00a0– Четверг", "time": "17:00–18:00"},
                            ]},
                            {"title": "Группа 4,5 класс, углублённый уровень", "slots": [
                                {"day": "Вторник\u00a0– Пятница", "time": "16:00–17:00"},
                            ]},
                            {"title": "Группа 5,6 класс, продвинутый уровень", "slots": [
                                {"day": "Вторник\u00a0– Четверг", "time": "18:00–19:00"},
                            ]},
                            {"title": "Группа 7–9 класс, продвинутый уровень", "slots": [
                                {"day": "Понедельник", "time": "17:00–18:00"},
                                {"day": "Пятница", "time": "18:00–19:30"},
                            ]},
                        ],
                        "teachers": ["#f59e40", "#6359c2", "#db5eb4"],
                        "teachers_count": "4 педагога",
                        "teachers_role": "Учителя начальной школы, психологи",
                        "price": "800–900\u00a0₽/занятие",
                    },
                    {"slug": "rannee-razvitie", "name": "Вместе с\u00a0мамой", "tags": ["1–3 года"], "description": "Малышам и\u00a0мамам\u00a0— сенсорика, пальчиковые игры, первые\u00a0слова.", "groups": [{"title": "Группа утренняя", "slots": [{"day": "Вт, Пт", "time": "11:00–11:40"}]}], "teachers": ["#85c88a"], "teachers_count": "1 педагог", "teachers_role": "Специалист раннего развития", "price": "от\u00a04\u00a0600\u00a0₽/мес"},
                    {"slug": "izostudia", "name": "Изостудия и\u00a0Лепка", "tags": ["4–10 лет"], "description": "Рисование, аппликация, лепка\u00a0— творчество как способ говорить о\u00a0себе.", "groups": [{"title": "Группа творческая", "slots": [{"day": "Сб", "time": "12:00–13:00"}]}], "teachers": ["#db5eb4"], "teachers_count": "1 педагог", "teachers_role": "Педагог\u00a0изо и\u00a0ДПИ", "price": "от\u00a03\u00a0400\u00a0₽/мес"},
                    {"slug": "podgotovka-k-shkole", "name": "Программа «Отличник»", "accent": True, "tags": ["5–7 лет"], "description": "Комплексная подготовка к\u00a0школе с\u00a0упором на\u00a0самостоятельность.", "groups": [{"title": "Группа Лучики", "slots": [{"day": "Вт, Чт", "time": "17:30–19:00"}]}, {"title": "Группа Звёздочки", "slots": [{"day": "Сб", "time": "10:00–11:30"}]}], "teachers": ["#f59e40", "#6359c2"], "teachers_count": "2 педагога", "teachers_role": "Учителя начальных классов", "price": "от\u00a06\u00a0800\u00a0₽/мес"},
                    {"slug": "detskij-lager", "name": "Детский лагерь", "tags": ["5–12 лет"], "description": "Тематические смены: творчество, спорт, английский, квесты.", "groups": [{"title": "Летняя смена", "slots": [{"day": "Пн\u00a0– Пт", "time": "9:00–14:00"}]}], "teachers": ["#4a8df5", "#db5eb4", "#85c88a"], "teachers_count": "3 педагога", "teachers_role": "Вожатые и\u00a0педагоги центра", "price": "от\u00a08\u00a0900\u00a0₽/смена"},
                ],
            },
        },
        {
            "component": "trust_bar",
            "data": {
                "title": "15\u00a0лет растим счастливых детей",
                "items": [
                    {"value": "15\u00a0лет", "label": "Работаем и\u00a0развиваем детей в\u00a0Сергиевом Посаде"},
                    {"value": "~1,5\u00a0ч", "label": "гарантированного живого развития без\u00a0смартфонов"},
                    {"value": ">70%", "label": "детей из\u00a0детского сада приходит за\u00a0дополнительными занятия"},
                    {"value": "98%", "label": "Детей идут с\u00a0удовольствием в\u00a0клуб"},
                    {"value": "10%", "label": "скидка предоставляется детям участников СВО и\u00a0вторым детям в\u00a0семье"},
                    {"value": "100%", "label": "Активно участвуют в\u00a0спектаклях, квестах, мастер-классах и\u00a0летнем лагере"},
                    {"value": ">80%", "label": "рекомендуют друзьям и\u00a0приводят младших сестер и\u00a0братьев"},
                ],
            },
        },
        {
            "component": "teachers_grid",
            "data": {
                "title": "Педагоги, которым доверяют",
                "subtitle": "Ведут учителя с\u00a0высшим педагогическим образованием",
                "source": "all_teachers",
                "show_chips": True,
                "limit": 2,
                "show_all_button": True,
            },
        },
        {
            "component": "how_it_works",
            "data": {
                "title": "Место, где раскрываются таланты",
                "subtitle": "В\u00a0отличие от\u00a0стандартного присмотра в\u00a0детском саду, Семицветик предлагает системное образование и\u00a0коррекционную поддержку, которые развивают медалистов и\u00a0лицеистов города",
                "steps": [
                    {"icon": "01", "image": "img/figma/place/group-small.png", "title": "До\u00a08\u00a0детей в\u00a0группе", "text": "У\u00a0нас учатся группы по\u00a08\u00a0детей, в\u00a0отличие от\u00a0садов, где занимаются 25–30 детей. Учитель уделяет время каждому."},
                    {"icon": "02", "image": "img/figma/place/teachers.png", "title": "Учителя начальных классов", "text": "Базовые знания закладывают школьные учителя с\u00a0наградами и\u00a0опытом. Ребёнок будет заранее готов к\u00a0учёбе в\u00a0школе."},
                    {"icon": "03", "image": "img/figma/place/psycho-speech.png", "title": "Психолог\u00a0+ логопед", "text": "Видим ребёнка целиком: развитие, речь, поведение. Если\u00a0заметим особенности\u00a0— скажем сразу и\u00a0поможем."},
                    {"icon": "04", "image": "img/figma/place/all-in-one.png", "title": "Всё\u00a0в\u00a0одном месте", "text": "Чтение, математика, англ.\u00a0яз., изо, психология, логопедия."},
                ],
            },
        },
        {"component": "form_strip", "data": {"title": "Давайте знакомиться!", "subtitle": "Оставьте телефон, и\u00a0убедитесь сами, почему нам\u00a0доверяют более 3000\u00a0семей", "color": "purple", "source_block": "cta_strip"}},
        {"component": "reviews_grid", "data": {"title": "Что говорят родители", "subtitle": "15\u00a0лет истории успеха в\u00a0каждом отзыве", "source": "featured_reviews", "limit": 1}},
        {"component": "gallery", "data": {"title": "Жизнь нашего центра в\u00a0одном видео", "subtitle": "Короткий ролик о\u00a0том, как\u00a0растут наши «маленькие звёздочки»", "variant": "video"}},
        {"component": "cta_final", "data": {"title": "Ответим на\u00a0вопросы по\u00a0телефону и\u00a0пригласим в\u00a0детский клуб на\u00a0экскурсию", "subtitle": "", "color": "green", "source_block": "final_cta"}},
        {"component": "gallery", "data": {"variant": "strip"}},
        {"component": "faq", "data": {"title": "Родители часто спрашивают", "items": [
            {"q": "Как\u00a0долго работает ваш\u00a0центр?", "a": "Центр работает уже\u00a0более 15\u00a0лет. За\u00a0это\u00a0время мы\u00a0подготовили более 3000\u00a0выпускников, многие из\u00a0которых закончили школу с\u00a0золотыми медалями."},
            {"q": "Где\u00a0вы\u00a0находитесь и\u00a0как\u00a0с\u00a0вами связаться?", "a": "Московская область, г.\u00a0Сергиев Посад, ул.\u00a0Воробьёвская, д.\u00a016А, 2\u00a0этаж. Телефон: 8\u00a0(926)\u00a0366-57-87."},
            {"q": "Как\u00a0именно найти вход в\u00a0ваш\u00a0центр?", "a": "Вход со стороны проспекта Красной Армии, 2\u00a0этаж. Ориентир — вывеска «Семицветик»."},
            {"q": "Можно\u00a0ли\u00a0в\u00a0«Семицветике» отметить День рождения ребёнка?", "a": "Да, мы\u00a0организуем праздники для\u00a0детей. Свяжитесь с\u00a0нами для\u00a0уточнения деталей."},
            {"q": "Проводятся\u00a0ли\u00a0в\u00a0центре занятия в\u00a0период школьных каникул или\u00a0летом?", "a": "Да, у\u00a0нас работает летний лагерь и\u00a0проводятся занятия в\u00a0каникулы."},
            {"q": "Предусмотрены\u00a0ли\u00a0льготы для\u00a0семей, где\u00a0занимаются двое детей?", "a": "Да, для\u00a0второго ребёнка в\u00a0семье предоставляется скидка 10%. Также скидка действует для\u00a0детей участников СВО."},
        ]}},
        {
            "component": "contact_panel",
            "data": {
                "title": "Ждём вас в\u00a0Семицветике",
                "variant": "compact",
                "source": "contact_data",
                "gallery": [
                    "img/figma/gallery/graduation.png",
                    "img/figma/gallery/balloons.png",
                    "img/figma/gallery/girl-gift.png",
                    "img/figma/gallery/girl-paints.png",
                    "img/figma/gallery/pumpkins.png",
                ],
            },
        },
    ]


def about_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Среда, где\u00a0дети растут разносторонними",
                "subtitle": "",
                "eyebrow": "О\u00a0центре",
                "cta_text": "Записаться",
                "cta_target": "contact-panel",
                "stats_row": [
                    {"value": "с\u00a02011\u00a0г.", "label": "Уже\u00a015\u00a0лет помогаем детям расти"},
                    {"value": "8", "label": "направлений обучения в\u00a0одном центре"},
                    {"value": "3000+", "label": "детей прошли у\u00a0нас\u00a0обучение"},
                ],
                "stats_row_note": "Московская область, Сергиев\u00a0Посад\u00a0— Воробьёвская, 16А, 2\u00a0этаж. Работаем ежедневно.",
            },
        },
        {
            "component": "rich_text",
            "data": {
                "variant": "about-lead",
                "content": (
                    "Сегодня «Семицветик»\u00a0— это\u00a0<span class=\"accent-violet\">команда профессиональных педагогов</span>, "
                    "современные программы обучения и\u00a0доказанные результаты. Но\u00a0главное\u00a0— это\u00a0по-прежнему "
                    "<span class=\"accent-orange\">любовь к\u00a0детям</span> и\u00a0вера в\u00a0их\u00a0безграничные возможности."
                ),
            },
        },
        {
            "component": "advantages",
            "data": {
                "title": "Наши ценности",
                "subtitle": "Принципы, которыми мы\u00a0руководствуемся в\u00a0работе с\u00a0детьми",
                "items": [
                    {"icon": "♥", "title": "Индивидуальный подход в\u00a0группе", "text": "Педагоги высшей категории с\u00a0многолетним опытом работы."},
                    {"icon": "✦", "title": "Мини-группы", "text": "Каждый ребёнок\u00a0— уникальная личность со\u00a0своими талантами и\u00a0особенностями: дисциплина, внимание."},
                    {"icon": "✪", "title": "Комплексное развитие", "text": "До\u00a08\u00a0детей в\u00a0группе\u00a0— каждому достаётся внимание педагога."},
                    {"icon": "★", "title": "Профессионализм", "text": "Развиваем интеллект, творчество, социальные навыки и\u00a0эмоциональный интеллект."},
                ],
            },
        },
        {
            "component": "form_strip",
            "data": {
                "title": "Приходите знакомиться!",
                "subtitle": "Покажем центр, педагогов и\u00a0предложим подходящую программу\u00a0— бесплатно.",
                "color": "purple",
                "source_block": "about_strip",
            },
        },
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


def program_landing_blocks(name: str, tagline: str) -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "source": "current_program",
                "eyebrow": "О\u00a0программе",
                "title": name,
                "subtitle": tagline,
                "subtitle_accent": True,
                "cta_text": "Записаться на\u00a0занятие",
                "cta_target": "lead-form",
                "cta_secondary_text": "Смотреть расписание",
                "cta_secondary_target": "schedule",
            },
        },
        {
            "component": "program_schedule",
            "data": {
                "title": "Программа занятий",
                "subtitle": "Группы формируем по\u00a0возрасту и\u00a0уровню подготовки",
                "source": "program_schedule",
                "age_filters": [
                    {"slug": "all", "label": "Все программы", "hint": ""},
                    {"slug": "age-5-6", "label": "За\u00a02 года до\u00a0школы", "hint": "5\u00a0лет"},
                    {"slug": "age-6-7", "label": "За\u00a01 год до\u00a0школы", "hint": "6\u00a0лет"},
                ],
                "price_toggle": [
                    {"slug": "per-lesson", "label": "Занятие"},
                    {"slug": "per-month", "label": "Месяц", "active": True},
                ],
                "default_subjects": [
                    {"name": "Развитие речи", "freq": "2 раза в\u00a0неделю"},
                    {"name": "Математика", "freq": "2 раза в\u00a0неделю"},
                    {"name": "Психология", "freq": "1 раз в\u00a0неделю"},
                    {"name": "Логопедия", "freq": "1 раз в\u00a0неделю"},
                    {"name": "Английский язык", "freq": "1 раз в\u00a0неделю"},
                    {"name": "ИЗО", "freq": "1 раз в\u00a0неделю"},
                ],
                "default_attributes": ["5–5.5\u00a0лет", "2 часа", "3 занятия в\u00a0неделю"],
                "default_teachers": {
                    "count": "4 педагогов",
                    "role": "Учителя начальной школы, психологи",
                    "colors": ["#f59e40", "#6359c2", "#db5eb4", "#4a8df5"],
                },
            },
        },
        {
            "component": "advantages",
            "data": {
                "title": "Место, где раскрываются таланты",
                "items": [
                    {"icon": "01", "title": "Комплексный подход", "text": "Программа связана с\u00a0общим развитием\u00a0— от\u00a0сенсорики до\u00a0самостоятельности."},
                    {"icon": "02", "title": "Опытные педагоги", "text": "Учителя начальных классов с\u00a0наградами и\u00a0стажем 10+\u00a0лет."},
                    {"icon": "03", "title": "Маленькие группы", "text": "До\u00a08\u00a0детей, каждому хватает внимания педагога."},
                    {"icon": "04", "title": "Открытая цена", "text": "Стоимость и\u00a0расписание видны сразу, без\u00a0звонка менеджеру."},
                ],
            },
        },
        {
            "component": "compare_table",
            "data": {
                "title": "Сравните сами",
                "subtitle": "Чем\u00a0программа «Семицветика» отличается от\u00a0стандартных альтернатив",
                "columns": [
                    {
                        "title": "Семицветик",
                        "subtitle": "Наш\u00a0подход",
                        "accent": True,
                        "points": [
                            "Группа до\u00a08\u00a0детей — внимание каждому",
                            "Учителя начальных классов с\u00a0наградами",
                            "Диагностика логопеда и\u00a0психолога включены",
                            "Открытая цена и\u00a0расписание на\u00a0сайте",
                            "15\u00a0лет опыта, более 3000\u00a0выпускников",
                        ],
                    },
                    {
                        "title": "Детский сад",
                        "subtitle": "Стандартный формат",
                        "points": [
                            "Группа 25–30\u00a0детей",
                            "Воспитатель, а\u00a0не\u00a0учитель-предметник",
                            "Коррекционная поддержка\u00a0— только по\u00a0запросу",
                            "Большая часть дня\u00a0— присмотр",
                        ],
                    },
                    {
                        "title": "Репетитор",
                        "subtitle": "Индивидуально",
                        "points": [
                            "Один предмет за\u00a0занятие",
                            "Дорого при\u00a0регулярных занятиях",
                            "Нет\u00a0социализации и\u00a0работы в\u00a0группе",
                            "Зависимость от\u00a0одного специалиста",
                        ],
                    },
                ],
            },
        },
        {
            "component": "form_strip",
            "data": {
                "title": "Запишитесь на\u00a0пробное занятие",
                "subtitle": "Познакомим с\u00a0педагогом, покажем методику и\u00a0подберём удобное время.",
                "color": "purple",
                "source_block": "program_strip",
            },
        },
        {
            "component": "faq",
            "data": {
                "title": "Родители часто спрашивают",
                "items": [
                    {"q": "Сколько детей в\u00a0группе?", "a": "До\u00a08\u00a0детей\u00a0— чтобы педагог успевал к\u00a0каждому."},
                    {"q": "Как\u00a0проходит пробное занятие?", "a": "Стандартное занятие, на\u00a0котором родитель может быть рядом или\u00a0в\u00a0соседнем кабинете."},
                    {"q": "Что если ребёнок пропустит занятие?", "a": "Мы\u00a0предложим дополнительное время в\u00a0рамках недели или\u00a0включим материал в\u00a0следующее занятие."},
                    {"q": "Можно\u00a0ли\u00a0платить за\u00a0абонемент и\u00a0разово?", "a": "Да, доступны оба формата. Абонемент выгоднее в\u00a0пересчёте на\u00a0одно занятие."},
                ],
            },
        },
        {"component": "reviews_grid", "data": {"title": "Что\u00a0говорят родители", "subtitle": "Отзывы по\u00a0программе «" + name + "»", "source": "program_reviews"}},
        {"component": "photo_strip", "data": {}},
        {"component": "cta_final", "data": {"title": "Запишите ребёнка на\u00a0пробное занятие", "subtitle": "Перезвоним в\u00a0течение 15\u00a0минут, поможем выбрать группу и\u00a0время.", "color": "green", "source_block": "program_final_cta"}},
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


def programmy_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Мы\u00a0создали 8\u00a0направлений, которые охватывают все сферы развития ребёнка",
                "subtitle": "",
                "cta_text": "Записаться",
                "cta_target": "contact-panel",
                "eyebrow": "Каталог",
            },
        },
        {"component": "programs_grid", "data": {"title": "", "subtitle": "", "source": "all_programs"}},
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


def pedagogi_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Учителя, которым доверяют",
                "subtitle": "",
                "eyebrow": "Педагоги",
            },
        },
        {"component": "teachers_grid", "data": {"title": "", "source": "all_teachers", "show_search": True, "show_chips": True}},
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


def kontakty_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Контакты",
                "subtitle": "Все каналы связи\u00a0— в\u00a0одном месте.",
                "cta_text": "Заказать звонок",
                "cta_target": "contact-panel",
                "eyebrow": "Связь",
            },
        },
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


PROGRAM_CATALOG = [
    # First four are surfaced on the home page grid (featured, limit=4).
    # Figma layout: Логопедия (orange), Комплексное развитие (red), Подготовка к школе (purple), Английский (green).
    {"slug": "logoped", "name": "Логопедия", "tagline": "Скорректируем нарушения речи, связанные со\u00a0звукопроизношением, нарушением чтения, письма, фономатического восприятия", "description": "Диагностика речи, постановка звуков, упражнения на\u00a0понимание и\u00a0чистую речь.", "emoji": "🗣️", "color": "#3d61f3", "image_url": "img/figma/programs/mic.png", "age_min": 4, "age_max": 12, "duration_min": 40, "frequency": "2\u00a0занятия в\u00a0неделю", "price": 1200, "price_unit": "день", "category": "speech", "category_label": "Логопедия и\u00a0коррекция", "sort_order": 1},
    {"slug": "rannee-razvitie", "name": "Комплексное развитие", "tagline": "Разовьём речь, общую мелкую моторику, научим правильно держать карандаш, рисовать и\u00a0общаться в\u00a0коллективе", "description": "Развивающие занятия: сенсорика, первые слова, мелкая моторика, групповая игра.", "emoji": "🧸", "color": "#f15922", "image_url": "img/figma/programs/cubes-abv.png", "age_min": 2.5, "age_max": 4.5, "duration_min": 60, "frequency": "2\u00a0занятия в\u00a0неделю", "price": 5200, "price_unit": "мес", "category": "early", "category_label": "Раннее развитие", "sort_order": 2},
    {"slug": "podgotovka-k-shkole", "name": "Подготовка к\u00a0школе", "tagline": "Научим читать целыми словами, считать в\u00a0пределах 2-го десятка, писать, разовьём звуковой анализ, логическое мышление, внимание и\u00a0памяти", "description": "Комплексная подготовка к\u00a0школе в\u00a0малых группах.", "emoji": "📘", "color": "#6359c2", "image_url": "img/figma/programs/school-desk.png", "age_min": 5, "age_max": 6.5, "duration_min": 150, "frequency": "2\u00a0занятия в\u00a0неделю", "price": 6200, "price_unit": "мес", "category": "school", "category_label": "Подготовка к\u00a0школе", "sort_order": 3},
    {"slug": "anglijskij", "name": "Английский язык", "tagline": "Игровой английский с\u00a0упором на\u00a0речь и\u00a0понимание на\u00a0слух — начинаем с\u00a0простых диалогов, заканчиваем проектами.", "description": "Учим через короткие игровые циклы, песни, карточки и\u00a0небольшие диалоги.", "emoji": "🇬🇧", "color": "#00b43c", "image_url": "img/figma/programs/speech-bubbles.png", "age_min": 4, "age_max": 12, "duration_min": 40, "frequency": "2\u00a0занятия в\u00a0неделю", "price": 1200, "price_unit": "день", "category": "english", "category_label": "Английский язык", "sort_order": 4},
    # Catalog extras (shown on /programmy/)
    {"slug": "izostudia", "name": "Изостудия и\u00a0Лепка", "tagline": "Рисование, аппликация, лепка и\u00a0декоративно-прикладное искусство для\u00a0детей 4–10 лет.", "description": "Развиваем моторику, вкус и\u00a0фантазию. Работаем с\u00a0красками, глиной, бумагой.", "emoji": "🎨", "color": "#db5eb4", "image_url": "img/figma/gallery/bear.png", "age_min": 4, "age_max": 10, "duration_min": 60, "frequency": "1 раз в\u00a0неделю", "price": 3400, "price_unit": "мес", "category": "art", "category_label": "Творчество и\u00a0дизайн", "sort_order": 5},
    {"slug": "otlichnik", "name": "Программа «Отличник»", "tagline": "Углублённая подготовка для\u00a0детей 5–7 лет с\u00a0упором на\u00a0самостоятельность и\u00a0медалистскую траекторию.", "description": "Добавляем олимпиадные задачи, проектную деятельность и\u00a0навыки публичных выступлений.", "emoji": "🏅", "color": "#f59e40", "image_url": "img/figma/programs/school-desk.png", "age_min": 5, "age_max": 7, "duration_min": 90, "frequency": "3 раза в\u00a0неделю", "price": 8900, "price_unit": "мес", "category": "school", "category_label": "Подготовка к\u00a0школе", "sort_order": 6},
    {"slug": "psiholog", "name": "Психология и\u00a0здоровье", "tagline": "Мини-группы для\u00a0детей 4–10 лет: уверенность, эмоции, дружба.", "description": "Работа в\u00a0парах и\u00a0группах: эмоциональный интеллект, общение, саморегуляция.", "emoji": "🌱", "color": "#4c83f1", "image_url": "img/figma/programs/speech-bubbles.png", "age_min": 4, "age_max": 10, "duration_min": 50, "frequency": "1 раз в\u00a0неделю", "price": 3200, "price_unit": "мес", "category": "psychology", "category_label": "Психология и\u00a0здоровье", "sort_order": 7},
    {"slug": "detskij-lager", "name": "Детский лагерь", "tagline": "Тематические смены для\u00a0детей 5–12 лет: творчество, спорт, английский, квесты.", "description": "Летние и\u00a0каникулярные смены полного и\u00a0полу-дня. Педагоги центра, активности каждый день.", "emoji": "🏕", "color": "#258c17", "image_url": "img/figma/gallery/balloons.png", "age_min": 5, "age_max": 12, "duration_min": 300, "frequency": "Пн\u00a0– Пт", "price": 8900, "price_unit": "смена", "category": "camp", "category_label": "Летний лагерь", "sort_order": 8},
]


TEACHER_CATALOG = [
    # Names from Figma slice_03 (top two visible cards): Бурова Ирина Михайловна, Дёмина Ирина Александровна.
    {"name": "Бурова Ирина Михайловна", "role": "Педагог подготовки к\u00a0школе", "specialization": "Чтение, математика, развитие логики", "bio": "15\u00a0лет помогает детям мягко входить в\u00a0учебную нагрузку и\u00a0формировать уверенность перед школой.", "emoji": "🎓", "photo_url": "/static/img/figma/teachers/burova.png", "category": "school", "sort_order": 1},
    {"name": "Дёмина Ирина Александровна", "role": "Педагог психологической поддержки", "specialization": "Эмоциональный интеллект, адаптация, коммуникация", "bio": "Работает с\u00a0детьми от\u00a04\u00a0лет. Помогает мягко адаптироваться к\u00a0школе.", "emoji": "🪄", "photo_url": "/static/img/figma/teachers/demina.png", "category": "psychology", "sort_order": 2},
    {"name": "Ольга Савельева", "role": "Педагог раннего развития", "specialization": "Сенсорика, внимание, запуск речи", "bio": "Собирает занятия так, чтобы ребёнок удерживал интерес и\u00a0не\u00a0уставал от\u00a0формата.", "emoji": "🌱", "photo_url": "/static/img/figma/teachers/woman-forest.png", "category": "early", "sort_order": 3},
    {"name": "Екатерина Морозова", "role": "Учитель начальных классов", "specialization": "Чтение, прописи, внимательность", "bio": "Работает с\u00a0группами «Лучики» и\u00a0«Звёздочки». Помогает детям полюбить школу ещё до\u00a01\u00a0сентября.", "emoji": "📘", "photo_url": "/static/img/figma/teachers/girl-laptop.png", "category": "school", "sort_order": 4},
    {"name": "Анна Карпова", "role": "Преподаватель английского", "specialization": "Игровой английский, речь, Junior Jack", "bio": "Готовит малышей к\u00a0первым международным экзаменам. Дети поют, играют, говорят на\u00a0английском без\u00a0стеснения.", "emoji": "🇬🇧", "photo_url": "/static/img/figma/teachers/demina.png", "category": "english", "sort_order": 5},
    {"name": "Наталья Кузнецова", "role": "Педагог изостудии", "specialization": "Рисование, лепка, декор", "bio": "Творчество как способ говорить о\u00a0себе. Учит видеть цвет, форму и\u00a0композицию.", "emoji": "🎨", "photo_url": "/static/img/figma/teachers/burova.png", "category": "art", "sort_order": 6},
    {"name": "Светлана Иванова", "role": "Педагог-психолог", "specialization": "Эмоциональный интеллект, уверенность, общение", "bio": "Помогает детям мягко пройти адаптацию и\u00a0развить социальные навыки.", "emoji": "🌱", "photo_url": "/static/img/figma/teachers/woman-forest.png", "category": "psychology", "sort_order": 7},
    {"name": "Дарья Николаева", "role": "Преподаватель английского", "specialization": "Старшие группы, подготовка к\u00a0олимпиадам", "bio": "Ведёт группы 2–4 классов. Фокус на\u00a0говорение и\u00a0понимание на\u00a0слух.", "emoji": "🗣️", "photo_url": "/static/img/figma/teachers/girl-laptop.png", "category": "english", "sort_order": 8},
    {"name": "Марина Лебедева", "role": "Учитель начальных классов", "specialization": "Математика и\u00a0логика", "bio": "Наставник олимпиадных групп. Любит задачи «на\u00a0подумать».", "emoji": "🔢", "photo_url": "/static/img/figma/teachers/demina.png", "category": "school", "sort_order": 9},
    {"name": "Татьяна Орлова", "role": "Воспитатель раннего развития", "specialization": "Ясельная группа, сенсорика", "bio": "Работает с\u00a0малышами 1–2 лет. Мягкий голос и\u00a0бесконечное терпение.", "emoji": "🌸", "photo_url": "/static/img/figma/teachers/burova.png", "category": "early", "sort_order": 10},
    {"name": "Юлия Васильева", "role": "Вожатая летнего лагеря", "specialization": "Квесты, командные игры, активности", "bio": "Четыре года вожатой в\u00a0«Семицветике». Лагерь\u00a0— её стихия.", "emoji": "🏕", "photo_url": "/static/img/figma/teachers/woman-forest.png", "category": "camp", "sort_order": 11},
    {"name": "Алёна Сорокина", "role": "Педагог по\u00a0подготовке к\u00a0школе", "specialization": "Письмо, чтение, развитие речи", "bio": "Ведёт «Отличника». Ставит руку, учит усидчивости.", "emoji": "✍️", "photo_url": "/static/img/figma/teachers/girl-laptop.png", "category": "school", "sort_order": 12},
]


SCHEDULE_CATALOG = {
    "podgotovka-k-shkole": [("Лучики", "Вт / Чт", "17:30", "19:00"), ("Звёздочки", "Сб", "10:00", "11:30")],
    "logoped": [("Индивидуально", "Пн-Пт", "по\u00a0записи", "по\u00a0записи")],
    "anglijskij": [("Starter", "Пн / Ср", "18:00", "19:00"), ("Junior", "Вт / Чт", "17:00", "18:00")],
    "rannee-razvitie": [("Малыши", "Вт / Пт", "11:00", "11:40")],
    "izostudia": [("Творческая", "Сб", "12:00", "13:00")],
    "otlichnik": [("Олимпиадники", "Пн / Ср / Пт", "17:00", "18:30")],
    "psiholog": [("Группа Солнышко", "Чт", "18:00", "18:50")],
    "detskij-lager": [("Летняя смена", "Пн-Пт", "09:00", "14:00")],
}


def upsert_programs() -> None:
    for item in PROGRAM_CATALOG:
        program = Program.query.filter_by(slug=item["slug"]).first()
        data = {k: v for k, v in item.items() if k not in ("slug", "category_label")}
        if program is None:
            program = Program(slug=item["slug"], has_landing=True, **data)
            db.session.add(program)
            print(f"[new] program: {item['slug']}")
        else:
            for key, value in data.items():
                setattr(program, key, value)
            print(f"[upd] program: {item['slug']}")
    db.session.flush()

    program_by_slug = {p.slug: p for p in Program.query.all()}
    for slug, slots in SCHEDULE_CATALOG.items():
        program = program_by_slug.get(slug)
        if program is None:
            continue
        existing_keys = {(s.group_name, s.day_of_week, s.time_start) for s in program.schedule_slots}
        for group, day, start, end in slots:
            if (group, day, start) in existing_keys:
                continue
            db.session.add(ScheduleSlot(program_id=program.id, group_name=group, day_of_week=day, time_start=start, time_end=end))


LEGACY_TEACHER_MERGE = {
    # legacy name -> canonical figma name from TEACHER_CATALOG
    "Ирина Бурова": "Бурова Ирина Михайловна",
    "Мария Степанова": "Дёмина Ирина Александровна",
}


def merge_legacy_teachers() -> None:
    """Move programs (and schedule slots if linked) from legacy duplicate teachers
    to their canonical figma-named counterparts, then delete the legacy rows.
    Idempotent: no-op once legacy rows are gone."""
    for legacy_name, canonical_name in LEGACY_TEACHER_MERGE.items():
        legacy = Teacher.query.filter_by(name=legacy_name).first()
        if legacy is None:
            continue
        canonical = Teacher.query.filter_by(name=canonical_name).first()
        if canonical is None:
            # canonical will be inserted in upsert_teachers; defer merge to next run
            print(f"[merge-defer] no canonical yet for {legacy_name} -> {canonical_name}")
            continue
        moved = 0
        for prog in Program.query.filter_by(teacher_id=legacy.id).all():
            prog.teacher_id = canonical.id
            moved += 1
        # ScheduleSlot has no teacher_id column (ties via program); nothing else to move.
        db.session.delete(legacy)
        print(f"[merge] {legacy_name} -> {canonical_name} (programs moved: {moved})")
    db.session.commit()


def upsert_teachers() -> None:
    wanted_names = {item["name"] for item in TEACHER_CATALOG}
    for item in TEACHER_CATALOG:
        teacher = Teacher.query.filter_by(name=item["name"]).first()
        if teacher is None:
            teacher = Teacher(**item)
            db.session.add(teacher)
            print(f"[new] teacher: {item['name']}")
        else:
            for key, value in item.items():
                setattr(teacher, key, value)
            print(f"[upd] teacher: {item['name']}")
    # Clean stale teachers that are no longer in the catalog (rename safety).
    stale = Teacher.query.filter(~Teacher.name.in_(wanted_names)).all()
    for teacher in stale:
        # Keep teachers that are referenced by programs, just blank out photo.
        if teacher.programs:
            teacher.photo_url = None
            print(f"[keep] teacher referenced by program: {teacher.name}")
            continue
        db.session.delete(teacher)
        print(f"[del] teacher: {teacher.name}")


def ensure_schema() -> None:
    from sqlalchemy import text
    needed = {
        "teacher": [("category", "VARCHAR(50)")],
        "program": [("image_url", "VARCHAR(255)")],
    }
    for table, cols in needed.items():
        existing = {row[1] for row in db.session.execute(text(f"PRAGMA table_info({table})"))}
        for col_name, col_type in cols:
            if col_name not in existing:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
                print(f"[migrate] {table}.{col_name} added")
    db.session.commit()


def upsert_site_settings() -> None:
    """Merge brand/contacts settings so templates have real URLs for socials/map."""
    needed = {
        "social_vk": "https://vk.com/semicvetic_sp",
        "social_tg": "https://t.me/semicvetic_bot",
        "yandex_map_iframe": (
            "https://yandex.ru/map-widget/v1/?ll=38.1356%2C56.3119&z=15"
            "&pt=38.1356%2C56.3119%2Cpm2rdm&l=map"
        ),
        "address": "Московская область, г. Сергиев Посад, ул. Воробьёвская, д. 16А, 2 этаж (вход с проспекта Красной Армии)",
        "hours": "Работаем с\u00a09:00 до\u00a021:00",
        "phone_1": "8 (926) 366-57-87",
        "phone_2": "8 (496) 551-33-85",
    }
    for key, default_value in needed.items():
        row = SiteSetting.query.filter_by(key=key).first()
        if row is None:
            db.session.add(SiteSetting(key=key, value=default_value))
            print(f"[new] setting: {key}")
        elif not row.value:
            row.value = default_value
            print(f"[upd] setting: {key} (empty → default)")
    db.session.commit()


def run() -> None:
    app = create_app()
    with app.app_context():
        ensure_schema()
        upsert_site_settings()
        upsert_programs()
        upsert_teachers()
        db.session.flush()
        # run merge after teachers upsert ensures canonical rows exist
        merge_legacy_teachers()

        program_meta = {item["slug"]: item for item in PROGRAM_CATALOG}
        teacher_category_map = {item["name"]: item["category"] for item in TEACHER_CATALOG}

        mapping = {
            "home": home_blocks(),
            "o-centre": about_blocks(),
            "programmy": programmy_blocks(),
            "pedagogi": pedagogi_blocks(),
            "kontakty": kontakty_blocks(),
        }
        for slug, blocks in mapping.items():
            page = Page.query.filter_by(slug=slug).first()
            if page is None:
                print(f"[skip] page not found: {slug}")
                continue
            page.blocks = blocks
            print(f"[ok] page updated: {slug} ({len(blocks)} blocks)")

        for program in Program.query.all():
            program.landing_blocks = program_landing_blocks(program.name, program.tagline)
            print(f"[ok] program landing updated: {program.slug}")

        db.session.commit()
        print("Content update complete.")
        print(f"  programs: {Program.query.count()}")
        print(f"  teachers: {Teacher.query.count()}")
        _ = program_meta, teacher_category_map  # reserved for future enrichment


if __name__ == "__main__":
    run()
