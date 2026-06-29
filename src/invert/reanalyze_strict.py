from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


MANIFESTATION_HIGH_THRESHOLD = 0.10

STRICT_DATASET_FIELDS = [
    "generator_model",
    "task_id",
    "dimension",
    "rep",
    "manifestation_score",
    "text_distance",
    "ast_distance",
    "import_jaccard",
    "function_jaccard",
    "recovery_mean",
    "recovery_strict",
    "recovery_partial",
    "recovery_none",
    "v0_correct",
    "v1_correct",
    "keyword_v0_correct",
    "keyword_v1_correct",
    "keyword_strict",
    "keyword_partial",
    "keyword_none",
    "manipulation_confirmed",
]


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _float_or_none(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _pearson(x: list[float], y: list[float]) -> float:
    if len(x) < 2:
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


def _log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _hypergeom_log_pmf(k: int, n: int, K: int, N: int) -> float:
    return _log_choose(K, k) + _log_choose(N - K, n - k) - _log_choose(N, n)


def _fisher_exact_2x2(a: int, b: int, c: int, d: int) -> dict[str, Any]:
    """Rows=manifestation (high/low), cols=recovery_strict (1/0).

    high_manifestation: a=strict1, b=strict0
    low_manifestation:  c=strict1, d=strict0
    """
    row_high = a + b
    row_low = c + d
    col_strict = a + c
    col_not = b + d
    total = row_high + row_low

    def table_prob(x11: int) -> float:
        x12 = row_high - x11
        x21 = col_strict - x11
        x22 = row_low - x21
        if min(x11, x12, x21, x22) < 0:
            return 0.0
        return math.exp(
            _log_choose(col_strict, x11)
            + _log_choose(col_not, x12)
            - _log_choose(total, row_high)
        )

    observed = table_prob(a)
    min_a = max(0, col_strict - row_low)
    max_a = min(row_high, col_strict)
    p_value = 0.0
    for x11 in range(min_a, max_a + 1):
        p = table_prob(x11)
        if p <= observed + 1e-12:
            p_value += p

    return {
        "high_manifestation_strict": a,
        "high_manifestation_not_strict": b,
        "low_manifestation_strict": c,
        "low_manifestation_not_strict": d,
        "fisher_p_value": min(1.0, p_value),
    }


def _strict_taxonomy(manifestation_score: float, recovery_strict: int) -> str:
    high_m = manifestation_score >= MANIFESTATION_HIGH_THRESHOLD
    high_r = recovery_strict == 1
    if high_m and high_r:
        return "A"
    if high_m and not high_r:
        return "B"
    if not high_m and high_r:
        return "C"
    return "D"


def _pair_gain(v1: bool, v0: bool) -> bool:
    return v1 and not v0


def _recovery_flags(v0: bool | None, v1: bool | None) -> dict[str, Any]:
    if v0 is None or v1 is None:
        return {
            "recovery_mean": "",
            "recovery_strict": "",
            "recovery_partial": "",
            "recovery_none": "",
            "v0_correct": "",
            "v1_correct": "",
        }

    v0_i = 1 if v0 else 0
    v1_i = 1 if v1 else 0
    mean = (v0_i + v1_i) / 2.0
    n_correct = v0_i + v1_i
    return {
        "recovery_mean": f"{mean:.6f}",
        "recovery_strict": "1" if n_correct == 2 else "0",
        "recovery_partial": "1" if n_correct == 1 else "0",
        "recovery_none": "1" if n_correct == 0 else "0",
        "v0_correct": str(v0).lower(),
        "v1_correct": str(v1).lower(),
    }


def _keyword_flags(v0: bool | None, v1: bool | None) -> dict[str, str]:
    if v0 is None or v1 is None:
        return {
            "keyword_v0_correct": "",
            "keyword_v1_correct": "",
            "keyword_strict": "",
            "keyword_partial": "",
            "keyword_none": "",
        }
    v0_i = 1 if v0 else 0
    v1_i = 1 if v1 else 0
    n_correct = v0_i + v1_i
    return {
        "keyword_v0_correct": str(v0).lower(),
        "keyword_v1_correct": str(v1).lower(),
        "keyword_strict": "1" if n_correct == 2 else "0",
        "keyword_partial": "1" if n_correct == 1 else "0",
        "keyword_none": "1" if n_correct == 0 else "0",
    }


def _manipulation_confirmed(
    manifestation_score: float,
    text_distance: float,
    ast_distance: float | None,
    lock_gain: bool,
    input_validation_gain: bool,
    kw_v0: bool | None,
    kw_v1: bool | None,
) -> bool:
    if manifestation_score > 0:
        return True
    if text_distance > 0:
        return True
    if ast_distance is not None and ast_distance > 0:
        return True
    if lock_gain:
        return True
    if input_validation_gain:
        return True
    if kw_v0 is not None and kw_v1 is not None and kw_v0 != kw_v1:
        return True
    return False


def _build_strict_dataset(run_dir: Path) -> list[dict[str, Any]]:
    prior_rows = _load_csv(run_dir / "manifestation_recovery_dataset.csv")
    manifest_rows = _load_csv(run_dir / "manifestation.csv")
    recovery_rows = _load_csv(run_dir / "recovery.csv")
    keyword_rows = _load_csv(run_dir / "keyword_baseline.csv")

    manifest_lookup = {
        (r["generator_model"], r["task_id"], r["dimension"], r["rep"]): r
        for r in manifest_rows
    }

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

    prior_lookup = {
        (r["generator_model"], r["task_id"], r["dimension"], r["rep"]): r
        for r in prior_rows
    }

    dataset: list[dict[str, Any]] = []
    for key, prior in sorted(prior_lookup.items()):
        model, task_id, dimension, rep = key
        m = manifest_lookup.get(key, {})

        text_distance = _float_or_none(prior.get("text_distance", ""))
        ast_distance = _float_or_none(prior.get("ast_distance", ""))
        import_jaccard = _float_or_none(prior.get("import_jaccard", ""))
        function_jaccard = _float_or_none(prior.get("function_jaccard", ""))
        manifestation_score = _float_or_none(prior.get("manifestation_score", ""))

        if text_distance is None and m:
            text_distance = _float_or_none(m.get("text_distance", ""))
        if ast_distance is None and m:
            ast_sim = _float_or_none(m.get("ast_similarity", ""))
            ast_distance = (1.0 - ast_sim) if ast_sim is not None else None
        if import_jaccard is None and m:
            import_jaccard = _float_or_none(m.get("import_jaccard", ""))
        if function_jaccard is None and m:
            function_jaccard = _float_or_none(m.get("function_name_jaccard", ""))
        if manifestation_score is None and all(
            v is not None for v in (text_distance, import_jaccard, function_jaccard)
        ):
            parts = [text_distance, 1.0 - import_jaccard, 1.0 - function_jaccard]
            if ast_distance is not None:
                parts.append(ast_distance)
            manifestation_score = _mean(parts)

        rec_v0 = recovery_lookup.get((model, task_id, dimension, "v0", rep))
        rec_v1 = recovery_lookup.get((model, task_id, dimension, "v1", rep))
        v0 = _parse_bool(rec_v0["correct"]) if rec_v0 else None
        v1 = _parse_bool(rec_v1["correct"]) if rec_v1 else None

        kw_v0_row = keyword_lookup.get((model, task_id, dimension, "v0", rep))
        kw_v1_row = keyword_lookup.get((model, task_id, dimension, "v1", rep))
        kw_v0 = _parse_bool(kw_v0_row["correct"]) if kw_v0_row else None
        kw_v1 = _parse_bool(kw_v1_row["correct"]) if kw_v1_row else None

        lock_gain = False
        input_validation_gain = False
        if m:
            lock_gain = _pair_gain(
                _parse_bool(m["has_lock_v1"]), _parse_bool(m["has_lock_v0"])
            )
            input_validation_gain = _pair_gain(
                _parse_bool(m["has_input_validation_v1"]),
                _parse_bool(m["has_input_validation_v0"]),
            )

        confirmed = False
        if manifestation_score is not None and text_distance is not None:
            confirmed = _manipulation_confirmed(
                manifestation_score,
                text_distance,
                ast_distance,
                lock_gain,
                input_validation_gain,
                kw_v0,
                kw_v1,
            )

        recovery = _recovery_flags(v0, v1)
        keyword = _keyword_flags(kw_v0, kw_v1)

        strict_cat = ""
        if manifestation_score is not None and recovery["recovery_strict"] != "":
            strict_cat = _strict_taxonomy(
                manifestation_score, int(recovery["recovery_strict"])
            )

        row: dict[str, Any] = {
            "generator_model": model,
            "task_id": task_id,
            "dimension": dimension,
            "rep": rep,
            "manifestation_score": (
                f"{manifestation_score:.6f}" if manifestation_score is not None else ""
            ),
            "text_distance": (
                f"{text_distance:.6f}" if text_distance is not None else ""
            ),
            "ast_distance": (
                f"{ast_distance:.6f}" if ast_distance is not None else ""
            ),
            "import_jaccard": (
                f"{import_jaccard:.6f}" if import_jaccard is not None else ""
            ),
            "function_jaccard": (
                f"{function_jaccard:.6f}" if function_jaccard is not None else ""
            ),
            "manipulation_confirmed": str(confirmed).lower(),
            "strict_taxonomy_category": strict_cat,
            **recovery,
            **keyword,
        }
        dataset.append(row)

    return dataset


def _count_categories(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        cat = row.get("strict_taxonomy_category", "")
        if cat:
            counts[cat] += 1
    return dict(counts)


def _write_summary(run_dir: Path, dataset: list[dict[str, Any]]) -> Path:
    out_path = run_dir / "manifestation_recovery_strict_summary.csv"
    summary_rows: list[dict[str, str]] = []

    def add_counts(section: str, key_name: str, items: list[dict[str, Any]]) -> None:
        counts: dict[str, int] = defaultdict(int)
        for row in items:
            counts[row[key_name]] += 1
        for value in sorted(counts):
            summary_rows.append(
                {
                    "section": section,
                    "key": key_name,
                    "value": value,
                    "count": str(counts[value]),
                }
            )

    complete = [r for r in dataset if r.get("recovery_mean", "")]
    confirmed = [r for r in complete if r.get("manipulation_confirmed") == "true"]

    for section, rows in (
        ("category_all", complete),
        ("category_manipulation_confirmed", confirmed),
    ):
        counts = _count_categories(rows)
        for cat in sorted(counts):
            summary_rows.append(
                {
                    "section": section,
                    "key": "strict_taxonomy_category",
                    "value": cat,
                    "count": str(counts[cat]),
                }
            )

    for section, rows in (
        ("task_all", complete),
        ("task_manipulation_confirmed", confirmed),
    ):
        task_cats: dict[tuple[str, str], int] = defaultdict(int)
        for row in rows:
            task_cats[(row["task_id"], row.get("strict_taxonomy_category", ""))] += 1
        for (task_id, cat), count in sorted(task_cats.items()):
            summary_rows.append(
                {
                    "section": section,
                    "key": task_id,
                    "value": cat,
                    "count": str(count),
                }
            )

    for section, rows, key in (
        ("dimension_all", complete, "dimension"),
        ("dimension_manipulation_confirmed", confirmed, "dimension"),
        ("generator_model_all", complete, "generator_model"),
        ("generator_model_manipulation_confirmed", confirmed, "generator_model"),
    ):
        grouped: dict[tuple[str, str], int] = defaultdict(int)
        for row in rows:
            grouped[(row[key], row.get("strict_taxonomy_category", ""))] += 1
        for (label, cat), count in sorted(grouped.items()):
            summary_rows.append(
                {
                    "section": section,
                    "key": label,
                    "value": cat,
                    "count": str(count),
                }
            )

    _write_csv(out_path, ["section", "key", "value", "count"], summary_rows)
    return out_path


def _plot_heatmap(run_dir: Path, dataset: list[dict[str, Any]]) -> Path:
    import matplotlib.pyplot as plt

    complete = [r for r in dataset if r.get("recovery_strict", "")]
    tasks = sorted({r["task_id"] for r in complete})
    dimensions = sorted({r["dimension"] for r in complete})

    cells: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in complete:
        rs = int(row["recovery_strict"])
        ms = float(row["manifestation_score"])
        cells[(row["task_id"], row["dimension"])].append(rs - ms)

    data = []
    for task_id in tasks:
        row_vals = []
        for dimension in dimensions:
            vals = cells.get((task_id, dimension), [])
            row_vals.append(_mean(vals) if vals else float("nan"))
        data.append(row_vals)

    fig, ax = plt.subplots(
        figsize=(max(5, len(dimensions) * 2.5), max(6, len(tasks) * 0.7))
    )
    im = ax.imshow(data, aspect="auto", cmap="RdBu_r", vmin=-0.5, vmax=0.5)
    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(tasks)
    ax.set_xlabel("Dimension")
    ax.set_ylabel("Task")
    ax.set_title("Mean recovery_strict − manifestation_score")

    for i, task_id in enumerate(tasks):
        for j, dimension in enumerate(dimensions):
            val = data[i][j]
            if val == val:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="recovery_strict − manifestation_score")
    fig.tight_layout()
    out_path = run_dir / "manifestation_recovery_strict_heatmap.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _prior_category_counts(run_dir: Path) -> dict[str, int]:
    rows = _load_csv(run_dir / "manifestation_recovery_dataset.csv")
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        cat = row.get("taxonomy_category", "")
        if cat:
            counts[cat] += 1
    return dict(counts)


def _write_report(
    run_dir: Path,
    dataset: list[dict[str, Any]],
    fisher: dict[str, Any],
    pearson_mean: float,
    pearson_strict: float,
    spearman_strict: float,
) -> Path:
    out_path = run_dir / "manifestation_recovery_strict_report.md"
    complete = [r for r in dataset if r.get("recovery_mean", "")]
    confirmed = [r for r in complete if r.get("manipulation_confirmed") == "true"]

    mean_dist: dict[str, int] = defaultdict(int)
    for row in complete:
        mean_dist[row["recovery_mean"]] += 1

    strict_success = sum(1 for r in complete if r["recovery_strict"] == "1")
    partial_only = sum(
        1
        for r in complete
        if r["recovery_partial"] == "1" and r["recovery_strict"] == "0"
    )
    none_count = sum(1 for r in complete if r["recovery_none"] == "1")

    prior = _prior_category_counts(run_dir)
    strict_all = _count_categories(complete)
    strict_conf = _count_categories(confirmed)

    cat_b = strict_all.get("B", 0)
    cat_c = strict_all.get("C", 0)

    x_mean = [float(r["manifestation_score"]) for r in complete]
    y_mean = [float(r["recovery_mean"]) for r in complete]
    y_strict = [float(r["recovery_strict"]) for r in complete]

    x_conf = [float(r["manifestation_score"]) for r in confirmed]
    y_strict_conf = [float(r["recovery_strict"]) for r in confirmed]

    lines = [
        "# Strict Manifestation–Recovery Reanalysis",
        "",
        f"Run: `{run_dir.name}`",
        "",
        "## 1. Recovery mean distribution",
        "",
        f"Complete pairs: {len(complete)}",
        "",
    ]
    for val in sorted(mean_dist, key=float):
        lines.append(f"- recovery_mean = {float(val):.1f}: **{mean_dist[val]}** pairs")
    lines.append("")

    lines.extend(
        [
            "## 2. Strict recovery successes",
            "",
            f"- recovery_strict = 1 (both v0 and v1 correct): **{strict_success}** / {len(complete)}",
            "",
            "## 3. Partial-only recoveries",
            "",
            f"- recovery_partial = 1 and recovery_strict = 0: **{partial_only}**",
            f"- recovery_none = 1 (neither correct): **{none_count}**",
            "",
            "## 4. Taxonomy change vs previous analysis",
            "",
            "Previous thresholds: high recovery = recovery_mean >= 0.5.",
            "Strict thresholds: high recovery = recovery_strict == 1.",
            "",
            "| Category | Previous | Strict (all) | Strict (manipulation confirmed) |",
            "|----------|----------|--------------|----------------------------------|",
        ]
    )
    for cat in ("A", "B", "C", "D"):
        lines.append(
            f"| {cat} | {prior.get(cat, 0)} | {strict_all.get(cat, 0)} | {strict_conf.get(cat, 0)} |"
        )

    lines.extend(
        [
            "",
            "## 5. Does Category B now exist?",
            "",
        ]
    )
    if cat_b > 0:
        lines.append(
            f"**Yes.** Category B count (all pairs): **{cat_b}**. "
            f"After manipulation_confirmed filter: **{strict_conf.get('B', 0)}**."
        )
    else:
        lines.append(
            "**No.** Category B is empty even under strict recovery."
        )
    lines.extend(
        [
            "",
            "## 6. Does Category C survive?",
            "",
            f"Category C count (all pairs): **{cat_c}** (previous: {prior.get('C', 0)}). "
            f"After manipulation_confirmed filter: **{strict_conf.get('C', 0)}**.",
            "",
            "## 7. After filtering to manipulation_confirmed == true",
            "",
            f"- Pairs retained: **{len(confirmed)}** / {len(complete)}",
            f"- Category counts: A={strict_conf.get('A', 0)}, B={strict_conf.get('B', 0)}, "
            f"C={strict_conf.get('C', 0)}, D={strict_conf.get('D', 0)}",
            "",
        ]
    )
    if confirmed:
        lines.append(
            f"- Pearson(manifestation_score, recovery_strict) on confirmed subset: "
            f"**{_pearson(x_conf, y_strict_conf):.4f}**"
        )
    lines.append("")

    lines.extend(
        [
            "## 8. Is there still evidence for a manifestation–recovery gap?",
            "",
            "Statistical checks (all complete pairs):",
            "",
            f"- Pearson(manifestation_score, recovery_mean): **{pearson_mean:.4f}**",
            f"- Pearson(manifestation_score, recovery_strict): **{pearson_strict:.4f}**",
            f"- Spearman(manifestation_score, recovery_strict): **{spearman_strict:.4f}**",
            "",
            "Fisher 2×2 table (high_manifestation × recovery_strict):",
            "",
            "| | recovery_strict=1 | recovery_strict=0 |",
            "|---|---:|---:|",
            f"| manifestation >= 0.10 | {fisher['high_manifestation_strict']} | {fisher['high_manifestation_not_strict']} |",
            f"| manifestation < 0.10 | {fisher['low_manifestation_strict']} | {fisher['low_manifestation_not_strict']} |",
            "",
            f"Fisher exact p-value: **{fisher['fisher_p_value']:.6f}**",
            "",
        ]
    )

    if cat_b == 0 and pearson_strict > 0.2:
        gap_evidence = (
            "Weak positive coupling remains, but Category B is empty; "
            "no high-manifestation / strict-failure cases."
        )
    elif cat_b > 0:
        gap_evidence = (
            f"Category B contains {cat_b} pairs where manifestation is high "
            f"but strict recovery fails. This is the operational gap cell."
        )
    else:
        gap_evidence = "No Category B and no strict-failure pairs at all."

    lines.extend(
        [
            gap_evidence,
            "",
            "## 9. Does the previous conclusion survive?",
            "",
        ]
    )

    prev_c = prior.get("C", 0)
    prev_collapsed = prev_c >= 10 and cat_c <= max(2, prev_c // 4)
    if prev_collapsed and cat_b >= 20:
        conclusion = "C"
        lines.append(
            "The previous conclusion **does not survive in its original form**. "
            f"Category C collapsed from {prev_c} to {cat_c} under strict recovery. "
            f"However, Category B now contains **{cat_b}** high-manifestation pairs "
            "that fail strict recovery — a real, stricter gap cell absent from the permissive taxonomy."
        )
    elif prev_collapsed:
        lines.append(
            "The previous conclusion **does not survive**. "
            f"Category C collapsed from {prev_c} to {cat_c} under strict recovery. "
            "The prior 'systematic dissociation' was driven by treating recovery_mean=0.5 "
            "(exactly one of two artifacts correct) as high recovery. "
            "Under strict recovery, the four-cell taxonomy is populated across multiple categories "
            "rather than collapsing to a manifestation-only split."
        )
        conclusion = "B"
    elif cat_b > 10 and pearson_strict < 0.35:
        lines.append(
            "The previous conclusion **weakens but a stricter gap remains**. "
            f"Category B contains {cat_b} pairs; correlation stays weak (r={pearson_strict:.3f})."
        )
        conclusion = "C"
    elif cat_b > 0:
        lines.append(
            "The previous conclusion **weakens but a stricter gap remains**. "
            "Some high-manifestation pairs fail strict recovery."
        )
        conclusion = "C"
    else:
        lines.append(
            "The previous conclusion **does not survive**. "
            "Strict recovery removes the apparent dissociation artifact."
        )
        conclusion = "B"

    conclusion_text = {
        "A": "**A.** The previous manifestation–recovery gap interpretation survives the strict reanalysis.",
        "B": "**B.** The previous interpretation collapses; the apparent dissociation was driven by the permissive recovery threshold.",
        "C": "**C.** The previous interpretation weakens but a smaller, stricter gap remains.",
    }
    lines.extend(
        [
            "",
            "## Final conclusion",
            "",
            conclusion_text[conclusion],
            "",
        ]
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def run_reanalyze_strict(project_root: Path, run_name: str) -> dict[str, Path]:
    run_dir = project_root / "results" / "runs" / run_name
    required = [
        run_dir / "manifestation_recovery_dataset.csv",
        run_dir / "recovery.csv",
        run_dir / "manifestation.csv",
        run_dir / "keyword_baseline.csv",
    ]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")

    dataset = _build_strict_dataset(run_dir)
    dataset_path = run_dir / "manifestation_recovery_strict_dataset.csv"
    _write_csv(dataset_path, STRICT_DATASET_FIELDS, dataset)

    complete = [r for r in dataset if r.get("recovery_mean", "")]
    x = [float(r["manifestation_score"]) for r in complete]
    y_mean = [float(r["recovery_mean"]) for r in complete]
    y_strict = [float(r["recovery_strict"]) for r in complete]

    pearson_mean = _pearson(x, y_mean)
    pearson_strict = _pearson(x, y_strict)
    spearman_strict = _spearman(x, y_strict)

    high_strict = low_strict = high_not = low_not = 0
    for row in complete:
        high_m = float(row["manifestation_score"]) >= MANIFESTATION_HIGH_THRESHOLD
        strict = int(row["recovery_strict"]) == 1
        if high_m and strict:
            high_strict += 1
        elif high_m and not strict:
            high_not += 1
        elif not high_m and strict:
            low_strict += 1
        else:
            low_not += 1

    fisher = _fisher_exact_2x2(high_strict, high_not, low_strict, low_not)

    summary_path = _write_summary(run_dir, dataset)
    report_path = _write_report(
        run_dir,
        dataset,
        fisher,
        pearson_mean,
        pearson_strict,
        spearman_strict,
    )
    heatmap_path = _plot_heatmap(run_dir, dataset)

    print(f"Wrote {dataset_path} ({len(dataset)} pairs)")
    print(f"Wrote {summary_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {heatmap_path}")
    print(f"Strict taxonomy: {_count_categories(complete)}")
    print(f"Pearson(manifestation, recovery_strict) = {pearson_strict:.4f}")

    return {
        "dataset": dataset_path,
        "summary": summary_path,
        "report": report_path,
        "heatmap": heatmap_path,
    }
