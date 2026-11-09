"""Каталог портфеля: карточки лендинга и пункты навигации."""

MODULES = [
    {
        "code": "P1",
        "slug": "p1",
        "path": "/p1",
        "module": "app.projects.p1_monitoring",
        "title": "Мониторинг серверов 1С",
        "summary": "Сбор метрик CPU, памяти и отклика по хостам кластера, статистика сеансов "
        "и автоматическое обнаружение аномалий робастным z-скорингом.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "MAD-аномалии", "Canvas-график"],
        "accent": "green",
    },
    {
        "code": "P2",
        "slug": "p2",
        "path": "/p2",
        "module": "app.projects.p2_backup",
        "title": "Оркестратор резервного копирования",
        "summary": "Расписание бэкапов информационных баз, контроль RPO, разбор журналов "
        "и классификация инцидентов по тексту ошибки.",
        "tags": ["бэк", "ИИ"],
        "stack": ["FastAPI", "PostgreSQL", "Centroid-классификатор"],
        "accent": "graphite",
    },
    {
        "code": "P3",
        "slug": "p3",
        "path": "/p3",
        "module": "app.projects.p3_access",
        "title": "Аудит прав доступа",
        "summary": "Матрица «пользователь — роль — объект», поиск избыточных прав, "
        "опасных сочетаний и учётных записей уволенных сотрудников.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "Скоринг риска"],
        "accent": "green",
    },
    {
        "code": "P4",
        "slug": "p4",
        "path": "/p4",
        "module": "app.projects.p4_updates",
        "title": "Трекер обновлений конфигураций",
        "summary": "Сравнение состава объектов между версиями типовой конфигурации, "
        "оценка риска обновления и чек-лист для расширений.",
        "tags": ["бэк", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "Diff-анализ"],
        "accent": "graphite",
    },
    {
        "code": "P5",
        "slug": "p5",
        "path": "/p5",
        "module": "app.projects.p5_sql",
        "title": "SQL-аналитик MSSQL/PostgreSQL",
        "summary": "Статический разбор запроса и плана: seq scan, функции в предикате, "
        "SELECT *, отсутствие индексов — с готовой рекомендацией.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "Разбор EXPLAIN"],
        "accent": "green",
    },
    {
        "code": "P6",
        "slug": "p6",
        "path": "/p6",
        "module": "app.projects.p6_sedesk",
        "title": "Service Desk с ИИ-маршрутизацией",
        "summary": "Классификация обращений по группе поддержки, приоритет с учётом SLA, "
        "подбор статьи базы знаний через BM25 и черновик ответа.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "BM25", "Centroid"],
        "accent": "graphite",
    },
    {
        "code": "P7",
        "slug": "p7",
        "path": "/p7",
        "module": "app.projects.p7_xbrl",
        "title": "XBRL/XML финансовая отчётность",
        "summary": "Разбор XBRL-фактов, проверка обязательных показателей, арифметики "
        "и периодов, человекочитаемая сводка по отчёту.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "xml.etree", "Валидатор"],
        "accent": "green",
    },
    {
        "code": "P8",
        "slug": "p8",
        "path": "/p8",
        "module": "app.projects.p8_edo",
        "title": "Документооборот: классификация",
        "summary": "Определение типа входящего документа, извлечение реквизитов, "
        "проверка контрольных чисел ИНН и поиск дублей по косинусной близости.",
        "tags": ["бэк", "ИИ", "фронт"],
        "stack": ["FastAPI", "PostgreSQL", "TF-IDF", "Контрольные числа"],
        "accent": "graphite",
    },
]

NAV = [{"code": item["code"], "path": item["path"], "title": item["title"]} for item in MODULES]

TAGS = ("бэк", "ИИ", "фронт")
TAG_COUNTS = {tag: sum(1 for item in MODULES if tag in item["tags"]) for tag in TAGS}

__all__ = ["MODULES", "NAV", "TAG_COUNTS", "TAGS"]
