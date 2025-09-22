view: metrics {
  sql_table_name: qalita_metrics ;;

  primary_key: id

  dimension: id { type: number; primary_key: yes; }
  dimension_group: created_at { type: time; timeframes: [raw, date, week, month, quarter, year]; sql: ${TABLE}.created_at ; }
  dimension_group: updated_at { type: time; timeframes: [raw, date, week, month, quarter, year]; sql: ${TABLE}.updated_at ; }

  dimension: partner_id { type: number }
  dimension: source_id { type: number }
  dimension: source_version_id { type: number }
  dimension: pack_id { type: number }
  dimension: pack_version_id { type: number }
  dimension: key { type: string }
  dimension: value_raw { type: string sql: ${TABLE}.value ;; }

  measure: value_numeric_avg { type: average sql: nullif(${TABLE}.value, '')::numeric ;; value_format_name: decimal_2 }
  measure: value_numeric_max { type: max sql: nullif(${TABLE}.value, '')::numeric ;; }
  measure: value_numeric_min { type: min sql: nullif(${TABLE}.value, '')::numeric ;; }
  measure: count { type: count }

  # Optional: perimeter extracted from scope JSON
  dimension: scope_perimeter { type: string sql: ${TABLE}.scope->>'perimeter' ;; }

  # Backlink to QALITA (set base URL via a Looker parameter or hardcode)
  parameter: qalita_base_url { type: unquoted allowed_value: { value: "https://your-qalita.example.com" } }
  dimension: source_url {
    type: string
    html: "<a href='${qalita_base_url}/home/data-engineering/sources/${source_id}' target='_blank'>Open Source</a>"
  }
}


