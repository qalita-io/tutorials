(function () {
  function normalizeBaseUrl(url) {
    if (!url) return "";
    return url.replace(/\/$/, "");
  }

  function buildHeaders(token) {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  function toMetricsRows(items) {
    return (items || []).map((m) => ({
      id: m.id ?? null,
      created_at: m.created_at ?? null,
      source_id: m.source_id ?? null,
      source_version_id: m.source_version_id ?? null,
      pack_id: m.pack_id ?? null,
      pack_version_id: m.pack_version_id ?? null,
      key: m.key ?? null,
      value: m.value ?? null,
      scope: m.scope ? JSON.stringify(m.scope) : null,
    }));
  }

  function toIssuesRows(items) {
    return (items || []).map((i) => ({
      id: i.id ?? null,
      created_at: i.created_at ?? null,
      updated_at: i.updated_at ?? null,
      title: i.title ?? null,
      description: i.description ?? null,
      status: i.status ?? null,
      source_id: i.source_id ?? (i.source && i.source.id) ?? null,
      assignee: i.assignee ?? (i.assignee_user && i.assignee_user.id) ?? null,
      due_date: i.due_date ?? null,
      url: i.url ?? null,
      chat_url: i.chat_url ?? null,
      closed_at: i.closed_at ?? null,
    }));
  }

  const connector = tableau.makeConnector();

  connector.getSchema = function (schemaCallback) {
    try {
      const cfg = JSON.parse(tableau.connectionData || "{}");

      const tables = [];

      if (cfg.tableMetrics) {
        tables.push({
          id: "metrics",
          alias: "QALITA Metrics",
          columns: [
            { id: "id", dataType: tableau.dataTypeEnum.int },
            { id: "created_at", dataType: tableau.dataTypeEnum.datetime },
            { id: "source_id", dataType: tableau.dataTypeEnum.int },
            { id: "source_version_id", dataType: tableau.dataTypeEnum.int },
            { id: "pack_id", dataType: tableau.dataTypeEnum.int },
            { id: "pack_version_id", dataType: tableau.dataTypeEnum.int },
            { id: "key", dataType: tableau.dataTypeEnum.string },
            { id: "value", dataType: tableau.dataTypeEnum.string },
            { id: "scope", dataType: tableau.dataTypeEnum.string },
          ],
        });
      }

      if (cfg.tableIssues) {
        tables.push({
          id: "issues",
          alias: "QALITA Issues",
          columns: [
            { id: "id", dataType: tableau.dataTypeEnum.int },
            { id: "created_at", dataType: tableau.dataTypeEnum.datetime },
            { id: "updated_at", dataType: tableau.dataTypeEnum.datetime },
            { id: "title", dataType: tableau.dataTypeEnum.string },
            { id: "description", dataType: tableau.dataTypeEnum.string },
            { id: "status", dataType: tableau.dataTypeEnum.string },
            { id: "source_id", dataType: tableau.dataTypeEnum.int },
            { id: "assignee", dataType: tableau.dataTypeEnum.int },
            { id: "due_date", dataType: tableau.dataTypeEnum.datetime },
            { id: "url", dataType: tableau.dataTypeEnum.string },
            { id: "chat_url", dataType: tableau.dataTypeEnum.string },
            { id: "closed_at", dataType: tableau.dataTypeEnum.datetime },
          ],
        });
      }

      if (!tables.length) {
        tableau.abortWithError("No tables selected in connector form.");
        return;
      }

      schemaCallback(tables);
    } catch (e) {
      tableau.abortWithError(`Schema error: ${e?.message || e}`);
    }
  };

  connector.getData = function (table, doneCallback) {
    const cfg = JSON.parse(tableau.connectionData || "{}");
    const baseUrl = normalizeBaseUrl(cfg.baseUrl || "http://localhost:8000/api/v1");
    const headers = buildHeaders(cfg.token);

    async function fetchJson(url) {
      const res = await fetch(url, { headers });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status} — ${text}`);
      }
      return res.json();
    }

    (async function () {
      try {
        if (table.tableInfo.id === "metrics") {
          const { reportId, sourceId, packId } = cfg;
          if (!reportId || !sourceId || !packId) {
            throw new Error("Metrics require reportId, sourceId, and packId.");
          }
          const url = `${baseUrl}/reports/${encodeURIComponent(reportId)}/metrics?source_id=${encodeURIComponent(sourceId)}&pack_id=${encodeURIComponent(packId)}`;
          const items = await fetchJson(url);
          table.appendRows(toMetricsRows(items));
        } else if (table.tableInfo.id === "issues") {
          const { projectId } = cfg;
          if (!projectId) {
            throw new Error("Issues require projectId.");
          }
          const url = `${baseUrl}/projects/${encodeURIComponent(projectId)}/issues`;
          const items = await fetchJson(url);
          table.appendRows(toIssuesRows(items));
        }
        doneCallback();
      } catch (e) {
        tableau.abortWithError(`Data error: ${e?.message || e}`);
      }
    })();
  };

  document.addEventListener("DOMContentLoaded", function () {
    tableau.registerConnector(connector);
  });
})();


