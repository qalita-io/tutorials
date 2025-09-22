connection: "your_looker_connection_name"

include: "/views/*.view.lkml"

explore: metrics {
  view_name: metrics
}

explore: issues {
  view_name: issues
}


