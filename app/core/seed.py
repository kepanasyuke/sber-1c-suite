"""Детерминированные демонстрационные данные для всех восьми модулей."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.core import db

MSK = timezone(timedelta(hours=3))
NOW = datetime(2026, 11, 6, 15, 0, tzinfo=MSK)
STEPS = 37
STEP_MINUTES = 10
START = NOW - timedelta(minutes=STEP_MINUTES * (STEPS - 1))
RNG = random.Random(20261106)

HOSTS = [
    ("c1-app-01", "c1-app-01 · сервер приложений", "Сервер приложений", "PostgreSQL", 8),
    ("c1-db-01", "c1-db-01 · СУБД 1С", "СУБД", "PostgreSQL", 16),
    ("c1-db-02", "c1-db-02 · СУБД 1С (MS SQL)", "СУБД", "MS SQL Server", 16),
    ("c1-web-01", "c1-web-01 · веб-сервер", "Веб-сервер", "—", 4),
]

PROFILES = {
    "c1-app-01": {"cpu": (31, 6, {}), "ram": (58, 4, {}), "resp": (118, 12, {30: 260, 31: 300})},
    "c1-db-01": {"cpu": (46, 5, {24: 30, 25: 34, 26: 38, 27: 30}), "ram": (72, 3, {}), "resp": (86, 8, {})},
    "c1-db-02": {"cpu": (41, 6, {}), "ram": (64, 4, {}), "resp": (94, 9, {22: 120})},
    "c1-web-01": {"cpu": (19, 4, {}), "ram": (37, 3, {}), "resp": (58, 7, {})},
}

METRIC_TITLES = {
    "cpu": "CPU, %",
    "ram": "Память, %",
    "resp": "Отклик, мс",
}

LOGINS = [
    ("a.ivanova", "Иванова Анна Сергеевна", "Главный бухгалтер", "Бухгалтерия"),
    ("p.petrov", "Петров Пётр Ильич", "Бухгалтер", "Бухгалтерия"),
    ("s.sidorova", "Сидорова Светлана Юрьевна", "Бухгалтер", "Бухгалтерия"),
    ("k.kuznetsov", "Кузнецов Кирилл Олегович", "Расчётчик", "Кадры"),
    ("m.morozova", "Морозова Мария Львовна", "Специалист по кадрам", "Кадры"),
    ("d.volkov", "Волков Дмитрий Андреевич", "Менеджер по продажам", "Продажи"),
    ("e.orlova", "Орлова Елена Викторовна", "Менеджер по продажам", "Продажи"),
    ("r.zaitsev", "Зайцев Роман Николаевич", "Складской учёт", "Логистика"),
    ("n.belova", "Белова Нина Павловна", "Экономист", "Плановый отдел"),
    ("t.gusev", "Гусев Тимур Ринатович", "Программист 1С", "Учётные системы"),
    ("v.lebedev", "Лебедев Виктор Семёнович", "Уволен: специалист поддержки", "Учётные системы"),
    ("o.krylova", "Крылова Ольга Дмитриевна", "Аналитик", "Плановый отдел"),
]

ROLES = [
    ("admin", "Администратор системы", True),
    ("accountant", "Бухгалтер", False),
    ("hr", "Кадровик", False),
    ("manager", "Менеджер продаж", False),
    ("warehouse", "Складской учёт", False),
    ("observer", "Наблюдатель", False),
]

USER_ROLES = [
    ("a.ivanova", ["accountant", "observer"]),
    ("p.petrov", ["accountant"]),
    ("s.sidorova", ["accountant"]),
    ("k.kuznetsov", ["hr"]),
    ("m.morozova", ["hr", "observer"]),
    ("d.volkov", ["manager"]),
    ("e.orlova", ["manager"]),
    ("r.zaitsev", ["warehouse"]),
    ("n.belova", ["observer"]),
    ("t.gusev", ["admin"]),
    ("v.lebedev", ["admin", "observer"]),
    ("o.krylova", ["observer", "manager"]),
]

RIGHTS = [
    ("admin", "Роль", "Полные права", "администрирование"),
    ("admin", "Документ", "*", "чтение, запись, проведение"),
    ("admin", "Регистр", "*", "чтение, запись"),
    ("admin", "Внешний отчёт", "*", "запуск"),
    ("accountant", "Документ", "ПоступлениеТоваровУслуг", "чтение, запись, проведение"),
    ("accountant", "Документ", "РеализацияТоваровУслуг", "чтение, запись, проведение"),
    ("accountant", "Отчёт", "ОСВ", "просмотр"),
    ("accountant", "Регистр", "Хозрасчёты", "чтение, запись"),
    ("hr", "Документ", "ПриёмНаРаботу", "чтение, запись"),
    ("hr", "Документ", "Увольнение", "чтение, запись"),
    ("hr", "Справочник", "Сотрудники", "чтение, запись"),
    ("hr", "Отчёт", "ШтатноеРасписание", "просмотр"),
    ("manager", "Документ", "РеализацияТоваровУслуг", "чтение, запись"),
    ("manager", "Справочник", "Контрагенты", "чтение, запись"),
    ("manager", "Отчёт", "Продажи", "просмотр"),
    ("warehouse", "Документ", "ПеремещениеТоваров", "чтение, запись, проведение"),
    ("warehouse", "Справочник", "Номенклатура", "чтение"),
    ("warehouse", "Отчёт", "ОстаткиНаСкладах", "просмотр"),
    ("observer", "Отчёт", "*", "просмотр"),
    ("observer", "Документ", "*", "чтение"),
]

BACKUP_JOBS = [
    ("Бухгалтерия 3.0 (прод)", "c1-db-01", "ежедневно 23:00", 14, "ok", 2140, 24),
    ("ЗУП 3.1 (прод)", "c1-db-01", "ежедневно 23:30", 14, "ok", 1180, 24),
    ("Документооборот 2.1", "c1-db-02", "ежедневно 00:15", 30, "warn", 3400, 24),
    ("УНФ 3.0 (опт)", "c1-db-02", "ежедневно 01:00", 7, "fail", 0, 24),
    ("ERP 2.5 (пилот)", "c1-db-02", "еженедельно вс 02:00", 30, "ok", 8900, 168),
    ("Бухгалтерия 3.0 (копия)", "c1-db-01", "ежедневно 02:30", 7, "ok", 1980, 24),
]

BACKUP_LOGS = [
    (0, "info", "Резервное копирование завершено, файл c1_acc_20261105.bak, 2140 МБ"),
    (0, "info", "Резервное копирование завершено, файл c1_acc_20261106.bak, 2148 МБ"),
    (1, "info", "Резервное копирование завершено, файл c1_zup_20261106.bak, 1180 МБ"),
    (2, "warn", "Срок хранения копии истёк, файл будет удалён через 3 дня"),
    (2, "warn", "Размер копии вырос на 18 процентов за сутки, проверить журнал регистрации"),
    (2, "info", "Резервное копирование завершено, файл c1_do_20261106.bak, 3400 МБ"),
    (3, "error", "FATAL: could not connect to server: Connection refused на 5432"),
    (3, "error", "ERROR: timeout expired while waiting for backup stream"),
    (3, "error", "Резервное копирование прервано: недостаточно места на диске D"),
    (4, "info", "Полная копия ERP сжата, 8900 МБ"),
    (5, "info", "Резервное копирование завершено, файл c1_acc_copy_20261106.bak, 1980 МБ"),
    (5, "warn", "Копия создана без проверки целостности"),
]

CONF_VERSIONS = [
    ("Бухгалтерия предприятия 3.0", "3.0.141", "2025-09-18", 1180, False),
    ("Бухгалтерия предприятия 3.0", "3.0.152", "2026-02-12", 1204, False),
    ("Бухгалтерия предприятия 3.0", "3.0.160", "2026-09-24", 1231, True),
    ("ЗУП 3.1", "3.1.28", "2025-11-05", 860, False),
    ("ЗУП 3.1", "3.1.31", "2026-08-14", 878, True),
]

OBJECTS_BY_VERSION = {
    "3.0.141": [("Документ", "ПоступлениеТоваровУслуг", "a1"), ("Документ", "РеализацияТоваровУслуг", "a2"), ("Справочник", "Контрагенты", "a3"), ("Регистр", "Хозрасчёты", "a4"), ("Отчёт", "ОСВ", "a5"), ("Роль", "Бухгалтер", "a6")],
    "3.0.152": [("Документ", "ПоступлениеТоваровУслуг", "b1"), ("Документ", "РеализацияТоваровУслуг", "b2"), ("Справочник", "Контрагенты", "a3"), ("Регистр", "Хозрасчёты", "b4"), ("Отчёт", "ОСВ", "a5"), ("Роль", "Бухгалтер", "a6"), ("Документ", "СчётНаОплату", "b7")],
    "3.0.160": [("Документ", "ПоступлениеТоваровУслуг", "c1"), ("Документ", "РеализацияТоваровУслуг", "c2"), ("Справочник", "Контрагенты", "c3"), ("Регистр", "Хозрасчёты", "b4"), ("Отчёт", "ОСВ", "c5"), ("Роль", "Бухгалтер", "a6"), ("Документ", "СчётНаОплату", "b7"), ("Регистр", "Продажи", "c8")],
    "3.1.28": [("Документ", "ПриёмНаРаботу", "d1"), ("Документ", "Увольнение", "d2"), ("Справочник", "Сотрудники", "d3"), ("Регистр", "Начисления", "d4"), ("Роль", "Кадровик", "d5")],
    "3.1.31": [("Документ", "ПриёмНаРаботу", "e1"), ("Документ", "Увольнение", "d2"), ("Справочник", "Сотрудники", "e3"), ("Регистр", "Начисления", "e4"), ("Роль", "Кадровик", "d5"), ("Отчёт", "ШтатноеРасписание", "e6")],
}

SQL_SAMPLES = [
    (
        "PostgreSQL",
        "Остатки по складам за квартал",
        """select * from регистр_остатков r
