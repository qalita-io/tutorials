## Docker Compose Deployment

### Prerequisites

To deploy locally on your computer, you will need:

- Docker
- Docker Compose
- Internet
- A valid license key [📀 Purchase a license](https://qalita.io) or [contact us to get a trial key](mailto:contact@qalita.io)

**The license key allows you to connect to the Docker registry and pull Docker images, in addition to adding information for the platform.**

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
