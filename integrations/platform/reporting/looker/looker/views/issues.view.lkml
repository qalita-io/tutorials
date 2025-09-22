view: issues {
  sql_table_name: qalita_issues ;;

  primary_key: id

  dimension: id { type: number; primary_key: yes; }
  dimension_group: created_at { type: time; timeframes: [raw, date, week, month, quarter, year]; sql: ${TABLE}.created_at ; }
  dimension_group: updated_at { type: time; timeframes: [raw, date, week, month, quarter, year]; sql: ${TABLE}.updated_at ; }

  dimension: partner_id { type: number }
  dimension: title { type: string }
  dimension: description { type: string }
  dimension: status { type: string }
  dimension: url { type: string }
  dimension: chat_url { type: string }
  dimension: source_id { type: number }
  dimension: assignee { type: number }
  dimension: due_date { type: time }
  dimension: author_id { type: number }
  dimension: closed_at { type: time }

  measure: count { type: count }

  dimension: scope_perimeter { type: string sql: ${TABLE}.scope->>'perimeter' ;; }

  parameter: qalita_base_url { type: unquoted allowed_value: { value: "https://your-qalita.example.com" } }
  dimension: issue_url_html {
    type: string
    html: "<a href='${url}' target='_blank'>Open Issue</a>"
  }
  dimension: source_url_html {
    type: string
    html: "<a href='${qalita_base_url}/home/data-engineering/sources/${source_id}' target='_blank'>Open Source</a>"
  }
}