where to_char(r.period, 'YYYY') = '2026'
  and r.склад in (select название from склады where активен = true)
order by r.period desc""",
        """Sort  (cost=182340.11..182585.30 rows=98100 width=208)
  Sort Key: period DESC
  ->  Seq Scan on регистр_остатков r  (cost=0.00..151204.00 rows=98100 width=208)
        Filter: ((to_char(period, 'YYYY'::text) = '2026'::text) AND (SubPlan 1))
        SubPlan 1
          ->  Seq Scan on склады  (cost=0.00..42.10 rows=8 width=12)""",
        2840,
    ),
    (
        "MS SQL Server",
        "Проводки по счёту 51 за период",
        """select top 1000 p.Сумма, p.Содержание
from Проводки p
join Счета s on s.Код = p.СчётДт
where convert(varchar(10), p.Период, 104) between '01.10.2026' and '31.10.2026'
  and p.Содержание like '%оплата%'""",
        """|--Clustered Index Scan (OBJECT:([Проводки].[PK_Проводки]))
     |--Filter(WHERE:(like([p].[Содержание],'%оплата%')))
     --Estimated rows: 1200000, Actual rows: 985000""",
        5120,
    ),
    (
        "PostgreSQL",
        "Топ контрагентов по выручке",
        """select к.наименование, sum(р.сумма) as выручка
