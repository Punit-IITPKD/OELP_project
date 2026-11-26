"""Generate editable-vector diagrams and research-result figures for Phase 9.

This script reads only saved aggregate evaluation JSON. It never opens notebooks,
loads model files, or writes under data/, models/, or notebooks/.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "submission" / "assets"
DIAGRAMS = OUTPUT / "diagrams"
FIGURES = OUTPUT / "figures"
COLORS = {
    "ink": "#17324D",
    "teal": "#087E8B",
    "blue": "#4F82A3",
    "orange": "#D77936",
    "pale": "#EAF2F5",
    "pale_teal": "#E5F3F2",
    "pale_orange": "#FAEFE5",
    "muted": "#607486",
    "white": "#FFFFFF",
    "grid": "#D8E1E7",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titleweight": "bold",
        "axes.labelcolor": COLORS["ink"],
        "text.color": COLORS["ink"],
        "axes.edgecolor": COLORS["grid"],
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "figure.facecolor": COLORS["white"],
        "axes.facecolor": COLORS["white"],
    }
)


def finish(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight", dpi=220, facecolor="white")
    plt.close(fig)


def add_box(ax, x, y, w, h, label, fill=None, fontsize=9):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=1.25,
        edgecolor=COLORS["teal"],
        facecolor=fill or COLORS["pale"],
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=COLORS["ink"], wrap=True)
    return patch


def add_arrow(ax, start, end, color=None, lw=1.5, mutation=14):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=mutation,
            linewidth=lw,
            color=color or COLORS["teal"],
            connectionstyle="arc3,rad=0",
        )
    )


def flow_diagram(name, title, labels, subtitle=None, colors=None):
    cols = 6
    w, h = 1.85, 0.66
    gap = 0.34
    x0 = 0.25
    x_positions = [x0 + i * (w + gap) for i in range(cols)]
    y_positions = [1.55, 0.35]
    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 2.75)
    ax.axis("off")
    ax.text(0.25, 2.55, title, fontsize=17, fontweight="bold", color=COLORS["ink"])
    if subtitle:
        ax.text(0.25, 2.28, subtitle, fontsize=9.5, color=COLORS["muted"])

    for index, label in enumerate(labels):
        row = 0 if index < cols else 1
        in_row = index if row == 0 else index - cols
        column = in_row if row == 0 else cols - 1 - in_row
        fill = (colors or {}).get(index, COLORS["pale"])
        add_box(ax, x_positions[column], y_positions[row], w, h, label, fill=fill, fontsize=8.7)

    for index in range(cols - 1):
        add_arrow(
            ax,
            (x_positions[index] + w + 0.015, y_positions[0] + h / 2),
            (x_positions[index + 1] - 0.015, y_positions[0] + h / 2),
        )
    # Serpentine continuation into the second row, then back toward the left.
    add_arrow(
        ax,
        (x_positions[-1] + w / 2, y_positions[0] - 0.03),
        (x_positions[-1] + w / 2, y_positions[1] + h + 0.03),
        color=COLORS["orange"],
    )
    for index in range(cols - 1):
        right_col = cols - 1 - index
        left_col = right_col - 1
        add_arrow(
            ax,
            (x_positions[right_col] - 0.015, y_positions[1] + h / 2),
            (x_positions[left_col] + w + 0.015, y_positions[1] + h / 2),
        )
    finish(fig, DIAGRAMS / name)


def linear_diagram(name, title, labels, subtitle=None):
    count = len(labels)
    w, h, gap = 2.55, 0.95, 0.65
    total = count * w + (count - 1) * gap
    fig, ax = plt.subplots(figsize=(max(9, total * 1.06), 3.1))
    ax.set_xlim(0, total + 0.3)
    ax.set_ylim(0, 2.5)
    ax.axis("off")
    ax.text(0, 2.23, title, fontsize=17, fontweight="bold", color=COLORS["ink"])
    if subtitle:
        ax.text(0, 1.92, subtitle, fontsize=9.5, color=COLORS["muted"])
    for i, label in enumerate(labels):
        x = i * (w + gap)
        fill = [COLORS["pale"], COLORS["pale_teal"], COLORS["pale_orange"]][i % 3]
        add_box(ax, x, 0.63, w, h, label, fill=fill, fontsize=10)
        if i < count - 1:
            add_arrow(ax, (x + w + 0.02, 1.1), (x + w + gap - 0.02, 1.1))
    finish(fig, DIAGRAMS / name)


def temporal_diagram(name):
    rows = [
        ("30-day", "2010-06-01", "2010-08-01", "2010-09-10", "2010-10-10"),
        ("60-day", "2010-05-01", "2010-07-01", "2010-09-10", "2010-11-09"),
        ("90-day", "2010-03-01", "2010-06-01", "2010-09-10", "2010-12-09"),
    ]
    fig, ax = plt.subplots(figsize=(12, 4.4))
    ax.set_title("Chronological evaluation with matured outcome windows", loc="left",
                 fontsize=16, color=COLORS["ink"], pad=16)
    ax.set_xlim(-0.4, 12.6)
    ax.set_ylim(-0.7, 3.25)
    ax.set_yticks([2.5, 1.5, 0.5], [r[0] for r in rows])
    ax.set_xticks([0, 2.5, 5, 7.5, 10, 12], ["Mar", "May", "Jul", "Sep", "Nov", "Dec 2010"])
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["grid"])
    origin = 2010 * 12

    def month_position(date):
        year, month, _ = map(int, date.split("-"))
        return year * 12 + month - origin

    for y, row in zip([2.5, 1.5, 0.5], rows):
        _, train, val, test, end = row
        points = [(train, COLORS["blue"], "TRAIN"), (val, COLORS["teal"], "VAL"), (test, COLORS["orange"], "TEST")]
        ax.plot([month_position(train), month_position(end)], [y, y], color="#C9D5DC", linewidth=3, zorder=1)
        for date, color, label in points:
            x = month_position(date)
            ax.scatter([x], [y], s=92, color=color, edgecolor="white", linewidth=1, zorder=3)
            ax.text(x, y + 0.22, f"{label}\n{date}", ha="center", va="bottom",
                    fontsize=7.6, color=COLORS["ink"])
        xend = month_position(end)
        ax.scatter([xend], [y], s=55, marker="|", color=COLORS["muted"], zorder=3)
        ax.text(xend, y - 0.28, f"outcome ends {end}", ha="center", va="top",
                fontsize=7.5, color=COLORS["muted"])
    ax.text(0, -0.55, "Each horizon uses its own outcome-matured TRAIN/VAL cutoffs; the locked TEST cutoff is 2010-09-10.",
            fontsize=8.7, color=COLORS["muted"])
    finish(fig, DIAGRAMS / name)


def result_charts():
    metrics = json.loads((ROOT / "data/metrics/final_project_evaluation.json").read_text())
    pc = [r for r in metrics["purchase_clock_evaluation"]["test_metrics"] if r["model"] == "Personalized"]
    horizons = [r["horizon_days"] for r in pc]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
    specs = [
        ("roc_auc", "ROC-AUC", 0.5, 1.0),
        ("average_precision", "Average precision", 0.0, 1.0),
        ("brier_score", "Brier score (lower is better)", 0.0, 0.35),
    ]
    for ax, (key, title, ymin, ymax) in zip(axes, specs):
        values = [r[key] for r in pc]
        ax.plot(horizons, values, marker="o", color=COLORS["teal"], linewidth=2.4, markersize=7)
        ax.set_title(title, fontsize=10, color=COLORS["ink"])
        ax.set_xticks(horizons, [f"{h}d" for h in horizons])
        ax.set_ylim(ymin, ymax)
        ax.grid(axis="y", color=COLORS["grid"])
        ax.spines[["top", "right"]].set_visible(False)
        for h, v in zip(horizons, values):
            ax.annotate(f"{v:.3f}", (h, v), xytext=(0, 9), textcoords="offset points",
                        ha="center", fontsize=8, color=COLORS["ink"])
    fig.suptitle("Personalized Purchase Clock — locked TEST cohort (n=3,373 per horizon)",
                 x=0.04, ha="left", fontsize=14, fontweight="bold", color=COLORS["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    finish(fig, FIGURES / "purchase_clock_test_metrics")

    spend = [r for r in metrics["spending_forecast_evaluation"]["test_metrics"]
             if r["model"] == "Personalized two-stage"]
    hs = [r["horizon_days"] for r in spend]
    fig, axes = plt.subplots(1, 2, figsize=(10.7, 4.0))
    axes[0].bar([str(h) for h in hs], [r["mae"] for r in spend], color=COLORS["blue"], width=0.55)
    axes[0].set_title("MAE (£), lower is better", color=COLORS["ink"])
    axes[1].bar([str(h) for h in hs], [r["mean_forecast_bias"] for r in spend],
                color=[COLORS["teal"] if r["mean_forecast_bias"] >= 0 else COLORS["orange"] for r in spend],
                width=0.55)
    axes[1].axhline(0, color=COLORS["muted"], linewidth=0.9)
    axes[1].set_title("Mean forecast bias (£)", color=COLORS["ink"])
    for ax in axes:
        ax.set_xlabel("Forecast horizon (days)")
        ax.grid(axis="y", color=COLORS["grid"])
        ax.spines[["top", "right"]].set_visible(False)
    for h, r in zip(hs, spend):
        axes[0].text(str(h), r["mae"] + max(x["mae"] for x in spend) * 0.025,
                     f'{r["mae"]:.0f}', ha="center", fontsize=8)
        axes[1].text(str(h), r["mean_forecast_bias"] + (35 if r["mean_forecast_bias"] >= 0 else -55),
                     f'{r["mean_forecast_bias"]:.0f}', ha="center", fontsize=8)
    fig.suptitle("Personalized two-stage spending forecasts — locked TEST cohort (n=3,373)",
                 x=0.04, ha="left", fontsize=14, fontweight="bold", color=COLORS["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    finish(fig, FIGURES / "spending_forecast_test_metrics")

    t = metrics["trajectory_evaluation"]
    reg11 = next(r for r in metrics["notebook_registry"] if r["notebook_id"] == "11")
    counts = reg11["evaluation_population_counts"]
    count_values = [
        counts["summary_trajectory_eligible_by_horizon_and_role"]["30d_test_summary"],
        counts["shape_cluster_eligible_by_role"]["TEST"],
        counts["functional_curve_test"] if "functional_curve_test" in counts else 659,
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), gridspec_kw={"width_ratios": [1.5, 1]})
    labels = ["Summary\ntrajectory", "Shape\nclusters", "Functional\ncurves"]
    axes[0].bar(labels, count_values, color=[COLORS["blue"], COLORS["teal"], COLORS["orange"]], width=0.58)
    axes[0].set_title("Method-specific TEST support", color=COLORS["ink"])
    axes[0].set_ylim(0, max(count_values) * 1.18)
    axes[0].grid(axis="y", color=COLORS["grid"])
    axes[0].spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(count_values):
        axes[0].text(i, v + max(count_values) * 0.025, f"{v:,}", ha="center", fontsize=9)
    axes[1].axis("off")
    axes[1].text(0.04, 0.8, "Functional PCA", fontsize=12, fontweight="bold", color=COLORS["ink"])
    axes[1].text(0.04, 0.58, "98.82%", fontsize=23, fontweight="bold", color=COLORS["teal"])
    axes[1].text(0.04, 0.44, "TRAIN-fitted explained variance", fontsize=9, color=COLORS["muted"])
    axes[1].text(0.04, 0.24, "0.006248", fontsize=20, fontweight="bold", color=COLORS["orange"])
    axes[1].text(0.04, 0.1, "TEST reconstruction RMSE", fontsize=9, color=COLORS["muted"])
    fig.suptitle("Notebook 11 — descriptive trajectory support and functional reconstruction",
                 x=0.04, ha="left", fontsize=14, fontweight="bold", color=COLORS["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    finish(fig, FIGURES / "trajectory_test_support_and_fda")


def main():
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    flow_diagram(
        "research_pipeline",
        "Research pipeline: transactions to decision-support dashboard",
        [
            "Historical\ntransactions", "Cleaning and\nquality checks", "Customer\nfeatures",
            "RFM and\nsegmentation", "Temporal\nvalidation", "Purchase\nprobability",
            "Conditional\nspending", "Behaviour and\nreliability", "Trajectory\nanalysis",
            "Saved models\nand metrics", "FastAPI\n(read-only/inference)", "React\nresearch UI",
        ],
        subtitle="Offline notebooks create validated outputs; the application serves saved artifacts and does not run training notebooks.",
        colors={0: COLORS["pale_blue"] if "pale_blue" in COLORS else COLORS["pale"],
                9: COLORS["pale_orange"], 10: COLORS["pale_teal"], 11: COLORS["pale_teal"]},
    )
    linear_diagram(
        "purchase_clock_architecture",
        "Personalized Purchase Clock",
        [
            "Historical customer activity\nbefore forecast cutoff",
            "Timing and customer-history\nfeatures",
            "Saved discrete-time\nhazard model",
            "Cumulative purchase probability\nfor 30, 60, and 90 days",
        ],
        "The service loads a saved model; inference does not fit or update it.",
    )
    linear_diagram(
        "expected_revenue_calculation",
        "Two-stage expected revenue",
        [
            "P(at least one purchase within H days)",
            "×  E(spending within H days | purchase)",
            "=  Expected future revenue (£)",
        ],
        "An expected value is not a realized amount, a recoverable loss, or a causal campaign effect.",
    )
    temporal_diagram("temporal_evaluation")
    linear_diagram(
        "application_architecture",
        "Application architecture",
        [
            "React pages\nand React Query",
            "Generated typed\nOpenAPI client",
            "FastAPI routes\nand validation",
            "Saved metrics, models,\nand serving snapshots",
        ],
        "Read-only research summary and frozen-model inference are separate from offline research.",
    )
    flow_diagram(
        "customer_intelligence_workflow",
        "Customer Intelligence workflow",
        [
            "Select saved\ncustomer", "Inspect history\nbefore cutoff", "Review purchase\nprobabilities",
            "Review expected\nspending", "Inspect model\nsensitivities", "Check cohort\nreliability",
            "Review behaviour\nindicators", "Explore trajectory\nsupport", "Open source\nmethodology",
            "Interpret results\nwith caveats", "Consider only a\nhypothetical plan", "Record limits;\nno causal claim",
        ],
        subtitle="Example walkthrough uses customer 18102; historical TEST outcomes are not revealed in the live demonstration.",
        colors={0: COLORS["pale_teal"], 9: COLORS["pale_orange"], 10: COLORS["pale_orange"], 11: COLORS["pale"]},
    )
    result_charts()
    print(f"Generated 6 diagrams and 3 result figures under {OUTPUT}")


if __name__ == "__main__":
    main()
