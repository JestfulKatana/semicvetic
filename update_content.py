"""Update page blocks and program landings in the existing DB to match Figma mockups.

Usage:
    python update_content.py            # updates pages, programs, settings

Safe to re-run: always overwrites page.blocks / program.landing_blocks.
Keeps existing teacher/review/event data intact.
"""
from __future__ import annotations

from app import create_app
from app.extensions import db
from app.models import Page, Program, SiteSetting


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
                "cta_target": "lead-form",
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
                        "description": "Разговорный английский, лексика, грамматика, фонетика, подготовка к\u00a0олимпиадам Junior Jack.",
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
                        ],
                        "teachers": ["#f59e40", "#6359c2", "#db5eb4"],
                        "teachers_count": "4 педагога",
                        "teachers_role": "Учителя начальной школы, психологи",
                        "price": "800–900\u00a0₽/занятие",
                    },
                    {"slug": "rannee-razvitie", "name": "Вместе с\u00a0мамой", "tags": ["1–3 года"], "description": "Малышам и\u00a0мамам\u00a0— сенсорика, пальчиковые игры, первые\u00a0слова.", "groups": [{"title": "Группа утренняя", "slots": [{"day": "Вт, Пт", "time": "11:00–11:40"}]}], "teachers": ["#85c88a"], "teachers_count": "1 педагог", "teachers_role": "Специалист раннего развития", "price": "от\u00a04\u00a0600\u00a0₽/мес"},
                    {"slug": "izostudia", "name": "Изостудия и\u00a0Лепка", "tags": ["4–10 лет"], "description": "Рисование, аппликация, лепка\u00a0— творчество как способ говорить о\u00a0себе.", "groups": [{"title": "Группа творческая", "slots": [{"day": "Сб", "time": "12:00–13:00"}]}], "teachers": ["#db5eb4"], "teachers_count": "1 педагог", "teachers_role": "Педагог\u00a0изо и\u00a0ДПИ", "price": "от\u00a03\u00a0400\u00a0₽/мес"},
                    {"slug": "podgotovka-k-shkole", "name": "Программа «Отличник»", "tags": ["5–7 лет"], "description": "Комплексная подготовка к\u00a0школе с\u00a0упором на\u00a0самостоятельность.", "groups": [{"title": "Группа Лучики", "slots": [{"day": "Вт, Чт", "time": "17:30–19:00"}]}, {"title": "Группа Звёздочки", "slots": [{"day": "Сб", "time": "10:00–11:30"}]}], "teachers": ["#f59e40", "#6359c2"], "teachers_count": "2 педагога", "teachers_role": "Учителя начальных классов", "price": "от\u00a06\u00a0800\u00a0₽/мес"},
                    {"slug": "detskij-lager", "name": "Детский лагерь", "tags": ["5–12 лет"], "description": "Тематические смены: творчество, спорт, английский, квесты.", "groups": [{"title": "Летняя смена", "slots": [{"day": "Пн\u00a0– Пт", "time": "9:00–14:00"}]}], "teachers": ["#4a8df5", "#db5eb4", "#85c88a"], "teachers_count": "3 педагога", "teachers_role": "Вожатые и\u00a0педагоги центра", "price": "от\u00a08\u00a0900\u00a0₽/смена"},
                ],
            },
        },
        {
            "component": "trust_bar",
            "data": {
                "title": "15\u00a0лет растим счастливых детей",
                "items": [
                    {"value": "~1,5\u00a0ч", "label": "гарантированного живого развития без\u00a0смартфонов"},
                    {"value": "15\u00a0лет", "label": "Работаем и\u00a0развиваем детей в\u00a0Сергиевом Посаде"},
                    {"value": ">70%", "label": "детей из\u00a0детского сада приходит за\u00a0дополнительными занятиями"},
                    {"value": "98%", "label": "Детей идут с\u00a0удовольствием в\u00a0клуб"},
                    {"value": "10%", "label": "скидка детям участников СВО и\u00a0вторым детям в\u00a0семье"},
                    {"value": "100%", "label": "Активно участвуют в\u00a0спектаклях, квестах, мастер-классах и\u00a0летнем лагере"},
                    {"value": ">80%", "label": "рекомендуют друзьям и\u00a0приводят младших сестёр и\u00a0братьев"},
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
            },
        },
        {
            "component": "how_it_works",
            "data": {
                "title": "Место, где раскрываются таланты",
                "subtitle": "В\u00a0отличие от\u00a0стандартного присмотра в\u00a0детском саду, Семицветик предлагает системное образование и\u00a0коррекционную поддержку, которые развивают медалистов и\u00a0лицеистов города",
                "steps": [
                    {"icon": "1", "title": "До\u00a08\u00a0детей в\u00a0группе", "text": "У\u00a0нас учатся группы по\u00a08\u00a0детей, в\u00a0отличие от\u00a0садов, где занимаются 25–30 детей. Учитель уделяет время каждому."},
                    {"icon": "2", "title": "Учителя начальных классов", "text": "Базовые знания закладывают школьные учителя с\u00a0наградами и\u00a0опытом. Ребёнок будет заранее готов к\u00a0учёбе в\u00a0школе."},
                    {"icon": "3", "title": "Психолог\u00a0+ логопед", "text": "Видим ребёнка целиком: развитие, речь, поведение. Если\u00a0заметим особенности\u00a0— скажем сразу и\u00a0поможем."},
                    {"icon": "4", "title": "Всё\u00a0в\u00a0одном месте", "text": "Чтение, математика, англ.\u00a0яз., изо, психология, логопедия."},
                ],
            },
        },
        {"component": "form_strip", "data": {"title": "Давайте знакомиться!", "subtitle": "Оставьте телефон, и\u00a0убедитесь сами, почему нам\u00a0доверяют более 3000\u00a0семей", "color": "purple", "source_block": "cta_strip"}},
        {"component": "reviews_grid", "data": {"title": "Что говорят родители", "subtitle": "15\u00a0лет истории успеха в\u00a0каждом отзыве", "source": "featured_reviews", "limit": 1}},
        {"component": "gallery", "data": {"title": "Жизнь нашего центра в\u00a0одном видео", "subtitle": "Короткий ролик о\u00a0том, как\u00a0растут наши «маленькие звёздочки»", "variant": "video"}},
        {"component": "cta_final", "data": {"title": "Ответим на\u00a0вопросы по\u00a0телефону и\u00a0пригласим в\u00a0детский клуб на\u00a0экскурсию", "subtitle": "", "color": "green", "source_block": "final_cta"}},
        {"component": "faq", "data": {"title": "Родители часто спрашивают", "items": [
            {"q": "Как\u00a0долго работает ваш\u00a0центр?", "a": "Центр работает уже\u00a0более 15\u00a0лет. За\u00a0это\u00a0время мы\u00a0подготовили более 3000\u00a0выпускников, многие из\u00a0которых закончили школу с\u00a0золотыми медалями."},
            {"q": "Где\u00a0вы\u00a0находитесь и\u00a0как\u00a0с\u00a0вами связаться?", "a": "Московская область, г.\u00a0Сергиев Посад, ул.\u00a0Воробьёвская, д.\u00a016А, 2\u00a0этаж. Телефон: 8\u00a0(926)\u00a0366-57-87."},
            {"q": "Как\u00a0именно найти вход в\u00a0ваш\u00a0центр?", "a": "Вход со стороны проспекта Красной Армии, 2\u00a0этаж. Ориентир — вывеска «Семицветик»."},
            {"q": "Можно\u00a0ли\u00a0в\u00a0«Семицветике» отметить День рождения ребёнка?", "a": "Да, мы\u00a0организуем праздники для\u00a0детей. Свяжитесь с\u00a0нами для\u00a0уточнения деталей."},
            {"q": "Проводятся\u00a0ли\u00a0в\u00a0центре занятия в\u00a0период школьных каникул или\u00a0летом?", "a": "Да, у\u00a0нас работает летний лагерь и\u00a0проводятся занятия в\u00a0каникулы."},
            {"q": "Предусмотрены\u00a0ли\u00a0льготы для\u00a0семей, где\u00a0занимаются двое детей?", "a": "Да, для\u00a0второго ребёнка в\u00a0семье предоставляется скидка 10%. Также скидка действует для\u00a0детей участников СВО."},
        ]}},
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "compact", "source": "contact_data"}},
    ]


