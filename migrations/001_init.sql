-- Схема портфеля: восемь прикладных модулей в одной базе.
-- Все таблицы создаются идемпотентно, чтобы миграция запускалась при каждом старте.

-- P1. Мониторинг серверов 1С
create table if not exists hosts (
    id serial primary key,
    code text unique not null,
    name text not null,
    role text not null,
    dbms text not null,
    cores int not null default 4
);

create table if not exists metrics (
    id bigserial primary key,
    host_code text not null references hosts (code),
    metric text not null,
    ts timestamptz not null,
    value double precision not null
);

create index if not exists metrics_host_metric_ts on metrics (host_code, metric, ts);

create table if not exists sessions (
    id serial primary key,
    host_code text not null references hosts (code),
    login text not null,
    app text not null,
    started_at timestamptz not null,
    duration_min int not null,
    calls int not null
);

-- P2. Резервное копирование
create table if not exists backup_jobs (
    id serial primary key,
    base_name text not null,
    host_code text not null,
    schedule text not null,
    retention_days int not null default 14,
    last_status text not null default 'ok',
    last_run timestamptz,
    size_mb int not null default 0,
    rpo_hours int not null default 24
);

create table if not exists backup_logs (
    id bigserial primary key,
    job_id int not null references backup_jobs (id),
    ts timestamptz not null,
    level text not null,
    message text not null
);

-- P3. Права доступа
create table if not exists users (
    id serial primary key,
    login text unique not null,
    full_name text not null,
    position text not null,
    department text not null,
    is_active boolean not null default true,
    hired_at date not null,
    fired_at date
);

create table if not exists roles (
    id serial primary key,
    code text unique not null,
    title text not null,
    is_admin boolean not null default false
);

create table if not exists user_roles (
    user_id int not null references users (id),
    role_id int not null references roles (id),
    primary key (user_id, role_id)
);

create table if not exists rights (
    id serial primary key,
    role_id int not null references roles (id),
    object_kind text not null,
    object_name text not null,
    access_level text not null
);

-- P4. Обновления конфигураций
create table if not exists conf_versions (
    id serial primary key,
    config_name text not null,
    version text not null,
    released_at date not null,
    objects_total int not null,
    extended boolean not null default false,
    unique (config_name, version)
);

create table if not exists conf_objects (
    id bigserial primary key,
    version_id int not null references conf_versions (id),
    kind text not null,
    name text not null,
    checksum text not null
);

create index if not exists conf_objects_version on conf_objects (version_id);

-- P5. SQL-аналитик
create table if not exists sql_samples (
    id serial primary key,
    dbms text not null,
    title text not null,
    query_text text not null,
    plan_text text not null,
    duration_ms int not null
);

-- P6. Service Desk
create table if not exists tickets (
    id serial primary key,
    subject text not null,
    body text not null,
    created_at timestamptz not null,
    group_name text not null,
    priority text not null,
    status text not null,
    sla_hours int not null,
    closed_at timestamptz
);

create table if not exists kb_articles (
    id serial primary key,
    title text not null,
    body text not null,
    group_name text not null
);

-- P7. XBRL / XML отчётность
create table if not exists xbrl_reports (
    id serial primary key,
    period text not null,
    entity text not null,
    form_code text not null,
    file_name text not null,
    xml_text text not null,
    loaded_at timestamptz not null default now()
);

-- P8. Электронный документооборот
create table if not exists documents (
    id serial primary key,
    file_name text not null,
    body text not null,
    received_at timestamptz not null,
    doc_type text,
    counterparty text,
    inn text,
    amount numeric(14, 2)
);
