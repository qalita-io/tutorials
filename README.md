# QALITA Tutorials

<p align="center">
  <img width="250px" height="auto" src="https://cloud.platform.qalita.io/logo.svg" style="max-width:250px;"/>
</p>

## Introduction

Welcome to the Qalita tutorials! Here you will find a collection of tutorials to help you get started ! 🚀

This repo will store data examples, and code examples for tutorials in the [documentation](https://doc.qalita.io/)

## Table of Contents

### Onboarding

* [Get Started]()

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
| **Source**         | Register a source from local Agent     | [Guide](#)                                                                                                         |
|                    | Register a source from CI/CD           | [Guide](#)                                                                                                         |
|                    | Register a source from a remote agent  | [Guide](#)                                                                                                         |
| **Pack**           | Create a pack                          | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#create-a-pack)                      |
|                    | Test a pack locally                    | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#test-a-pack)                        |
|                    | Push a pack                            | [Guide](https://doc.qalita.io/docs/platform/user-guides/data-engineering/packs#publish-a-pack)                     |

### QALITA CLI Integration

| Category                    | Integration       | Link                   |
| --------------------------- | ----------------- | ---------------------- |
| **ETL**                     | DBT               | [DBT](#)               |
| **Data Orchestration**      | Airflow           | [Airflow](#)           |
|                             | Dagster           | [Dagster](#)           |
| **Data Quality Frameworks** | soda              | [soda](#)              |
|                             | great-expecations | [great-expecations](#) |

### QALITA Platfrom Integration

| Category                                                                                                                               | Integration        | Link                    |
| -------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ----------------------- |
| **Issue Management** , add integration to your ticketing platform to receive and synchronize data quality issues from QALITA Platform. | Gitlab             | [Gitlab](#)             |
|                                                                                                                                        | Jira               | [Jira](#)               |
| **Alerting** , receive notifications on data quality score decrease directly to your communication feed.                               | Teams              | [Teams](#)              |
|                                                                                                                                        | Slack              | [Slack](#)              |
| **Reporting** , use your favorite reporting tool to fetch data quality metrics from QALITA Platform.                                   | Tableau            | [Tableau](#)            |
|                                                                                                                                        | Power BI           | [Power BI](#)           |
|                                                                                                                                        | Looker             | [Looker](#)             |
|                                                                                                                                        | Apache Superset    | [Apache Superset](#)    |
|                                                                                                                                        | Grafana            | [Grafana](#)            |
| **Data Catalog & Governance** , enrich your data catalog and governance platform with data quality metrics from QALITA Platform        | Collibra           | [Collibra](#)           |
|                                                                                                                                        | Atlation           | [Atlation](#)           |
|                                                                                                                                        | Microsoft Pureview | [Microsoft Pureview](#) |
|                                                                                                                                        | Datahub            | [Datahub](#)            |
|                                                                                                                                        | Apache Atlas       | [Apache Atlas](#)       |