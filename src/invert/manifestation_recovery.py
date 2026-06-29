from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


DATASET_FIELDS = [
    "generator_model",
    "task_id",
    "dimension",
    "rep",
    "text_distance",
    "ast_similarity",
    "ast_distance",
    "import_jaccard",
    "function_jaccard",
    "manifestation_score",
    "recovery_correct",
    "recovery_confidence",
    "keyword_prediction",
    "keyword_correct",
    "structural_fingerprint_score",
    "lock_gain",
    "input_validation_gain",
    "engineer_guessable",
    "manifestation_recovery_gap",
    "taxonomy_category",
]

# Thresholds (documented in manifestation_recovery_report.md)
MANIFESTATION_HIGH_THRESHOLD = 0.10
RECOVERY_HIGH_THRESHOLD = 0.5


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _float_or_empty(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _manifestation_score(
    text_distance: float,
    ast_distance: float | None,
    import_jaccard: float,
    function_jaccard: float,
) -> float:
    parts = [
        text_distance,
        1.0 - import_jaccard,
        1.0 - function_jaccard,
    ]
    if ast_distance is not None:
        parts.append(ast_distance)
    return _mean(parts)


def _pair_gain(v1: bool, v0: bool) -> float:
    return 1.0 if v1 and not v0 else 0.0


def _load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return float("nan")
    mx, my = _mean(x), _mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
    den_y = math.sqrt(sum((b - my) ** 2 for b in y))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda t: t[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _spearman(x: list[float], y: list[float]) -> float:
    if len(x) < 2:
        return float("nan")
    return _pearson(_rank(x), _rank(y))


def _taxonomy(manifestation_score: float, recovery_correct: float) -> str:
    high_m = manifestation_score >= MANIFESTATION_HIGH_THRESHOLD
    high_r = recovery_correct >= RECOVERY_HIGH_THRESHOLD
    if high_m and high_r:
        return "A"
    if high_m and not high_r:
        return "B"
    if not high_m and high_r:
        return "C"
    return "D"


def _category_label(code: str) -> str:
    labels = {
        "A": "High manifestation / High recovery",
        "B": "High manifestation / Low recovery",
        "C": "Low manifestation / High recovery",
        "D": "Low manifestation / Low recovery",
    }
    return labels.get(code, code)


def _build_dataset(run_dir: Path) -> list[dict[str, Any]]:
    manifest_rows = _load_csv(run_dir / "manifestation.csv")
    recovery_rows = _load_csv(run_dir / "recovery.csv")
    keyword_rows = _load_csv(run_dir / "keyword_baseline.csv")
    leakage_rows = _load_csv(run_dir / "proxy_leakage_report.csv")

    recovery_lookup: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in recovery_rows:
        key = (
            row["generator_model"],
            row["task_id"],
            row["manipulated_dimension"],
            row["true_value"],
            row["rep"],
        )
        recovery_lookup[key] = row

    keyword_lookup: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in keyword_rows:
        key = (
            row["generator_model"],
            row["task_id"],
            row["dimension"],
            row["true_value"],
            row["rep"],
        )
        keyword_lookup[key] = row

    leakage_lookup: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in leakage_rows:
        key = (
            row["generator_model"],
            row["task_id"],
            row["dimension"],
            row["value"],
            row["rep"],
        )
        leakage_lookup[key] = row

    dataset: list[dict[str, Any]] = []
    for m in manifest_rows:
        model = m["generator_model"]
        task_id = m["task_id"]
        dimension = m["dimension"]
        rep = m["rep"]

        text_distance = float(m["text_distance"])
        ast_similarity = _float_or_empty(m["ast_similarity"])
        ast_distance = (1.0 - ast_similarity) if ast_similarity is not None else None
        import_jaccard = float(m["import_jaccard"])
        function_jaccard = float(m["function_name_jaccard"])

        manif_score = _manifestation_score(
            text_distance, ast_distance, import_jaccard, function_jaccard
        )

        rec_v0 = recovery_lookup.get((model, task_id, dimension, "v0", rep))
        rec_v1 = recovery_lookup.get((model, task_id, dimension, "v1", rep))
        recovery_correct_vals: list[float] = []
        recovery_conf_vals: list[float] = []
        for rec in (rec_v0, rec_v1):
            if rec is not None:
                recovery_correct_vals.append(1.0 if _parse_bool(rec["correct"]) else 0.0)
                conf = _float_or_empty(rec["confidence"])
                if conf is not None:
                    recovery_conf_vals.append(conf)

        recovery_correct = (
            _mean(recovery_correct_vals) if recovery_correct_vals else None
        )
        recovery_confidence = (
            _mean(recovery_conf_vals) if recovery_conf_vals else None
        )

        kw_v0 = keyword_lookup.get((model, task_id, dimension, "v0", rep))
        kw_v1 = keyword_lookup.get((model, task_id, dimension, "v1", rep))
        keyword_correct_vals: list[float] = []
        for kw in (kw_v0, kw_v1):
            if kw is not None:
                keyword_correct_vals.append(1.0 if _parse_bool(kw["correct"]) else 0.0)
        keyword_correct = (
            _mean(keyword_correct_vals) if keyword_correct_vals else None
        )
        keyword_prediction = ""
        if kw_v0 and kw_v1:
            if kw_v0["predicted_value"] == kw_v1["predicted_value"]:
                keyword_prediction = kw_v0["predicted_value"]

        leak_v0 = leakage_lookup.get((model, task_id, dimension, "v0", rep))
        leak_v1 = leakage_lookup.get((model, task_id, dimension, "v1", rep))
        structural_scores: list[float] = []
        guessable = ""
        for leak in (leak_v0, leak_v1):
            if leak is None:
                continue
            score = _float_or_empty(leak["structural_fingerprint_score"])
            if score is not None:
                structural_scores.append(score)
            if leak.get("engineer_guessable", "").strip().lower() == "yes":
                guessable = "yes"
        if not guessable and (leak_v0 or leak_v1):
            guessable = "no"
        structural_fingerprint_score = max(structural_scores) if structural_scores else None

        lock_gain = _pair_gain(
            _parse_bool(m["has_lock_v1"]), _parse_bool(m["has_lock_v0"])
        )
        input_validation_gain = _pair_gain(
            _parse_bool(m["has_input_validation_v1"]),
            _parse_bool(m["has_input_validation_v0"]),
        )

        gap = None
        if recovery_correct is not None:
            gap = manif_score - recovery_correct

        category = ""
        if recovery_correct is not None:
            category = _taxonomy(manif_score, recovery_correct)

        dataset.append(
            {
                "generator_model": model,
                "task_id": task_id,
                "dimension": dimension,
                "rep": rep,
                "text_distance": f"{text_distance:.6f}",
                "ast_similarity": m["ast_similarity"],
                "ast_distance": f"{ast_distance:.6f}" if ast_distance is not None else "",
                "import_jaccard": f"{import_jaccard:.6f}",
                "function_jaccard": f"{function_jaccard:.6f}",
                "manifestation_score": f"{manif_score:.6f}",
                "recovery_correct": (
                    f"{recovery_correct:.6f}" if recovery_correct is not None else ""
                ),
                "recovery_confidence": (
                    f"{recovery_confidence:.6f}" if recovery_confidence is not None else ""
                ),
                "keyword_prediction": keyword_prediction,
                "keyword_correct": (
                    f"{keyword_correct:.6f}" if keyword_correct is not None else ""
                ),
                "structural_fingerprint_score": (
                    f"{structural_fingerprint_score:.6f}"
                    if structural_fingerprint_score is not None
                    else ""
                ),
                "lock_gain": f"{lock_gain:.6f}",
                "input_validation_gain": f"{input_validation_gain:.6f}",
                "engineer_guessable": guessable,
                "manifestation_recovery_gap": f"{gap:.6f}" if gap is not None else "",
                "taxonomy_category": category,
            }
        )

    return dataset


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _write_summary(run_dir: Path, dataset: list[dict[str, Any]]) -> Path:
    out_path = run_dir / "manifestation_recovery_summary.csv"

    summary_rows: list[dict[str, str]] = []

    def add_section(section: str, key_name: str, counts: dict[str, int]) -> None:
        for key in sorted(counts):
            summary_rows.append(
                {
                    "section": section,
                    "key": key_name,
                    "value": key,
                    "count": str(counts[key]),
                }
            )

    cat_counts: dict[str, int] = defaultdict(int)
    task_counts: dict[str, int] = defaultdict(int)
    dim_counts: dict[str, int] = defaultdict(int)
    model_counts: dict[str, int] = defaultdict(int)

    for row in dataset:
        cat_counts[row["taxonomy_category"]] += 1
        task_counts[row["task_id"]] += 1
        dim_counts[row["dimension"]] += 1
        model_counts[row["generator_model"]] += 1

    add_section("category", "taxonomy_category", dict(cat_counts))
    add_section("task", "task_id", dict(task_counts))
    add_section("dimension", "dimension", dict(dim_counts))
    add_section("generator_model", "generator_model", dict(model_counts))

    cat_by_task: dict[tuple[str, str], int] = defaultdict(int)
    cat_by_dim: dict[tuple[str, str], int] = defaultdict(int)
    cat_by_model: dict[tuple[str, str], int] = defaultdict(int)
    for row in dataset:
        cat = row["taxonomy_category"]
        cat_by_task[(row["task_id"], cat)] += 1
        cat_by_dim[(row["dimension"], cat)] += 1
        cat_by_model[(row["generator_model"], cat)] += 1

    for (task_id, cat), count in sorted(cat_by_task.items()):
        summary_rows.append(
            {
                "section": "category_by_task",
                "key": task_id,
                "value": cat,
                "count": str(count),
            }
        )
    for (dimension, cat), count in sorted(cat_by_dim.items()):
        summary_rows.append(
            {
                "section": "category_by_dimension",
                "key": dimension,
                "value": cat,
                "count": str(count),
            }
        )
    for (model, cat), count in sorted(cat_by_model.items()):
        summary_rows.append(
            {
                "section": "category_by_generator_model",
                "key": model,
                "value": cat,
                "count": str(count),
            }
        )

    _write_csv(out_path, ["section", "key", "value", "count"], summary_rows)
    return out_path


def _plot_heatmap(run_dir: Path, dataset: list[dict[str, Any]]) -> Path:
    import matplotlib.pyplot as plt

    tasks = sorted({row["task_id"] for row in dataset})
    dimensions = sorted({row["dimension"] for row in dataset})

    gaps: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in dataset:
        gap = _float_or_empty(row["manifestation_recovery_gap"])
        if gap is not None:
            gaps[(row["task_id"], row["dimension"])].append(gap)

    data = []
    for task_id in tasks:
        row_vals = []
        for dimension in dimensions:
            vals = gaps.get((task_id, dimension), [])
            row_vals.append(_mean(vals) if vals else float("nan"))
        data.append(row_vals)

    fig, ax = plt.subplots(figsize=(max(5, len(dimensions) * 2.5), max(6, len(tasks) * 0.7)))
    im = ax.imshow(data, aspect="auto", cmap="RdBu_r", vmin=-0.5, vmax=0.5)

    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(tasks)
    ax.set_xlabel("Dimension")
    ax.set_ylabel("Task")
    ax.set_title("Mean manifestation–recovery gap (task × dimension)")

    for i, task_id in enumerate(tasks):
        for j, dimension in enumerate(dimensions):
            val = data[i][j]
            if val == val:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="manifestation_score − recovery_correct")
    fig.tight_layout()

    out_path = run_dir / "manifestation_recovery_heatmap.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _write_report(run_dir: Path, dataset: list[dict[str, Any]]) -> Path:
    out_path = run_dir / "manifestation_recovery_report.md"

    manif_vals: list[float] = []
    rec_vals: list[float] = []
    for row in dataset:
        m = _float_or_empty(row["manifestation_score"])
        r = _float_or_empty(row["recovery_correct"])
        if m is not None and r is not None:
            manif_vals.append(m)
            rec_vals.append(r)

    pearson_r = _pearson(manif_vals, rec_vals)
    spearman_r = _spearman(manif_vals, rec_vals)

    task_gaps: dict[str, list[float]] = defaultdict(list)
    dim_gaps: dict[str, list[float]] = defaultdict(list)
    for row in dataset:
        gap = _float_or_empty(row["manifestation_recovery_gap"])
        if gap is not None:
            task_gaps[row["task_id"]].append(gap)
            dim_gaps[row["dimension"]].append(gap)

    task_rank = sorted(
        ((task, _mean(gaps), abs(_mean(gaps))) for task, gaps in task_gaps.items()),
        key=lambda t: t[2],
        reverse=True,
    )
    dim_rank = sorted(
        ((dim, _mean(gaps), abs(_mean(gaps))) for dim, gaps in dim_gaps.items()),
        key=lambda t: t[2],
        reverse=True,
    )

    gap_cases = [
        row
        for row in dataset
        if row["taxonomy_category"] == "B"
    ]
    halluc_cases = [
        row
        for row in dataset
        if row["taxonomy_category"] == "C"
    ]

    b_keyword: list[float] = []
    b_recovery: list[float] = []
    for row in gap_cases:
        kw = _float_or_empty(row["keyword_correct"])
        rec = _float_or_empty(row["recovery_correct"])
        if kw is not None:
            b_keyword.append(kw)
        if rec is not None:
            b_recovery.append(rec)

    lines: list[str] = [
        "# Manifestation–Recovery Analysis",
        "",
        f"Run: `{run_dir.name}`",
        f"Observations: {len(dataset)} artifact pairs (v0/v1)",
        "",
        "## Taxonomy thresholds",
        "",
        "Each observation is classified into exactly one category using fixed thresholds:",
        "",
        f"- **High manifestation**: `manifestation_score >= {MANIFESTATION_HIGH_THRESHOLD}`",
        f"- **Low manifestation**: `manifestation_score < {MANIFESTATION_HIGH_THRESHOLD}`",
        f"- **High recovery**: `recovery_correct >= {RECOVERY_HIGH_THRESHOLD}` (mean accuracy across v0 and v1 artifacts)",
        f"- **Low recovery**: `recovery_correct < {RECOVERY_HIGH_THRESHOLD}`",
        "",
        "`manifestation_score` = mean of available components among:",
        "`text_distance`, `ast_distance` (= 1 − `ast_similarity`),",
        "`1 − import_jaccard`, `1 − function_jaccard`.",
        "",
        "`recovery_correct` = mean of binary recovery outcomes for the v0 and v1 artifacts in the pair.",
        "",
        "| Category | Label |",
        "|----------|-------|",
        "| A | High manifestation / High recovery |",
        "| B | High manifestation / Low recovery |",
        "| C | Low manifestation / High recovery |",
        "| D | Low manifestation / Low recovery |",
        "",
        "## 1. Does manifestation strongly predict recoverability?",
        "",
        f"- Pearson correlation (manifestation_score vs recovery_correct): **{pearson_r:.4f}**",
        f"- Spearman correlation: **{spearman_r:.4f}**",
        "",
    ]

    if math.isnan(pearson_r) or abs(pearson_r) < 0.3:
        lines.extend(
            [
                "Pearson and Spearman magnitudes are below 0.3, indicating weak linear and monotonic association.",
                "Recovery_correct is discrete ({0, 0.5, 1}) while manifestation_score is continuous;",
                "this violates normality assumptions for Pearson correlation.",
                "Spearman is more appropriate here but still shows weak association at this sample size (n=120).",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Correlation magnitudes suggest non-negligible association between manifestation and recovery.",
                "Recovery_correct is discrete ({0, 0.5, 1}); Pearson assumes continuous normality.",
                "Spearman rank correlation is the more appropriate summary.",
                "",
            ]
        )

    lines.extend(
        [
            "## 2. Tasks with largest manifestation–recovery gap",
            "",
            "Ranked by mean |manifestation_score − recovery_correct| (higher = stronger dissociation):",
            "",
            "| Rank | Task | Mean gap | |gap| |",
            "|------|------|----------|-------|",
        ]
    )
    for i, (task, gap, abs_gap) in enumerate(task_rank, 1):
        lines.append(f"| {i} | {task} | {gap:.4f} | {abs_gap:.4f} |")

    lines.extend(
        [
            "",
            "## 3. Dimensions with largest manifestation–recovery gap",
            "",
            "| Rank | Dimension | Mean gap | |gap| |",
            "|------|-----------|----------|-------|",
        ]
    )
    for i, (dim, gap, abs_gap) in enumerate(dim_rank, 1):
        lines.append(f"| {i} | {dim} | {gap:.4f} | {abs_gap:.4f} |")

    lines.extend(
        [
            "",
            "## 4. Gap cases (Category B: high manifestation, low recovery)",
            "",
            f"Count: {len(gap_cases)}",
            "",
        ]
    )
    for row in sorted(
        gap_cases,
        key=lambda r: (
            -float(r["manifestation_score"]),
            r["task_id"],
            r["dimension"],
            r["rep"],
        ),
    ):
        lines.append(
            f"- **{row['task_id']}** | {row['dimension']} | {row['generator_model']} | rep {row['rep']}: "
            f"manifestation_score={row['manifestation_score']}, text_distance={row['text_distance']}, "
            f"ast_distance={row['ast_distance'] or 'n/a'}, "
            f"recovery_correct={row['recovery_correct']}, recovery_confidence={row['recovery_confidence']}, "
            f"keyword_correct={row['keyword_correct']}"
        )

    lines.extend(
        [
            "",
            "## 5. Hallucinated recovery cases (Category C: low manifestation, high recovery)",
            "",
            f"Count: {len(halluc_cases)}",
            "",
        ]
    )
    for row in sorted(
        halluc_cases,
        key=lambda r: (
            float(r["manifestation_score"]),
            r["task_id"],
            r["dimension"],
            r["rep"],
        ),
    ):
        lines.append(
            f"- **{row['task_id']}** | {row['dimension']} | {row['generator_model']} | rep {row['rep']}: "
            f"manifestation_score={row['manifestation_score']}, text_distance={row['text_distance']}, "
            f"ast_distance={row['ast_distance'] or 'n/a'}, "
            f"recovery_correct={row['recovery_correct']}, recovery_confidence={row['recovery_confidence']}, "
            f"keyword_correct={row['keyword_correct']}"
        )

    lines.extend(
        [
            "",
            "## 6. Keyword baseline vs recovery in Category B subset",
            "",
        ]
    )
    if gap_cases:
        mean_kw = _mean(b_keyword)
        mean_rec = _mean(b_recovery)
        kw_acc = sum(1 for v in b_keyword if v >= 1.0) / len(b_keyword) if b_keyword else 0.0
        rec_acc = sum(1 for v in b_recovery if v >= 1.0) / len(b_recovery) if b_recovery else 0.0
        lines.extend(
            [
                f"- Category B observations: {len(gap_cases)}",
                f"- Mean keyword_correct: **{mean_kw:.4f}**",
                f"- Mean recovery_correct: **{mean_rec:.4f}**",
                f"- Fraction with keyword_correct = 1.0: **{kw_acc:.4f}**",
                f"- Fraction with recovery_correct = 1.0: **{rec_acc:.4f}**",
            ]
        )
        if mean_kw > mean_rec + 0.05:
            lines.append(
                "- Keyword baseline exceeds LLM recovery in this subset; "
                "proxy keywords partially explain cases where recovery fails despite manifestation."
            )
        elif mean_kw < mean_rec - 0.05:
            lines.append(
                "- LLM recovery exceeds keyword baseline in this subset; "
                "the gap is not explained by keyword proxies alone."
            )
        else:
            lines.append(
                "- Keyword and recovery accuracies are similar in Category B; "
                "keyword baseline does not clearly explain the manifestation–recovery gap."
            )
    else:
        lines.append("- No Category B observations; comparison not applicable.")

    cat_counts: dict[str, int] = defaultdict(int)
    for row in dataset:
        cat_counts[row["taxonomy_category"]] += 1

    lines.extend(
        [
            "",
            "## 7. Conclusion",
            "",
            f"Category counts: A={cat_counts.get('A', 0)}, B={cat_counts.get('B', 0)}, "
            f"C={cat_counts.get('C', 0)}, D={cat_counts.get('D', 0)}.",
            "",
        ]
    )

    weak_corr = math.isnan(pearson_r) or abs(pearson_r) < 0.3
    has_dissociation = cat_counts.get("B", 0) + cat_counts.get("C", 0) >= 10

    if weak_corr and has_dissociation:
        text = (
            "**B.** Manifestation and recoverability show systematic dissociation. "
            "The manifestation–recovery gap deserves further investigation."
        )
    elif not weak_corr and cat_counts.get("B", 0) <= 5 and cat_counts.get("C", 0) <= 5:
        text = (
            "**A.** Recoverability is almost completely explained by manifestation. "
            "There is no evidence of a distinct phenomenon."
        )
    else:
        text = (
            "**B.** Manifestation and recoverability show systematic dissociation. "
            "The manifestation–recovery gap deserves further investigation."
        )

    lines.append(text)
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def run_manifestation_recovery_analysis(project_root: Path, run_name: str) -> dict[str, Path]:
    run_dir = project_root / "results" / "runs" / run_name
    required = [
        run_dir / "manifestation.csv",
        run_dir / "recovery.csv",
        run_dir / "keyword_baseline.csv",
        run_dir / "proxy_leakage_report.csv",
    ]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")

    dataset = _build_dataset(run_dir)
    dataset_path = run_dir / "manifestation_recovery_dataset.csv"
    _write_csv(dataset_path, DATASET_FIELDS, dataset)

    summary_path = _write_summary(run_dir, dataset)
    report_path = _write_report(run_dir, dataset)
    heatmap_path = _plot_heatmap(run_dir, dataset)

    print(f"Wrote {dataset_path} ({len(dataset)} observations)")
    print(f"Wrote {summary_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {heatmap_path}")

    return {
        "dataset": dataset_path,
        "summary": summary_path,
        "report": report_path,
        "heatmap": heatmap_path,
    }
