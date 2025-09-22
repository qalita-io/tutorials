-- QALITA → Warehouse schema (Postgres compatible)
-- Tables: qalita_metrics, qalita_issues

create table if not exists qalita_metrics (
    id bigint primary key,
    partner_id bigint not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    key text not null,
    value text,
    source_id bigint not null,
    source_version_id bigint not null,
    pack_id bigint not null,
    pack_version_id bigint not null,
    scope jsonb
);

create index if not exists ix_qalita_metrics_created_at on qalita_metrics (created_at desc);
create index if not exists ix_qalita_metrics_source on qalita_metrics (source_id);
create index if not exists ix_qalita_metrics_pack on qalita_metrics (pack_id);
create index if not exists ix_qalita_metrics_key on qalita_metrics (key);
create index if not exists ix_qalita_metrics_scope_perimeter on qalita_metrics ((scope->>'perimeter'));

-- Composite uniqueness for latest-only semantics can be implemented with materialized views if needed.

create table if not exists qalita_issues (
    id bigint primary key,
    partner_id bigint not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    title text,
    description text,
    status text,
    url text,
    chat_url text,
    source_id bigint,
    assignee bigint,
    scope jsonb,
    due_date timestamptz,
    author_id bigint,
    closed_at timestamptz,
    updated_by bigint,
    closed_by bigint
);

create index if not exists ix_qalita_issues_created_at on qalita_issues (created_at desc);
create index if not exists ix_qalita_issues_status on qalita_issues (status);
create index if not exists ix_qalita_issues_source on qalita_issues (source_id);
create index if not exists ix_qalita_issues_assignee on qalita_issues (assignee);
create index if not exists ix_qalita_issues_scope_perimeter on qalita_issues ((scope->>'perimeter'));


