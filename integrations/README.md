## QALITA Integrations (Draft)

This folder contains draft guides for integrating external tools and platforms with QALITA. Each integration README explains the high-level architecture, how the integration interacts with `app-backend` (REST API and background jobs) and references relevant documentation from `app-doc`.

Structure:

- data-engineering
  - elt
    - dbt
    - airbyte
  - orchestration
    - airflow
    - dagster
- data-quality
  - soda
  - great-expectations
- platform
  - issue-management
    - gitlab
    - jira
  - alerting
    - teams
    - slack
  - reporting
    - tableau
    - power-bi
    - looker
    - apache-superset
    - grafana
  - catalog-governance
    - collibra
    - atlation
    - microsoft-purview
    - datahub

Conventions used in these drafts:

- "Backend touchpoints" reference directories in `app-backend` such as `src/backend/routers/v2/`, `src/backend/database/model/`, and long-running tasks in `src/backend/services/` or `src/backend/workers/` if applicable.
- Documentation references point to `app-doc` or to the public docs site, to be refined once the exact pages exist.
- Replace placeholders like <your_value> and TODO links with concrete values during implementation.


