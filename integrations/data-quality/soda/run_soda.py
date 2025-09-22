import argparse
import json
import os
from pathlib import Path

import pandas as pd
from soda.scan import Scan


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_recommendations(checks: list, dataset_label: str) -> list:
    recs = []
    total = len(checks)
    passed = sum(1 for c in checks if c.get("outcome") == "pass")
    score = passed / total if total > 0 else 0.0
    if score < 1.0:
        recs.append({
            "content": f"Dataset '{dataset_label}' passed {passed}/{total} checks ({round(score*100,2)}%).",
            "type": "Checks Summary",
            "scope": {"perimeter": "dataset", "value": dataset_label},
            "level": "medium" if score >= 0.8 else "high",
        })
    for c in checks:
        if c.get("outcome") != "pass":
            col = c.get("column")
            scope = {"perimeter": "dataset", "value": dataset_label}
            if col:
                scope = {
                    "perimeter": "column",
                    "value": col,
                    "parent_scope": {"perimeter": "dataset", "value": dataset_label},
                }
            recs.append({
                "content": c.get("definition") or c.get("name") or "Check failed",
                "type": c.get("name") or "Check Failed",
                "scope": scope,
                "level": "high",
            })
    return recs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Soda scan on a CSV and emit artifacts")
    parser.add_argument("--data", default="data/retail.csv", help="Path to CSV data file")
    parser.add_argument("--checks", default="checks/checks.yaml", help="Path to SodaCL checks file")
    parser.add_argument("--artifacts", default="artifacts", help="Directory to write artifacts")
    args = parser.parse_args()

    data_path = Path(args.data)
    checks_path = Path(args.checks)
    artifacts_dir = Path(args.artifacts)

    ensure_dir(artifacts_dir)

    df = pd.read_csv(data_path)
    dataset_label = data_path.stem

    scan = Scan()
    data_source_name = dataset_label
    scan.set_data_source_name(data_source_name)
    scan.add_pandas_dataframe(
        data_source_name=data_source_name,
        dataset_name=dataset_label,
        pandas_df=df,
    )
    scan.add_sodacl_yaml_files(str(checks_path))
    scan.execute()

    results = scan.get_scan_results()
    checks = results.get("checks", [])

    total_checks = len(checks)
    passed_checks = sum(1 for c in checks if c.get("outcome") == "pass")
    score = round(passed_checks / total_checks, 2) if total_checks > 0 else 0.0

    metrics = [
        {"key": "score", "value": score, "scope": {"perimeter": "dataset", "value": dataset_label}},
        {"key": "check_passed", "value": passed_checks, "scope": {"perimeter": "dataset", "value": dataset_label}},
        {"key": "check_failed", "value": total_checks - passed_checks, "scope": {"perimeter": "dataset", "value": dataset_label}},
    ]

    with open(artifacts_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    recommendations = build_recommendations(checks, dataset_label)
    with open(artifacts_dir / "recommendations.json", "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2)

    with open(artifacts_dir / "soda_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote artifacts to {artifacts_dir}")


if __name__ == "__main__":
    main()
