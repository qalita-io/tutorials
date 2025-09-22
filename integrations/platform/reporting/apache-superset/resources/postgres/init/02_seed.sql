SET search_path TO reporting;

COPY metrics_daily (metric_date, project, domain, metric_name, metric_value, tags)
FROM '/docker-entrypoint-initdb.d/seeds/metrics_daily.csv'
WITH (FORMAT csv, HEADER true);

COPY issues (issue_id, project, domain, severity, status, created_at, resolved_at)
FROM '/docker-entrypoint-initdb.d/seeds/issues.csv'
WITH (FORMAT csv, HEADER true);