from реализации р, контрагенты к
where р.контрагент_id = к.id
group by к.наименование
order by выручка desc
limit 20""",
        """Limit  (cost=91234.00..91234.05 rows=20 width=64)
  ->  Sort
        Sort Key: (sum(сумма)) DESC
        ->  HashAggregate
              ->  Hash Join
                    Hash Cond: (р.контрагент_id = к.id)
                    ->  Seq Scan on реализации р
                    ->  Hash  (rows=12000)
                          ->  Seq Scan on контрагенты к""",
        1760,
    ),
    (
        "MS SQL Server",
        "Карточка счёта с фильтром по дате",
        """select Номер, Дата, Сумма
from Документы
where year(Дата) = 2026 and month(Дата) = 10
  and Сумма > 0
order by Дата""",
        """|--Sort(ORDER BY:([Дата] ASC))
     |--Clustered Index Scan (OBJECT:([Документы].[PK_Документы]), WHERE:([Сумма]>(0)))
     --Estimated rows: 2400000""",
        4380,
    ),
]

TICKETS = [
    ("Не печатается счёт на оплату", "При попытке распечатать счёт на оплату из документа Реализация товаров и услуг выдаёт ошибку «Не удалось подключить расширение печати». Печать из других документов работает.", "1С: Бухгалтерия", "средний", "closed", 8),
    ("Медленно проводится реализация", "Проведение документа Реализация товаров и услуг занимает больше двух минут, за прошлую неделю было 15 секунд. База Бухгалтерия 3.0.", "1С: Бухгалтерия", "высокий", "open", 4),
    ("Не формируется отчёт ОСВ", "При формировании оборотно-сальдовой ведомости за октябрь отчёт зависает и закрывается. Остальные отчёты формируются нормально.", "1С: Бухгалтерия", "высокий", "open", 4),
    ("Ошибка обновления конфигурации", "После обновления на 3.0.160 при запуске появляется сообщение о несовпадении структуры данных. Требуется помощь в завершении обновления.", "Обновление и администрирование", "критический", "open", 2),
    ("Нет доступа к документу ЗУП", "Не открывается документ Приём на работу, пишет «Недостаточно прав для просмотра». Раньше доступ был.", "1С: ЗУП", "средний", "open", 8),
    ("Восстановить копию базы", "Просим восстановить базу Бухгалтерия на тестовый сервер из копии за 5 ноября для проверки отчётов.", "Резервное копирование", "средний", "open", 8),
    ("Не приходит уведомление об ЭДО", "Контрагент отправил документ через Диадок, в 1С: Документооборот уведомление не появилось, документ не загрузился.", "1С: Документооборот", "высокий", "open", 4),
    ("Забыл пароль от базы", "Не могу войти в базу, забыл пароль. Прошу сбросить и выдать новый.", "Пользователи и права", "низкий", "closed", 24),
    ("Создать нового пользователя", "Принять на работу бухгалтера, нужен доступ к базе Бухгалтерия с правами бухгалтера и просмотром отчётов.", "Пользователи и права", "низкий", "closed", 24),
    ("Закрыть доступ уволенному", "Сотрудник уволился 3 ноября, просим закрыть доступ к информационным базам.", "Пользователи и права", "средний", "open", 8),
    ("Зависает веб-клиент", "При работе через веб-клиент в браузере страница периодически перестаёт отвечать, особенно при открытии списка документов.", "Серверы и производительность", "высокий", "open", 4),
    ("Закончилось место на диске", "Сервер СУБД пишет, что недостаточно места на диске D, резервные копии не создаются.", "Серверы и производительность", "критический", "open", 2),
    ("Не открывается отчёт по зарплате", "Отчёт Расчётные листки за октябрь выдаёт пустой результат, хотя начисления есть.", "1С: ЗУП", "средний", "closed", 8),
    ("Ошибка при выгрузке в банк", "При выгрузке платёжных поручений в клиент-банк файл формируется пустой.", "1С: Бухгалтерия", "средний", "open", 8),
    ("Настроить новое рабочее место", "Новому сотруднику отдела продаж требуется настроить рабочее место и доступ к базе УНФ.", "Пользователи и права", "низкий", "closed", 24),
    ("Не сходится сумма в акте сверки", "Акт сверки с контрагентом не сходится на 12 400 рублей, просим помочь разобраться в проводках.", "1С: Бухгалтерия", "средний", "open", 8),
    ("Медленно открывается список номенклатуры", "Список номенклатуры открывается больше минуты, в нём около 40 тысяч позиций.", "Серверы и производительность", "средний", "open", 8),
    ("Не проходит обмен с сайтом", "Обмен заказами с сайтом останавливается на этапе загрузки заказов, в журнале ошибка соединения.", "Интеграции и обмены", "высокий", "open", 4),
    ("Требуется доработка печатной формы", "Нужно добавить в печатную форму счёта логотип и подпись руководителя.", "Доработки и расширения", "низкий", "open", 24),
    ("Ошибка блокировки при проведении", "При одновременном проведении документов возникает ошибка блокировки таблицы регистра.", "Серверы и производительность", "высокий", "closed", 4),
    ("Не загружается классификатор адресов", "При запуске программа предлагает загрузить классификатор адресов, загрузка прерывается.", "Обновление и администрирование", "низкий", "closed", 24),
    ("Просим расширение отчёта", "Нужен отчёт по продажам в разрезе менеджеров с фильтром по периоду, лучше как расширение конфигурации.", "Доработки и расширения", "средний", "open", 8),
]

KB = [
    ("Очистка кэша и перезапуск сеанса", "Если документ не открывается или печать выдаёт ошибку, очистите кэш: сервис и поддержка, затем очистка кэша. После этого перезапустите клиент. На сервере проверьте журнал регистрации за время ошибки.", "1С: Бухгалтерия"),
    ("Медленное проведение документов", "Проверьте активные блокировки через технологический журнал и статистику СУБД. Убедитесь, что регламентные задания не пересекаются с проведением, при необходимости перестройте индексы регистров.", "Серверы и производительность"),
    ("Недостаточно прав для просмотра", "Проверьте роли пользователя в списке пользователей информационной базы, затем права роли на объект. После изменений требуется перезапуск сеанса пользователя.", "Пользователи и права"),
    ("Восстановление из резервной копии", "Остановите информационную базу, восстановите дамп на тестовый сервер, проверьте целостность через chdbfl или утилиту СУБД, затем переключите пользователей на восстановленную базу.", "Резервное копирование"),
    ("Ошибка обновления конфигурации", "Завершите обновление в монопольном режиме: сделайте резервную копию, запустите конфигуратор, выполните обновление конфигурации базы данных с проверкой структуры. Расширения обновляйте после типовой.", "Обновление и администрирование"),
    ("Нет места на диске сервера СУБД", "Освободите место: удалите устаревшие копии по политике хранения, проверьте журналы транзакций и временные файлы. Для PostgreSQL выполните vacuum, для MS SQL Server проверьте рост файлов журнала.", "Серверы и производительность"),
    ("Обмен с сайтом не проходит", "Проверьте доступность сервиса обмена, корректность адреса и учётных данных, затем в журнале обмена посмотрите последний успешный пакет и повторно загрузите заказы после восстановления соединения.", "Интеграции и обмены"),
    ("Доработка через расширение", "Изменения выполняйте в расширении конфигурации: создайте расширение, включите режим безопасного изменения, перенесите объекты и проверьте работу в копии базы перед публикацией.", "Доработки и расширения"),
]

XBR_L_NS = "http://www.cbr.ru/xbrl/nfo"

XBR_RP = """<?xml version="1.0" encoding="UTF-8"?>
<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:ru="http://www.cbr.ru/xbrl/nfo">
  <xbrli:context id="Y2026">
    <xbrli:period><xbrli:startDate>2026-01-01</xbrli:startDate><xbrli:endDate>2026-09-30</xbrli:endDate></xbrli:period>
    <xbrli:entity><xbrli:identifier scheme="inn">7707083893</xbrli:identifier></xbrli:entity>
  </xbrli:context>
  <ru:НаименованиеОрганизации contextRef="Y2026">ПАО «Внутренние учётные системы»</ru:НаименованиеОрганизации>
  <ru:АктивыВсего contextRef="Y2026" unitRef="RUB" decimals="0">184250000</ru:АктивыВсего>
  <ru:Обязательства contextRef="Y2026" unitRef="RUB" decimals="0">96400000</ru:Обязательства>
  <ru:Капитал contextRef="Y2026" unitRef="RUB" decimals="0">87850000</ru:Капитал>
  <ru:Выручка contextRef="Y2026" unitRef="RUB" decimals="0">512700000</ru:Выручка>
  <ru:ЧистаяПрибыль contextRef="Y2026" unitRef="RUB" decimals="0">42100000</ru:ЧистаяПрибыль>
