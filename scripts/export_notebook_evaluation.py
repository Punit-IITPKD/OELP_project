from __future__ import annotations

import argparse
import base64
import json
import math
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class _FirstTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._in_table = False
        self._row: list[str] = []
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table" and not self._in_table:
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._row = []
        elif self._in_table and tag in {"th", "td"}:
            self._cell = []
        elif self._in_table and tag == "br" and self._cell is not None:
            self._cell.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_table and self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._in_table and tag in {"th", "td"} and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif self._in_table and tag == "tr" and self._row:
            self.rows.append(self._row)
        elif tag == "table" and self._in_table:
            self._in_table = False


def _find_cell(notebook: dict[str, Any], source_marker: str) -> dict[str, Any]:
    matches = [
        cell
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
        and source_marker in "".join(cell.get("source", []))
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one notebook cell containing {source_marker!r}; found {len(matches)}."
        )
    return matches[0]


def _display_table(cell: dict[str, Any], output_index: int) -> list[dict[str, Any]]:
    outputs = cell.get("outputs", [])
    if output_index >= len(outputs):
        raise ValueError("Expected executed notebook table output is missing.")
    data = outputs[output_index].get("data", {})
    html = data.get("text/html")
    if html is None:
        raise ValueError("Expected notebook HTML table output is missing.")
    parser = _FirstTableParser()
    parser.feed("".join(html) if isinstance(html, list) else html)
    if len(parser.rows) < 2:
        raise ValueError("Notebook output did not contain a populated table.")
    raw_header = parser.rows[0]
    has_index = bool(raw_header and not raw_header[0])
    header = raw_header[1:] if has_index else raw_header
    records = []
    for row in parser.rows[1:]:
        if has_index:
            row = row[1:]
        if len(row) != len(header):
            raise ValueError("Notebook table output has inconsistent row widths.")
        records.append(dict(zip(header, (_parse_value(value) for value in row))))
    return records


def _parse_value(value: str) -> Any:
    text = value.strip()
    if not text or text.lower() in {"nan", "none", "nat"}:
        return None
    try:
        number = float(text.replace(",", ""))
    except ValueError:
        return text
    if not math.isfinite(number):
        return None
    if number.is_integer() and not any(marker in text.lower() for marker in (".", "e")):
        return int(number)
    return number


def _write_notebook_image(
    cell: dict[str, Any], output_index: int, destination: Path
) -> None:
    outputs = cell.get("outputs", [])
    if output_index >= len(outputs):
        raise ValueError("Expected notebook calibration image is missing.")
    encoded = outputs[output_index].get("data", {}).get("image/png")
    if not encoded:
        raise ValueError("Expected notebook calibration PNG output is missing.")
    if isinstance(encoded, list):
        encoded = "".join(encoded)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(encoded))


def export_notebook_evaluation(
    root: Path = ROOT,
    *,
    output_path: Path | None = None,
    assets_dir: Path | None = None,
) -> dict[str, Any]:
    """Extract saved TEST metrics and calibration figures without executing notebooks."""
    purchase_path = root / "notebooks" / "06_Personalized_Purchase_Clock.ipynb"
    revenue_path = root / "notebooks" / "07_Future_Spending_and_Revenue_Forecasting.ipynb"
    purchase_nb = json.loads(purchase_path.read_text(encoding="utf-8"))
    revenue_nb = json.loads(revenue_path.read_text(encoding="utf-8"))

    purchase_metrics = _display_table(
        _find_cell(purchase_nb, "test_metrics, test_calibration = pc.evaluate_purchase_probabilities"),
        0,
    )
    history_metrics = _display_table(
        _find_cell(purchase_nb, "history_metrics = pc.performance_by_history_group"),
        0,
    )
    revenue_metrics = _display_table(
        _find_cell(revenue_nb, "test_metrics, test_joined = score_expected_forecasts"),
        2,
    )
    revenue_groups = _display_table(
        _find_cell(revenue_nb, "performance_by_group = pd.DataFrame(group_rows)"),
        1,
    )

    horizons = {30, 60, 90}
    if {int(row["horizon_days"]) for row in purchase_metrics} != horizons:
        raise ValueError("Purchase metrics do not contain all expected TEST horizons.")
    if any(int(row["n_customers"]) != 3373 for row in purchase_metrics):
        raise ValueError("Purchase metrics do not match the verified TEST cohort.")
    if {int(row["horizon_days"]) for row in revenue_metrics} != horizons:
        raise ValueError("Revenue metrics do not contain all expected TEST horizons.")
    if any(row.get("split_role") != "TEST" for row in revenue_metrics):
        raise ValueError("Revenue metrics include a non-TEST split.")

    metrics = {
        "source": {
            "generated_from": "saved executed outputs; notebooks were not rerun",
            "purchase_clock": {
                "notebook": purchase_path.relative_to(root).as_posix(),
                "cutoff_date": "2010-09-10",
                "split": "TEST",
                "customer_count": 3373,
            },
            "spending_forecast": {
                "notebook": revenue_path.relative_to(root).as_posix(),
                "cutoff_date": "2010-09-10",
                "split": "TEST",
                "customer_count": 3373,
            },
        },
        "purchase_clock": {
            "test_metrics": purchase_metrics,
            "history_group_metrics": history_metrics,
        },
        "spending_forecast": {
            "test_metrics": revenue_metrics,
            "group_metrics": revenue_groups,
        },
    }

    calibration_cell = _find_cell(purchase_nb, "90-day TEST reliability diagram")
    metrics_dir = assets_dir or root / "data" / "metrics"
    _write_notebook_image(
        calibration_cell,
        0,
        metrics_dir / "purchase_clock_test_calibration.png",
    )
    _write_notebook_image(
        calibration_cell,
        1,
        metrics_dir / "purchase_clock_test_calibration_90d.png",
    )

    destination = output_path or metrics_dir / "notebook_evaluation_summary.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(metrics, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export verified metrics from saved Notebook 06/07 outputs."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON destination (default: data/metrics/notebook_evaluation_summary.json).",
    )
    args = parser.parse_args()
    summary = export_notebook_evaluation(output_path=args.output)
    print(
        "Exported saved TEST metrics for "
        f"{summary['source']['purchase_clock']['customer_count']:,} customers."
    )


if __name__ == "__main__":
    main()
