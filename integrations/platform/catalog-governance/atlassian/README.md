## Integration: Atlassian (Confluence/Jira Assets) ↔ QALITA (Beta)

Goal: surface QALITA quality summaries in Atlassian tools for governance and documentation.

High-level flow:

1. QALITA exposes summaries (scores, recent issues) per dataset/source.
2. Confluence macros or Jira Assets ingest and display the data.
3. Links route back to QALITA for details.

Backend touchpoints:

- `app-backend` read APIs for summaries; potential Confluence app endpoint.

Implementation options:

- Confluence macro fetching JSON from QALITA
- Jira Assets import job via REST

Docs references:

- Integrations: https://doc.qalita.io/docs/platform/user-guides/admin/integrations

Next steps:

- Provide example Confluence macro
- Define field mapping for Jira Assets
- Authentication and caching guidance


