#!/usr/bin/env python3
import os
import json
import click
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv


def ge_results_to_metrics(ge_json: Dict[str, Any], dataset_name: str, dataset_env: str):
    results = ge_json.get("results") or ge_json.get("statistics", {}).get("evaluations") or []
    metrics: List[Dict[str, Any]] = []
    total = 0
    passed = 0

    if isinstance(results, list):
        for item in results:
            # Great Expectations v0.x typical shape
            exp_cfg = item.get("expectation_config", {}) if isinstance(item, dict) else {}
            exp_type = exp_cfg.get("expectation_type")
            success = bool(item.get("success", False)) if isinstance(item, dict) else False
            if exp_type:
                metrics.append({
                    "key": "expectation_result",
                    "value": {"expectation": exp_type, "success": success},
                    "scope": {"perimeter": "dataset", "value": dataset_name, "env": dataset_env},
                })
                total += 1
                passed += 1 if success else 0
    # Compute score
    score = 1.0 if total == 0 else round(passed / total, 4)
    metrics.append({
        "key": "score",
        "value": str(score),
        "scope": {"perimeter": "dataset", "value": dataset_name, "env": dataset_env},
    })
    return metrics


def upload_metrics(metrics_path: str) -> None:
    endpoint = os.getenv("QALITA_AGENT_ENDPOINT")
    token = os.getenv("QALITA_AGENT_TOKEN")
    source_id = os.getenv("QALITA_SOURCE_ID")
    if not endpoint or not token:
        click.echo("QALITA_AGENT_ENDPOINT and QALITA_AGENT_TOKEN are required to upload. Skipping upload.")
        return
    url = endpoint.rstrip("/") + "/api/v1/metrics/upload"
    params = {}
    if source_id:
        params["source_id"] = source_id
    verify = not bool(os.getenv("SKIP_SSL_VERIFY", ""))
    with open(metrics_path, "rb") as f:
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files={"file": f}, params=params, timeout=60, verify=verify)
    if r.status_code == 200:
        click.echo("Uploaded metrics to QALITA.")
    else:
        click.echo(f"Failed to upload metrics: {r.status_code} - {r.text}")


@click.command()
@click.option("--file", "ge_file", required=True, help="Path to Great Expectations validation JSON")
@click.option("--dataset-name", default=os.getenv("DATASET_NAME", "retail"), show_default=True)
@click.option("--env", "dataset_env", default=os.getenv("DATASET_ENV", "dev"), show_default=True)
@click.option("--no-upload", is_flag=True, help="Do not upload metrics to QALITA")
def main(ge_file: str, dataset_name: str, dataset_env: str, no_upload: bool):
    load_dotenv(override=False)
    if not os.path.isfile(ge_file):
        raise FileNotFoundError(f"GE JSON file not found: {ge_file}")
    with open(ge_file, "r", encoding="utf-8") as f:
        ge_json = json.load(f)
    metrics = ge_results_to_metrics(ge_json, dataset_name, dataset_env)
    os.makedirs("artifacts", exist_ok=True)
    metrics_path = os.path.join("artifacts", "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    click.echo(f"Metrics written to {metrics_path}")
    if not no_upload:
        upload_metrics(metrics_path)


if __name__ == "__main__":
    main()
\"EOF\"
