# QALITA Tutorials

<p align="center">
  <img width="250px" height="auto" src="https://cloud.platform.qalita.io/logo.svg" style="max-width:250px;"/>
</p>

## Introduction

Welcome to the Qalita tutorials! Here you will find a collection of tutorials to help you get started ! 🚀

This repo will store data examples, and code examples for tutorials in the [documentation](https://doc.qalita.io/)

## Table of Contents

### Onboarding

* [Get Started](https://doc.qalita.io/docs/platform/quick-start)

### General use cases

| Category           | Task                                   | Link                                                                                                               |
| ------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Deployment**     | Deploy Platform with Docker Compose    | [Guide](./deploy/docker-compose)                                                                                   |
|                    | Deploy Platform with Helm              | [Guide](https://doc.qalita.io/docs/platform/user-guides/admin/deploy#requirements-1)                               |
| **Authentication** | Setup LDAP authentication              | [Guide](https://doc.qalita.io/docs/platform/user-guides/admin/users-management/#ldap-registry)                     |
|                    | Setup Microsoft Entra authentication   | [Guide](https://doc.qalita.io/docs/platform/user-guides/admin/users-management/#microsoft-authentication-oidcsaml) |
| **Agent**          | Deploy an agent locally on Windows     | [Guide](https://doc.qalita.io/docs/cli/quick-start)                                                                |
|                    | Deploy an agent locally on Linux/MacOS | [Guide](https://doc.qalita.io/docs/cli/quick-start)                                                                |
|                    | Deploy an agent with Docker            | [Guide](https://doc.qalita.io/docs/cli/docker)                                                                     |
|                    | Deploy an agent with Kubernetes        | [Guide](https://artifacthub.io/packages/helm/qalita/qalita#agent)                                                  |
| **Source**         | Register a source from local Agent     | [Guide](./source/local-agent.md)                                                                                   |
|                    | Register a source from CI/CD           | [Guide](#)                                                                                                         |
|                    | Register a source from a remote agent  | [Guide](#)                                                                                                         |
| **Pack**           | Create a pack                          | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#create-a-pack)                      |
|                    | Test a pack locally                    | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#test-a-pack)                        |
|                    | Push a pack                            | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#publish-a-pack)                     |

### QALITA Data Engineering Integration

| Category                    | Integration                                                                                                                      | Link                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **ELT** , export metadata and results from quality checks within your ELT to QALITA Platform.                     | <img alt="dbt" src="https://cdn.simpleicons.org/dbt" height="16" /> DBT                                                          | [Guide](./integrations/data-engineering/elt/dbt)                                 |
|                             | <img alt="Airbyte" src="https://cdn.simpleicons.org/Airbyte" height="16" /> Airbyte                                              | [Guide](./integrations/data-engineering/elt/airbyte)                         |
| **Data Orchestration** , implement quality checks steps into your data pipelines and push metadata results into QALITA Platform.     | <img alt="Apache Airflow" src="https://cdn.simpleicons.org/apacheairflow" height="16" /> Airflow                                 | [Guide](./integrations/data-engineering/orchestration/airflow)                         |
|                             | <img alt="Dagster" src="https://docs.dagster.io/images/dagster-primary-mark.svg" height="16" /> Dagster                          | [Guide](./integrations/data-engineering/orchestration/dagster)                         |
| **Data Quality Frameworks** , use state-of-the-art data quality checks frameworks seamlessly with QALITA Platform. | <img alt="Soda" src="https://avatars.githubusercontent.com/u/45313710?s=280&v=4" height="16" />  Soda                            | [Guide](./integrations/data-quality/soda)                               |
|                             | <img alt="Great Expectations" src="https://avatars.githubusercontent.com/u/31670619?s=200&v=4" height="16" /> Great Expectations | [Guide](./integrations/data-quality/great-expectations) |

### QALITA Platform Integration

| Category                                                                                                                               | Integration                                                                                                                                                                                                                            | Link                                                                                                    |
| -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Issue Management** , add integration to your ticketing platform to receive and synchronize data quality issues from QALITA Platform. | <img alt="GitLab" src="https://cdn.simpleicons.org/gitlab" height="16" /> Gitlab                                                                                                                                                       | [Guide](./integrations/platform/issue-management/gitlab)                           |
|                                                                                                                                        | <img alt="Jira" src="https://cdn.simpleicons.org/jira" height="16" /> Jira                                                                                                                                                             | [Guide](./integrations/platform/issue-management/jira)                               |
| **Alerting** , receive notifications on data quality score decrease directly to your communication feed.                               | <img alt="Microsoft Teams" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Microsoft_Office_Teams_%282018%E2%80%93present%29.svg/1200px-Microsoft_Office_Teams_%282018%E2%80%93present%29.svg.png" height="16" /> Teams | [Guide](./integrations/platform/alerting/teams)                             |
|                                                                                                                                        | <img alt="Slack" src="https://cdn.simpleicons.org/slack" height="16" /> Slack                                                                                                                                                          | [Guide](./integrations/platform/alerting/slack)                             |
| **Reporting** , use your favorite reporting tool to fetch data quality metrics from QALITA Platform.                                   | <img alt="Tableau" src="https://www.svgrepo.com/show/354428/tableau-icon.svg" height="16" /> Tableau                                                                                                                                   | [Guide](./integrations/platform/reporting/tableau)                         |
|                                                                                                                                        | <img alt="Power BI" src="https://1000logos.net/wp-content/uploads/2022/08/Microsoft-Power-BI-Logo-2013.png" height="16" /> Power BI                                                                                                    | [Guide](./integrations/platform/reporting/power-bi)                     |
|                                                                                                                                        | <img alt="Looker" src="https://cdn.simpleicons.org/looker" height="16" /> Looker                                                                                                                                                       | [Guide](./integrations/platform/reporting/looker)                           |
|                                                                                                                                        | <img alt="Apache Superset" src="https://cdn.simpleicons.org/apachesuperset" height="16" /> Apache Superset                                                                                                                             | [Guide](./integrations/platform/reporting/apache-superset)       |
|                                                                                                                                        | <img alt="Grafana" src="https://cdn.simpleicons.org/grafana" height="16" /> Grafana                                                                                                                                                    | [Guide](./integrations/platform/reporting/grafana)                         |
| **Data Catalog & Governance** , enrich your data catalog and governance platform with data quality metrics from QALITA Platform        | <img alt="Collibra" src="https://billigence.com/wp-content/uploads/2022/08/6-e1720040805903.png" height="16" /> Collibra                                                                                                               | [Guide](./integrations/platform/catalog-governance/collibra)                       |
|                                                                                                                                        | <img alt="Microsoft Purview" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Microsoft_Purview_Logo.svg/2048px-Microsoft_Purview_Logo.svg.png" height="16" /> Microsoft Purview                                       | [Guide](./integrations/platform/catalog-governance/microsoft-purview) |
|                                                                                                                                        | <img alt="DataHub" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6oohh6MJ_UjYi6g75YfHlmr7HWLhH6XAoxg&s" height="16" /> Datahub                                                                                           | [Guide](./integrations/platform/catalog-governance/datahub)                         |