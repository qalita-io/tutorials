## Déploiement Docker Compose

### Prérequis

Pour déployer en local sur votre ordinateur, il vous faudra :

- Docker
- Docker-compose
- Internet
- Une clé de licence valide [📀 Acheter une licence](https://qalita.io) ou [contactez-nous pour bénéficier d'une clé d'essai](mailto:contact@qalita.io)

:::info
La clé de licence permet de se connecter au docker registry et de pull les images docker, en plus d'ajouter des informations pour la plateforme.
:::

1. Se connecter au dépôt d'images docker :

```bash
docker login qalita.azurecr.io
```

2. Créez ces deux fichiers :

- docker-compose.yaml
- s3_config.json

1. Executer docker-compose :

```bash
docker-compose up -d
```