def about_blocks() -> list[dict]:
    return [
        {
            "component": "hero",
            "data": {
                "title": "Среда, где дети растут разносторонними",
                "subtitle": "",
                "eyebrow": "О центре",
                "cta_text": "Записаться",
                "cta_target": "lead-form",
                "stats_row": [
                    {"value": "с\u00a02011\u00a0г.", "label": "Уже\u00a015\u00a0лет помогаем детям расти"},
                    {"value": "8", "label": "направлений обучения в\u00a0одном центре"},
                    {"value": "3000", "label": "детей прошли обучение"},
                ],
            },
        },
        {
            "component": "rich_text",
            "data": {
                "content": "Сегодня «Семицветик»\u00a0— это\u00a0команда **профессиональных педагогов**, современные программы обучения и\u00a0доказанные результаты. Но\u00a0главное\u00a0— по-прежнему **любовь к\u00a0детям** и\u00a0вера в\u00a0их\u00a0безграничные возможности.",
            },
        },
        {
            "component": "advantages",
            "data": {
                "title": "Наши ценности",
                "subtitle": "Принципы, которыми мы\u00a0руководствуемся в\u00a0работе с\u00a0детьми",
                "items": [
                    {"icon": "♥", "title": "Индивидуальный подход к\u00a0группе", "text": "Маленькие группы, внимание к\u00a0каждому."},
                    {"icon": "✦", "title": "Мини-группы", "text": "До\u00a08\u00a0детей\u00a0— каждый получает внимание педагога."},
                    {"icon": "✪", "title": "Комплексное развитие", "text": "Академические и\u00a0творческие занятия, психология и\u00a0логопедия в\u00a0одном месте."},
                    {"icon": "★", "title": "Профессионализм", "text": "Педагоги с\u00a0опытом и\u00a0регулярным повышением квалификации."},
                ],
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
                "eyebrow": "Программа центра",
                "title": name,
                "subtitle": tagline,
                "cta_text": "Записаться на\u00a0пробное",
                "cta_target": "lead-form",
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
        {"component": "reviews_grid", "data": {"title": "Отзывы по\u00a0программе", "source": "program_reviews"}},
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
                "cta_target": "lead-form",
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
                "cta_text": "Записаться на\u00a0консультацию",
                "cta_target": "lead-form",
                "eyebrow": "Команда",
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
                "cta_target": "lead-form",
                "eyebrow": "Связь",
            },
        },
        {"component": "contact_panel", "data": {"title": "Ждём вас в\u00a0Семицветике", "variant": "full", "source": "contact_data"}},
    ]


def run() -> None:
    app = create_app()
    with app.app_context():
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


if __name__ == "__main__":
    run()