</xbrli:xbrl>"""

XBR_RP_DEFECT = """<?xml version="1.0" encoding="UTF-8"?>
<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:ru="http://www.cbr.ru/xbrl/nfo">
  <xbrli:context id="Q3">
    <xbrli:period><xbrli:startDate>2026-07-01</xbrli:startDate><xbrli:endDate>2026-09-30</xbrli:endDate></xbrli:period>
    <xbrli:entity><xbrli:identifier scheme="inn">7707083893</xbrli:identifier></xbrli:entity>
  </xbrli:context>
  <ru:НаименованиеОрганизации contextRef="Q3">ПАО «Внутренние учётные системы»</ru:НаименованиеОрганизации>
  <ru:АктивыВсего contextRef="Q3" unitRef="RUB" decimals="0">184250000</ru:АктивыВсего>
  <ru:Обязательства contextRef="Q3" unitRef="RUB" decimals="0">96400000</ru:Обязательства>
  <ru:Капитал contextRef="Q3" unitRef="RUB" decimals="0">97850000</ru:Капитал>
  <ru:Выручка contextRef="Q3" unitRef="RUB" decimals="0">-1250000</ru:Выручка>
</xbrli:xbrl>"""

DOCUMENTS = [
    ("Счёт № 2145 от 03.11.2026.txt", "Счёт на оплату № 2145 от 03 ноября 2026 года. Поставщик: ООО «Северный поставщик», ИНН 7701234567. Покупатель: ПАО «Внутренние учётные системы». Услуги по сопровождению 1С: Бухгалтерия, сумма 148 000,00 руб., в том числе НДС 20%.", None),
    ("Акт № 118 от 31.10.2026.txt", "Акт оказанных услуг № 118 от 31 октября 2026 года по договору № 44/2026. Исполнитель: ООО «Консалт-Плюс», ИНН 7809876543. Стоимость работ 96 500,00 руб., НДС не облагается.", None),
    ("Договор поставки № 44-2026.txt", "Договор поставки № 44-2026 от 12 октября 2026 года. Поставщик: ООО «Северный поставщик», ИНН 7701234567. Покупатель: ПАО «Внутренние учётные системы». Предмет: поставка серверного оборудования, сумма 620 000,00 руб.", None),
    ("Накладная ТОРГ-12 № 9001.txt", "Товарная накладная № 9001 от 28.10.2026. Грузоотправитель: ООО «Складская логистика», ИНН 500100732259. Получатель: ПАО «Внутренние учётные системы». Товар: источники бесперебойного питания, 4 шт., сумма 312 400,00 руб.", None),
    ("Счёт № 3150 от 05.11.2026.txt", "Счёт на оплату № 3150 от 05 ноября 2026. Поставщик: ООО «Софт-Дистрибуция», ИНН 7701234568. Покупатель: ПАО «Внутренние учётные системы». Лицензии 1С: Предприятие 8, сумма 87 500,00 руб., НДС 20%.", None),
    ("Акт сверки за 9 месяцев.txt", "Акт сверки взаимных расчётов за 9 месяцев 2026 года между ПАО «Внутренние учётные системы» и ООО «Консалт-Плюс», ИНН 7809876543. Сальдо на 30.09.2026 — 24 100,00 руб.", None),
    ("Счёт № 4410 от 06.11.2026.txt", "Счёт на оплату № 4410 от 06 ноября 2026. Поставщик: ООО «Сервисный центр», ИНН 7707083894. Покупатель: ПАО «Внутренние учётные системы». Ремонт серверного оборудования, сумма 54 900,00 руб.", None),
    ("Служебная записка.txt", "Служебная записка от отдела продаж о согласовании скидки клиенту, требуется рассмотреть на совещании.", None),
]

CORPUS_TRAIN = [
    ("счёт", "Счёт на оплату № 2145 от 03.11.2026, сумма 148000 руб, НДС 20%, поставщик ООО, оплатить в течение 5 дней"),
    ("счёт", "Счёт на оплату лицензии 1С, сумма, в том числе НДС, покупатель оплачивает по реквизитам"),
    ("акт", "Акт оказанных услуг по договору, стоимость работ, НДС не облагается, подписан сторонами"),
    ("акт", "Акт сверки взаимных расчётов, сальдо на конец периода, задолженность перед контрагентом"),
    ("договор", "Договор поставки оборудования, предмет договора, сроки поставки, штрафные санкции, оплата по факту"),
    ("договор", "Договор оказания услуг, стороны заключили договор, приложения, реквизиты сторон, подписи"),
    ("накладная", "Товарная накладная, грузоотправитель, грузополучатель, товар, количество, сумма, склад"),
    ("накладная", "Транспортная накладная, перевозчик, груз, вес, сопроводительные документы, приёмка"),
    ("записка", "Служебная записка, согласование скидки, руководитель отдела просит рассмотреть вопрос"),
    ("записка", "Заявка на закупку канцелярии, обоснование необходимости, подпись начальника отдела"),
]


def _empty(table):
    return db.scalar(f"select count(*) from {table}") == 0


def _insert_sql(table, columns):
    return f"insert into {table} ({', '.join(columns)}) values ({', '.join(['%s'] * len(columns))})"


def _insert_one(sql, row):
    return db.execute(sql, tuple(row))


def _insert_many(table, columns, rows):
    sql = _insert_sql(table, columns)
    return len([_insert_one(sql, row) for row in rows])


def _line(base, spread, bumps=None):
    bumps = bumps or {}
    return [round(base + RNG.uniform(-spread, spread) + bumps.get(index, 0.0), 1) for index in range(STEPS)]


def _metrics_rows():
    return [(code, metric, START + timedelta(minutes=STEP_MINUTES * index), value) for code, profile in PROFILES.items() for metric, (base, spread, bumps) in profile.items() for index, value in enumerate(_line(base, spread, bumps))]


def _session_rows():
    return [("c1-app-01", login, app, NOW - timedelta(minutes=17 * index), 12 + (index * 7) % 95, 40 + (index * 37) % 900) for index, (login, _, _, _) in enumerate([*LOGINS, *LOGINS]) for app in ["Тонкий клиент"] if index % 3 == 0 or app]


def _backup_rows():
    return [(name, host, schedule, retention, status, NOW - timedelta(hours=4 + index), size, rpo) for index, (name, host, schedule, retention, status, size, rpo) in enumerate(BACKUP_JOBS)]


def _log_rows():
    return [(job + 1, NOW - timedelta(minutes=35 * index), level, message) for index, (job, level, message) in enumerate(BACKUP_LOGS)]


def _user_rows():
    return [(login, name, position, department, login != "v.lebedev", datetime(2019 + index % 6, 1 + index % 12, 1).date(), datetime(2026, 10, 31).date() if login == "v.lebedev" else None) for index, (login, name, position, department) in enumerate(LOGINS)]


def _role_rows():
    return [(code, title, admin) for code, title, admin in ROLES]


def _user_role_rows():
    return [(LOGINS.index(next(item for item in LOGINS if item[0] == login)) + 1, ROLES.index(next(item for item in ROLES if item[0] == role)) + 1) for login, roles in USER_ROLES for role in roles]


def _right_rows():
    return [(ROLES.index(next(item for item in ROLES if item[0] == role)) + 1, kind, name, level) for role, kind, name, level in RIGHTS]


def _version_rows():
    return [(name, version, datetime.strptime(released, "%Y-%m-%d").date(), total, extended) for name, version, released, total, extended in CONF_VERSIONS]


def _object_rows():
    versions = {version: index + 1 for index, (_, version, *_rest) in enumerate(CONF_VERSIONS)}
    return [(versions[version], kind, name, checksum) for version, objects in OBJECTS_BY_VERSION.items() for kind, name, checksum in objects]


def _ticket_rows():
    return [(subject, body, NOW - timedelta(hours=3 * index), group, priority, status, sla, NOW - timedelta(hours=2) if status == "closed" else None) for index, (subject, body, group, priority, status, sla) in enumerate(TICKETS)]


def _kb_rows():
    return [(title, body, group) for title, body, group in KB]


def _xbrl_rows():
    return [
        ("9 месяцев 2026", "ПАО «Внутренние учётные системы»", "0420501", "balance_2026q3.xbrl", XBR_RP),
        ("3 квартал 2026", "ПАО «Внутренние учётные системы»", "0420501", "balance_2026q3_defect.xbrl", XBR_RP_DEFECT),
        ("2025 год", "ПАО «Внутренние учётные системы»", "0420501", "balance_2025.xbrl", XBR_RP),
    ]


def _document_rows():
    return [(name, body, NOW - timedelta(hours=5 * index)) for index, (name, body, _) in enumerate(DOCUMENTS)]


def _sql_rows():
    return [(dbms, title, query, plan, duration) for dbms, title, query, plan, duration in SQL_SAMPLES]


def seed_hosts():
    return _insert_many("hosts", ["code", "name", "role", "dbms", "cores"], HOSTS) if _empty("hosts") else 0


def seed_metrics():
    return _insert_many("metrics", ["host_code", "metric", "ts", "value"], _metrics_rows()) if _empty("metrics") else 0


def seed_sessions():
    return _insert_many("sessions", ["host_code", "login", "app", "started_at", "duration_min", "calls"], _session_rows()) if _empty("sessions") else 0


def seed_backups():
    return _insert_many("backup_jobs", ["base_name", "host_code", "schedule", "retention_days", "last_status", "last_run", "size_mb", "rpo_hours"], _backup_rows()) if _empty("backup_jobs") else 0


def seed_backup_logs():
    return _insert_many("backup_logs", ["job_id", "ts", "level", "message"], _log_rows()) if _empty("backup_logs") else 0


def seed_users():
    return _insert_many("users", ["login", "full_name", "position", "department", "is_active", "hired_at", "fired_at"], _user_rows()) if _empty("users") else 0


def seed_roles():
    return _insert_many("roles", ["code", "title", "is_admin"], _role_rows()) if _empty("roles") else 0


def seed_user_roles():
    return _insert_many("user_roles", ["user_id", "role_id"], _user_role_rows()) if _empty("user_roles") else 0


def seed_rights():
    return _insert_many("rights", ["role_id", "object_kind", "object_name", "access_level"], _right_rows()) if _empty("rights") else 0


def seed_versions():
    return _insert_many("conf_versions", ["config_name", "version", "released_at", "objects_total", "extended"], _version_rows()) if _empty("conf_versions") else 0


def seed_objects():
    return _insert_many("conf_objects", ["version_id", "kind", "name", "checksum"], _object_rows()) if _empty("conf_objects") else 0


def seed_sql():
    return _insert_many("sql_samples", ["dbms", "title", "query_text", "plan_text", "duration_ms"], _sql_rows()) if _empty("sql_samples") else 0


def seed_tickets():
    return _insert_many("tickets", ["subject", "body", "created_at", "group_name", "priority", "status", "sla_hours", "closed_at"], _ticket_rows()) if _empty("tickets") else 0


def seed_kb():
    return _insert_many("kb_articles", ["title", "body", "group_name"], _kb_rows()) if _empty("kb_articles") else 0


def seed_xbrl():
    return _insert_many("xbrl_reports", ["period", "entity", "form_code", "file_name", "xml_text"], _xbrl_rows()) if _empty("xbrl_reports") else 0


def seed_documents():
    return _insert_many("documents", ["file_name", "body", "received_at"], _document_rows()) if _empty("documents") else 0


STEPS_ALL = (
    seed_hosts,
    seed_metrics,
    seed_sessions,
    seed_backups,
    seed_backup_logs,
    seed_users,
    seed_roles,
    seed_user_roles,
    seed_rights,
    seed_versions,
    seed_objects,
    seed_sql,
    seed_tickets,
    seed_kb,
    seed_xbrl,
    seed_documents,
)


def seed_all():
    return {step.__name__: step() for step in STEPS_ALL}
