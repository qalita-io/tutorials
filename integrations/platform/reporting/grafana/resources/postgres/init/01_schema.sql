CREATE SCHEMA IF NOT EXISTS reporting;

SET search_path TO reporting;

CREATE TABLE IF NOT EXISTS metrics_daily (
  metric_date DATE NOT NULL,
  project TEXT NOT NULL,
  domain TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value NUMERIC(18,4) NOT NULL,
  tags JSONB,
  PRIMARY KEY (metric_date, project, domain, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_metrics_daily_metric_name
  ON metrics_daily(metric_name);

CREATE INDEX IF NOT EXISTS idx_metrics_daily_project_date
  ON metrics_daily(project, metric_date);

CREATE TABLE IF NOT EXISTS issues (
  issue_id TEXT PRIMARY KEY,
  project TEXT NOT NULL,
  domain TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_issues_project_status
  ON issues(project, status);

CREATE INDEX IF NOT EXISTS idx_issues_created_at
  ON issues(created_at);


