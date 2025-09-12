## Docker Compose Deployment

### Prerequisites

To deploy locally on your computer, you will need:

- Docker
- Docker Compose
- Internet
- A valid license key [📀 Purchase a license](https://qalita.io) or [contact us to get a trial key](mailto:contact@qalita.io)

:::info
La clé de licence permet de se connecter au docker registry et de pull les images docker, en plus d'ajouter des informations pour la plateforme.
:::

1. Sign in to the Docker image registry:

```bash
docker login qalita.azurecr.io
```

2. Create these two files:

- docker-compose.yaml
- s3_config.json

1. Run Docker Compose:

```bash
docker-compose up -d
```
