from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

from _lib.qalita_operator import QalitaOperator


with DAG(
    dag_id="qalita_example_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["qalita", "tutorial"],
) as dag:
    extract = BashOperator(
        task_id="extract",
        bash_command="echo 'Extracting source data...'",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command="echo 'Transforming data into staging...'",
    )

    # Smoke test: show CLI version via Python package
    qalita_cli_version = QalitaOperator(
        task_id="qalita_cli_version",
        command=["version"],
    )

    # Prepare agent context and verify connectivity
    qalita_agent_login = QalitaOperator(
        task_id="qalita_agent_login",
        command=["agent", "login"],
        env={
            "QALITA_AGENT_NAME": "airflow-agent",
            "QALITA_AGENT_MODE": "job",
            # Expected to be set via Airflow connections/variables or .env
            # QALITA_AGENT_TOKEN, QALITA_AGENT_ENDPOINT
        },
    )

    # Example agent job run using documented flags
    # Requires valid IDs; replace with your own or parameterize via Variables
    qalita_agent_run = QalitaOperator(
        task_id="qalita_agent_run",
        command=[
            "agent",
            "run",
            "-s",
            "{{ var.json.qalita_params.source_id | default('1') }}",
            "-p",
            "{{ var.json.qalita_params.pack_id | default('1') }}",
        ],
        env={
            "QALITA_AGENT_MODE": "job",
        },
    )

    # Helper commands (optional) to explore configured entities
    qalita_source_list = QalitaOperator(
        task_id="qalita_source_list",
        command=["source", "list"],
    )
    qalita_pack_list = QalitaOperator(
        task_id="qalita_pack_list",
        command=["pack", "list"],
    )

    extract >> transform >> qalita_cli_version >> qalita_agent_login
    qalita_agent_login >> [qalita_source_list, qalita_pack_list] >> qalita_agent_run


