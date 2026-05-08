# AGENTS.md — Qalita Tutorials

Ce fichier fournit des instructions aux agents IA pour travailler sur ce dépôt.

## Projet

**Qalita Tutorials** — Collection de tutoriels, exemples de données et guides d'intégration pour la plateforme Qalita.

- **Organisation GitHub** : `qalita-io`
- **Documentation** : <https://doc.qalita.io/>

## Architecture

```
tutorials/
├── deploy/
│   └── docker-compose/    # Déploiement via Docker Compose
├── integrations/
│   ├── data-engineering/  # Intégrations ELT & orchestration
│   ├── data-quality/      # Intégrations frameworks data quality
│   └── platform/          # Intégrations plateforme (ticketing, alerting, reporting, catalogues)
└── source/                # Guides d'enregistrement de sources
```

## Conventions

- Chaque tutoriel est un dossier autonome avec son propre `README.md`
- Les exemples de données doivent être anonymisées (pas de données réelles)
- **Langue** : README en anglais pour la cohérence avec le reste du repo
- **Commits** : Messages en anglais, conventionnels (`feat:`, `fix:`, `docs:`)

## Règles

- ❌ Ne pas commiter de données sensibles ou confidentielles
- ✅ Vérifier que les liens vers la documentation sont valides
