import os

from dagster import Definitions
from dotenv import load_dotenv

from .jobs.example_qalita_job import example_qalita_job
from .resources.qalita_resource import QalitaResource


# Load .env if present (for QALITA_* variables)
load_dotenv()


defs = Definitions(
    jobs=[example_qalita_job],
    resources={
        "qalita": QalitaResource(
            # Use environment variable defaults if not provided
            endpoint=os.environ.get("QALITA_AGENT_ENDPOINT"),
            token=os.environ.get("QALITA_AGENT_TOKEN"),
            agent_name=os.environ.get("QALITA_AGENT_NAME", "dagster-agent"),
            agent_mode=os.environ.get("QALITA_AGENT_MODE", "job"),
        )
    },
)


