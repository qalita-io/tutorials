// QALITA Power Query Samples (M)
// Requires functions from QALITA.pq in the same PBIX or Dataflow

let
  // Parameters you should create in Power BI:
  // QALITA_Url (Text), QALITA_Username (Text), QALITA_Password (Text), QALITA_ApiToken (Text optional)

  // Helper to obtain a working token: prefer API token if provided
  QALITA_Token = let
    apiToken = try QALITA_ApiToken otherwise null,
    hasApiToken = apiToken <> null and apiToken <> "",
    token = if hasApiToken then apiToken else QALITA[QALITA_SignIn](QALITA_Url, QALITA_Username, QALITA_Password)
  in token,

  // Sample 1: Metrics for a given source_id and pack_id via v2
  QALITA_Sample_Metrics = (source_id as number, pack_id as number) as table =>
    let
      path = "/api/v2/metrics?source_id=" & Number.ToText(source_id) & "&pack_id=" & Number.ToText(pack_id),
      json = QALITA[QALITA_GetJson](QALITA_Url, path, QALITA_Token),
      table = QALITA[QALITA_TableFromJson](json)
    in
      table,

  // Sample 2: Monthly scores via v1 curated report endpoint
  QALITA_Sample_MonthlyScores = (report_id as number, source_id as number) as table =>
    let
      path = "/api/v1/reports/" & Number.ToText(report_id) & "/sources/" & Number.ToText(source_id) & "/monthly_scores",
      json = QALITA[QALITA_GetJson](QALITA_Url, path, QALITA_Token),
      // json is a list of records: [datetime, scores = record{dimensions}, source = record]
      tbl = Table.FromList(json, Splitter.SplitByNothing(), {"row"}),
      expanded = Table.ExpandRecordColumn(tbl, "row", {"datetime", "scores", "source"}, {"datetime", "scores", "source"}),
      // Expand scores (dimensions as columns)
      scoresExpanded = Table.ExpandRecordColumn(expanded, "scores", Record.FieldNames(expanded[scores]{0}), Record.FieldNames(expanded[scores]{0})),
      // Expand source minimal fields if present
      sourceCols = if Table.RowCount(scoresExpanded) > 0 then Record.FieldNames(scoresExpanded[source]{0}) else {},
      fullyExpanded = if List.Count(sourceCols) > 0 then Table.ExpandRecordColumn(scoresExpanded, "source", sourceCols, sourceCols) else scoresExpanded,
      // Ensure datetime type
      typed = Table.TransformColumnTypes(fullyExpanded, {{"datetime", type datetime}})
    in
      typed,

  // Sample 3: Issues (v2) – simple list
  QALITA_Sample_Issues = () as table =>
    let
      json = QALITA[QALITA_GetJson](QALITA_Url, "/api/v2/issues", QALITA_Token),
      table = QALITA[QALITA_TableFromJson](json)
    in
      table
in
  [
    QALITA_Sample_Metrics = QALITA_Sample_Metrics,
    QALITA_Sample_MonthlyScores = QALITA_Sample_MonthlyScores,
    QALITA_Sample_Issues = QALITA_Sample_Issues
  ]


