#!/usr/bin/env python3
import os
import json
import click
import requests
import pandas as pd
from typing import List, Dict, Any
from dotenv import load_dotenv

try:
    from great_expectations.dataset import PandasDataset
except Exception:
    PandasDataset = None  # type: ignore


def build_expectations_from_suite_file(suite_path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(suite_path):
        return []
    with open(suite_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    return suite.get("expectations", []) if isinstance(suite, dict) else []


def run_expectations(df: pd.DataFrame, expectations: List[Dict[str, Any]]):
    if PandasDataset is None:
        raise RuntimeError("great_expectations PandasDataset API not available. Check your installation.")
    gx_ds = PandasDataset(df)
    results: List[Dict[str, Any]] = []
    total = 0
    passed = 0

    for exp in expectations:
        exp_type = exp.get("expectation_type")
        kwargs = exp.get("kwargs", {})
        if not exp_type or not hasattr(gx_ds, exp_type):
            continue
        try:
            res = getattr(gx_ds, exp_type)(**kwargs)
            success = bool(res.get("success", False))
        except Exception:
            success = False
            res = {"success": False, "exception": True}
        results.append({
            "expectation_type": exp_type,
            "kwargs": kwargs,
            "success": success,
        })
        total += 1
        passed += 1 if success else 0

    score = 1.0 if total == 0 else round(passed / total, 4)
    return results, score


def write_metrics_json(metrics: List[Dict[str, Any]], out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


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
@click.option("--suite", "suite_name", default="retail_suite", show_default=True, help="Expectation suite name")
@click.option("--data", "data_path", default="data/retail.csv", show_default=True, help="CSV data path")
@click.option("--suite-file", "suite_file", default="ge/expectations/retail_suite.json", show_default=True, help="Suite JSON file path")
@click.option("--dataset-name", default=os.getenv("DATASET_NAME", "retail"), show_default=True, help="Logical dataset name")
@click.option("--env", "dataset_env", default=os.getenv("DATASET_ENV", "dev"), show_default=True, help="Environment tag")
@click.option("--no-upload", is_flag=True, help="Do not upload metrics to QALITA")
def main(suite_name: str, data_path: str, suite_file: str, dataset_name: str, dataset_env: str, no_upload: bool):
    load_dotenv(override=False)

    if not os.path.isfile(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)

    expectations = build_expectations_from_suite_file(suite_file)
    if not expectations:
        # Fallback minimal expectations if suite file is missing/empty
        expectations = [
            {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "id"}},
            {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "date"}},
            {"expectation_type": "expect_column_values_to_be_between", "kwargs": {"column": "amount", "min_value": 0, "max_value": 10000, "allow_cross_type_comparisons": True}},
            {"expectation_type": "expect_column_values_to_match_regex", "kwargs": {"column": "currency", "regex": "^(EUR|USD|GBP)$"}},
            {"expectation_type": "expect_column_values_to_be_unique", "kwargs": {"column": "id"}},
        ]

    results, score = run_expectations(df, expectations)

    metrics: List[Dict[str, Any]] = []
    # Per-expectation results
    for r in results:
        metrics.append({
            "key": "expectation_result",
            "value": {"expectation": r.get("expectation_type"), "success": bool(r.get("success"))},
            "scope": {"perimeter": "dataset", "value": dataset_name, "env": dataset_env, "suite": suite_name},
        })
    # Aggregate score
    metrics.append({
        "key": "score",
        "value": str(score),
        "scope": {"perimeter": "dataset", "value": dataset_name, "env": dataset_env, "suite": suite_name},
    })

    os.makedirs("artifacts", exist_ok=True)
    metrics_path = os.path.join("artifacts", "metrics.json")
    write_metrics_json(metrics, metrics_path)
    click.echo(f"Metrics written to {metrics_path}")

    if not no_upload:
        upload_metrics(metrics_path)


if __name__ == "__main__":
    main()
\"EOF\"
