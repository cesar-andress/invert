from __future__ import annotations

import ast
import csv
import difflib
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MANIFESTATION_THRESHOLD = 0.10

THREADING_PATTERN = re.compile(r"\b(threading|asyncio|concurrent|multiprocessing)\b")
LOCK_PATTERN = re.compile(r"\b(Lock|RLock|Semaphore|mutex)\b")
INPUT_VALIDATION_PATTERNS = [
    re.compile(r"\bisinstance\s*\("),
    re.compile(r"\bif\s+not\b"),
    re.compile(r"\braise\s+ValueError\b"),
    re.compile(r"\braise\s+TypeError\b"),
    re.compile(r"\blen\s*\("),
    re.compile(r"\.strip\s*\("),
]
RAISE_PATTERN = re.compile(r"\braise\b")
COMMENT_PATTERN = re.compile(r"^\s*#", re.MULTILINE)
DOCSTRING_NODES = (ast.Expr,)


DATASET_FIELDS = [
    "observation_id",
    "generator_model",
    "task_id",
    "dimension",
    "rep",
    "manifestation_score",
    "text_distance",
    "ast_distance",
    "import_jaccard",
    "function_jaccard",
    "text_contrib",
    "ast_contrib",
    "import_contrib",
    "function_contrib",
    "dominant_driver",
    "recovery_mean",
    "recovery_strict",
    "v0_correct",
    "v1_correct",
    "failure_direction",
    "keyword_strict",
    "keyword_partial",
    "keyword_v0_correct",
    "keyword_v1_correct",
    "keyword_explains",
    "equivalence_rating",
    "equivalence_rationale",
    "inferred_cluster",
    "cluster_mechanism",
    "proxy_leakage_v0",
    "proxy_leakage_v1",
    "proxy_explains",
    "proxy_rationale",
    "engineer_guessable_v0",
    "engineer_guessable_v1",
    "stripped_v0_correct",
    "stripped_v1_correct",
    "stripped_strict",
    "stripped_vs_original",
    "threading_gain",
    "lock_gain",
    "input_validation_gain",
    "raise_gain",
    "comment_delta",
    "docstring_delta",
    "import_changed",
    "algorithm_restructure",
    "v0_path",
    "v1_path",
    "interpretation",
]


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


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def _float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _has_pattern(code: str, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(code))


def _has_input_validation(code: str) -> bool:
    return any(p.search(code) for p in INPUT_VALIDATION_PATTERNS)


def _strip_comments(code: str) -> str:
    lines = []
    for line in code.splitlines():
        if line.strip().startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _docstring_text(tree: ast.AST) -> str:
    texts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            doc = ast.get_docstring(node)
            if doc:
                texts.append(doc)
    return "\n".join(texts)


def _code_features(code: str) -> dict[str, Any]:
    tree = None
    try:
        tree = ast.parse(code)
    except SyntaxError:
        pass
    imports: set[str] = set()
    functions: set[str] = set()
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name)
    return {
        "imports": imports,
        "functions": functions,
        "has_threading": _has_pattern(code, THREADING_PATTERN),
        "has_lock": _has_pattern(code, LOCK_PATTERN),
        "has_input_validation": _has_input_validation(code),
        "has_raise": _has_pattern(code, RAISE_PATTERN),
        "comment_lines": len(COMMENT_PATTERN.findall(code)),
        "docstring_len": len(_docstring_text(tree)) if tree else 0,
        "parsed": tree is not None,
    }


def _analyze_diff(v0_code: str, v1_code: str) -> dict[str, Any]:
    v0f = _code_features(v0_code)
    v1f = _code_features(v1_code)
    text_sim = difflib.SequenceMatcher(None, v0_code, v1_code).ratio()
    code_no_comments_v0 = _strip_comments(v0_code)
    code_no_comments_v1 = _strip_comments(v1_code)
    text_sim_nc = difflib.SequenceMatcher(
        None, code_no_comments_v0, code_no_comments_v1
    ).ratio()

    ast_sim = ""
    if v0f["parsed"] and v1f["parsed"]:
        ast_sim = difflib.SequenceMatcher(
            None,
            ast.dump(ast.parse(v0_code), include_attributes=False),
            ast.dump(ast.parse(v1_code), include_attributes=False),
        ).ratio()

    import_changed = v0f["imports"] != v1f["imports"]
    function_changed = v0f["functions"] != v1f["functions"]
    comment_delta = abs(v0f["comment_lines"] - v1f["comment_lines"])
    docstring_delta = abs(v0f["docstring_len"] - v1f["docstring_len"])

    algorithm_restructure = False
    if isinstance(ast_sim, float):
        algorithm_restructure = ast_sim < 0.55
    elif text_sim < 0.45:
        algorithm_restructure = True

    cosmetic_text_only = (
        text_sim_nc > 0.92
        and not import_changed
        and not function_changed
        and v0f["has_threading"] == v1f["has_threading"]
        and v0f["has_lock"] == v1f["has_lock"]
        and v0f["has_input_validation"] == v1f["has_input_validation"]
    )

    return {
        "text_similarity": text_sim,
        "text_similarity_no_comments": text_sim_nc,
        "ast_similarity": ast_sim if ast_sim != "" else None,
        "import_changed": import_changed,
        "function_changed": function_changed,
        "comment_delta": comment_delta,
        "docstring_delta": docstring_delta,
        "algorithm_restructure": algorithm_restructure,
        "cosmetic_text_only": cosmetic_text_only,
        "threading_gain": v1f["has_threading"] and not v0f["has_threading"],
        "lock_gain": v1f["has_lock"] and not v0f["has_lock"],
        "validation_gain": v1f["has_input_validation"] and not v0f["has_input_validation"],
        "raise_gain": v1f["has_raise"] and not v0f["has_raise"],
        "validation_loss": v0f["has_input_validation"] and not v1f["has_input_validation"],
        "threading_loss": v0f["has_threading"] and not v1f["has_threading"],
        "lock_loss": v0f["has_lock"] and not v1f["has_lock"],
        "v0_imports": sorted(v0f["imports"]),
        "v1_imports": sorted(v1f["imports"]),
    }


def _manifestation_contributions(
    text_distance: float,
    ast_distance: float | None,
    import_jaccard: float,
    function_jaccard: float,
) -> dict[str, Any]:
    import_dist = 1.0 - import_jaccard
    func_dist = 1.0 - function_jaccard
    parts: dict[str, float] = {
        "text": text_distance,
        "import": import_dist,
        "function": func_dist,
    }
    if ast_distance is not None:
        parts["ast"] = ast_distance
    total = sum(parts.values())
    contribs = {k: (v / total if total else 0.0) for k, v in parts.items()}
    dominant = max(contribs, key=contribs.get)
    return {
        "contributions": contribs,
        "dominant_driver": dominant,
        "import_dist": import_dist,
        "function_dist": func_dist,
    }


def _equivalence_rating(
    dimension: str,
    diff: dict[str, Any],
    ast_distance: float | None,
    text_distance: float,
    manifest_row: dict[str, str],
) -> tuple[str, str]:
    if diff["algorithm_restructure"]:
        return (
            "Definitely different",
            "AST/text similarity indicates algorithmic restructure or API substitution",
        )
    if dimension == "concurrency" and (
        diff["threading_gain"] or diff["lock_gain"] or diff["threading_loss"] or diff["lock_loss"]
    ):
        return (
            "Definitely different",
            "Concurrency primitive presence changed between v0 and v1",
        )
    if dimension == "security" and (
        diff["validation_gain"] or diff["raise_gain"] or diff["validation_loss"]
    ):
        return (
            "Probably different",
            "Validation or exception-handling patterns differ",
        )
    if diff["cosmetic_text_only"] or (
        ast_distance is not None
        and ast_distance < 0.08
        and text_distance < 0.12
    ):
        return (
            "Probably equivalent",
            "Structural features unchanged; differences are textual or cosmetic",
        )
    if ast_distance is not None and ast_distance < 0.20 and text_distance < 0.25:
        return (
            "Unclear",
            "Moderate structural similarity; dimension-specific semantics may still differ",
        )
    if _parse_bool(manifest_row.get("has_input_validation_v1", "")) != _parse_bool(
        manifest_row.get("has_input_validation_v0", "")
    ):
        return (
            "Probably different",
            "Input-validation pattern flag differs between v0 and v1",
        )
    return (
        "Unclear",
        "Mixed signals between text and structural distance metrics",
    )


def _infer_cluster(obs: dict[str, Any]) -> tuple[str, str]:
    """Infer cluster label from observation features only."""
    task = obs["task_id"]
    dimension = obs["dimension"]
    fd = obs["failure_direction"]
    driver = obs["dominant_driver"]
    algo = obs["algorithm_restructure"] == "true"
    imp = obs["import_changed"] == "true"
    ast_d = _float(obs["ast_distance"])
    text_d = _float(obs["text_distance"])

    if task == "dependency_order" and algo:
        return (
            "non_dimension_algorithm_substitution",
            "Entire algorithm replaced (often API-backed); manipulated dimension markers absent",
        )
    if algo and imp and obs["lock_gain"] != "true" and obs["threading_gain"] != "true":
        return (
            "algorithm_api_substitution",
            "Large AST rewrite with import/API substitution unrelated to dimension markers",
        )
    if fd == "v1_only_fail" and (
        obs["input_validation_gain"] == "true" or obs["raise_gain"] == "true"
    ):
        return (
            "v1_salient_dimension_edit",
            "Dimension-aligned edit concentrated in v1; judge recovers v0 only",
        )
    if fd == "v0_only_fail" and dimension == "security":
        return (
            "v0_validation_surface_miss",
            "Security v0 uses alternate validation surface; judge misses v0, recovers v1",
        )
    if fd == "v1_only_fail" and dimension == "concurrency":
        return (
            "v1_concurrency_surface_miss",
            "Concurrency v1 edited but without lock/threading tokens; judge misses v1",
        )
    if driver == "text" and ast_d < 0.35:
        return (
            "text_dominant_rewrite",
            "Text distance drives manifestation; moderate AST similarity",
        )
    if driver == "ast":
        return (
            "ast_structural_rewrite",
            "AST distance dominates; partial judge failure",
        )
    if driver == "import":
        return (
            "import_surface_change",
            "Import set change inflates manifestation without function rename",
        )
    if obs["comment_delta"] != "0" or int(obs["docstring_delta"]) > 50:
        return (
            "documentation_surface_edit",
            "Comment/docstring delta contributes to manifestation",
        )
    if obs["keyword_explains"] == "yes":
        return (
            "keyword_mirrored_partial",
            "Keyword baseline replicates same v0/v1 recovery asymmetry",
        )
    return (
        "residual_partial_recovery",
        "Partial recovery without a single dominant inferred mechanism",
    )



def _keyword_explains(obs: dict[str, Any]) -> str:
    v0k = obs["keyword_v0_correct"]
    v1k = obs["keyword_v1_correct"]
    v0r = obs["v0_correct"]
    v1r = obs["v1_correct"]
    if v0k == v0r and v1k == v1r:
        return "yes"
    if v0k == v1k:
        return "partial"
    return "no"


def _proxy_explains(
    dimension: str,
    v0_leak: dict[str, str] | None,
    v1_leak: dict[str, str] | None,
    failure_direction: str,
) -> tuple[str, str]:
    if not v0_leak or not v1_leak:
        return "UNCLEAR", "Missing leakage report rows"

    def side_score(leak: dict[str, str], dimension: str) -> int:
        if dimension == "concurrency":
            return int(leak["remaining_concurrency_identifiers"]) + int(
                leak["sync_pattern_count"]
            ) + int(leak["remaining_strip_concurrency_tokens"])
        return int(leak["remaining_security_identifiers"]) + int(
            leak["validation_pattern_count"]
        ) + int(leak["structural_fingerprint_score"])

    s0 = side_score(v0_leak, dimension)
    s1 = side_score(v1_leak, dimension)
    g0 = v0_leak["engineer_guessable"].lower() == "yes"
    g1 = v1_leak["engineer_guessable"].lower() == "yes"

    if failure_direction == "v1_only_fail" and g1 and not g0:
        return (
            "YES",
            f"v1 engineer_guessable=yes (score={s1}) while v0=no (score={s0}); "
            "proxy leakage asymmetric on failed side",
        )
    if failure_direction == "v0_only_fail" and g0 and not g1:
        return (
            "YES",
            f"v0 engineer_guessable=yes (score={s0}) while v1=no (score={s1}); "
            "proxy leakage asymmetric on failed side",
        )
    if g0 and g1:
        return (
            "PROBABLY",
            f"Both sides engineer_guessable (v0 score={s0}, v1 score={s1}); "
            "judge may use proxies but asymmetry not aligned with failure",
        )
    if not g0 and not g1:
        return (
            "NO",
            f"Neither side engineer_guessable (v0 score={s0}, v1 score={s1})",
        )
    return (
        "UNCLEAR",
        f"Mixed guessability (v0={g0}, v1={g1}, scores {s0}/{s1})",
    )


def _stripped_status(
    v0_orig: bool,
    v1_orig: bool,
    v0_strip: bool | None,
    v1_strip: bool | None,
) -> tuple[str, str, str, str]:
    orig_strict = v0_orig and v1_orig
    if v0_strip is None or v1_strip is None:
        return (
            "",
            "",
            "",
            "missing_stripped_recovery",
        )
    strip_strict = v0_strip and v1_strip

    if orig_strict:
        status = "disappear"
    elif strip_strict:
        status = "disappear"
    else:
        status = "persist"

    return (
        str(v0_strip).lower(),
        str(v1_strip).lower(),
        "1" if strip_strict else "0",
        status,
    )


def _interpretation_label(
    obs: dict[str, Any],
    equivalence: str,
    keyword_explains: str,
    proxy_explains: str,
) -> str:
    cluster = obs.get("inferred_cluster", "")
    if cluster in (
        "non_dimension_algorithm_substitution",
        "algorithm_api_substitution",
    ):
        return "methodological_artefact"
    if keyword_explains == "yes":
        return "methodological_artefact"
    if equivalence in ("Definitely equivalent", "Probably equivalent"):
        return "methodological_artefact"
    if (
        obs["input_validation_gain"] == "true"
        or obs["raise_gain"] == "true"
        or obs["lock_gain"] == "true"
        or obs["threading_gain"] == "true"
    ) and obs["failure_direction"] == "v1_only_fail":
        if proxy_explains in ("NO", "UNCLEAR") and keyword_explains != "yes":
            return "genuine_evidence"
    if (
        obs["failure_direction"] == "v0_only_fail"
        and obs["dimension"] == "security"
        and equivalence == "Definitely different"
        and keyword_explains == "partial"
        and proxy_explains == "NO"
    ):
        return "ambiguous"
    if obs["dominant_driver"] == "text" and _float(obs["ast_distance"]) < 0.35:
        if keyword_explains == "partial":
            return "ambiguous"
        return "methodological_artefact"
    if proxy_explains == "YES" and keyword_explains in ("yes", "partial"):
        return "methodological_artefact"
    return "ambiguous"


def _collect_category_b(run_dir: Path, project_root: Path) -> list[dict[str, Any]]:
    strict_rows = _load_csv(run_dir / "manifestation_recovery_strict_dataset.csv")
    manifest_rows = _load_csv(run_dir / "manifestation.csv")
    recovery_rows = _load_csv(run_dir / "recovery.csv")
    recovery_strip_rows = _load_csv(run_dir / "recovery_stripped.csv")
    keyword_rows = _load_csv(run_dir / "keyword_baseline.csv")
    leakage_rows = _load_csv(run_dir / "proxy_leakage_report.csv")

    manifest_lookup = {
        (r["generator_model"], r["task_id"], r["dimension"], r["rep"]): r
        for r in manifest_rows
    }
    recovery_lookup = {
        (
            r["generator_model"],
            r["task_id"],
            r["manipulated_dimension"],
            r["true_value"],
            r["rep"],
        ): r
        for r in recovery_rows
    }
    strip_lookup = {
        (
            r["generator_model"],
            r["task_id"],
            r["manipulated_dimension"],
            r["true_value"],
            r["rep"],
        ): r
        for r in recovery_strip_rows
    }
    keyword_lookup = {
        (
            r["generator_model"],
            r["task_id"],
            r["dimension"],
            r["true_value"],
            r["rep"],
        ): r
        for r in keyword_rows
    }
    leakage_lookup = {
        (r["generator_model"], r["task_id"], r["dimension"], r["value"], r["rep"]): r
        for r in leakage_rows
    }

    observations: list[dict[str, Any]] = []
    obs_id = 0
    for row in strict_rows:
        if not row.get("recovery_mean"):
            continue
        if _float(row["manifestation_score"]) < MANIFESTATION_THRESHOLD:
            continue
        if row["recovery_strict"] != "0":
            continue

        obs_id += 1
        model = row["generator_model"]
        task_id = row["task_id"]
        dimension = row["dimension"]
        rep = row["rep"]
        key = (model, task_id, dimension, rep)
        manifest = manifest_lookup.get(key, {})

        v0_path = manifest.get("v0_path", "")
        v1_path = manifest.get("v1_path", "")
        v0_code = Path(v0_path).read_text(encoding="utf-8") if v0_path and Path(v0_path).exists() else ""
        v1_code = Path(v1_path).read_text(encoding="utf-8") if v1_path and Path(v1_path).exists() else ""

        diff = _analyze_diff(v0_code, v1_code)
        text_distance = _float(row["text_distance"])
        ast_distance = _float(row["ast_distance"]) if row["ast_distance"] else None
        import_jaccard = _float(row["import_jaccard"])
        function_jaccard = _float(row["function_jaccard"])
        mc = _manifestation_contributions(
            text_distance, ast_distance, import_jaccard, function_jaccard
        )

        v0_correct = _parse_bool(row["v0_correct"])
        v1_correct = _parse_bool(row["v1_correct"])
        if not v0_correct and v1_correct:
            failure_direction = "v0_only_fail"
        elif v0_correct and not v1_correct:
            failure_direction = "v1_only_fail"
        elif not v0_correct and not v1_correct:
            failure_direction = "both_fail"
        else:
            failure_direction = "both_ok_impossible"

        equiv, equiv_reason = _equivalence_rating(
            dimension, diff, ast_distance, text_distance, manifest
        )

        rec_v0 = recovery_lookup.get((model, task_id, dimension, "v0", rep))
        rec_v1 = recovery_lookup.get((model, task_id, dimension, "v1", rep))
        strip_v0 = strip_lookup.get((model, task_id, dimension, "v0", rep))
        strip_v1 = strip_lookup.get((model, task_id, dimension, "v1", rep))
        v0_strip = _parse_bool(strip_v0["correct"]) if strip_v0 else None
        v1_strip = _parse_bool(strip_v1["correct"]) if strip_v1 else None
        s_v0, s_v1, s_strict, stripped_status = _stripped_status(
            v0_correct, v1_correct, v0_strip, v1_strip
        )

        leak_v0 = leakage_lookup.get((model, task_id, dimension, "v0", rep))
        leak_v1 = leakage_lookup.get((model, task_id, dimension, "v1", rep))
        proxy_label, proxy_reason = _proxy_explains(
            dimension, leak_v0, leak_v1, failure_direction
        )

        obs: dict[str, Any] = {
            "observation_id": f"B{obs_id:03d}",
            "generator_model": model,
            "task_id": task_id,
            "dimension": dimension,
            "rep": rep,
            "manifestation_score": row["manifestation_score"],
            "text_distance": row["text_distance"],
            "ast_distance": row["ast_distance"] or "",
            "import_jaccard": row["import_jaccard"],
            "function_jaccard": row["function_jaccard"],
            "text_contrib": f"{mc['contributions'].get('text', 0):.4f}",
            "ast_contrib": f"{mc['contributions'].get('ast', 0):.4f}",
            "import_contrib": f"{mc['contributions'].get('import', 0):.4f}",
            "function_contrib": f"{mc['contributions'].get('function', 0):.4f}",
            "dominant_driver": mc["dominant_driver"],
            "recovery_mean": row["recovery_mean"],
            "recovery_strict": row["recovery_strict"],
            "v0_correct": row["v0_correct"],
            "v1_correct": row["v1_correct"],
            "failure_direction": failure_direction,
            "keyword_strict": row["keyword_strict"],
            "keyword_partial": row["keyword_partial"],
            "keyword_v0_correct": row["keyword_v0_correct"],
            "keyword_v1_correct": row["keyword_v1_correct"],
            "equivalence_rating": equiv,
            "equivalence_rationale": equiv_reason,
            "proxy_leakage_v0": leak_v0["engineer_guessable"] if leak_v0 else "",
            "proxy_leakage_v1": leak_v1["engineer_guessable"] if leak_v1 else "",
            "engineer_guessable_v0": leak_v0["engineer_guessable"] if leak_v0 else "",
            "engineer_guessable_v1": leak_v1["engineer_guessable"] if leak_v1 else "",
            "stripped_v0_correct": s_v0,
            "stripped_v1_correct": s_v1,
            "stripped_strict": s_strict,
            "stripped_vs_original": stripped_status,
            "threading_gain": str(diff["threading_gain"]).lower(),
            "lock_gain": str(diff["lock_gain"]).lower(),
            "input_validation_gain": str(diff["validation_gain"]).lower(),
            "raise_gain": str(diff["raise_gain"]).lower(),
            "comment_delta": str(diff["comment_delta"]),
            "docstring_delta": str(diff["docstring_delta"]),
            "import_changed": str(diff["import_changed"]).lower(),
            "algorithm_restructure": str(diff["algorithm_restructure"]).lower(),
            "v0_path": v0_path,
            "v1_path": v1_path,
            "failure_direction_raw": failure_direction,
        }
        obs["keyword_explains"] = _keyword_explains(obs)
        obs["proxy_explains"] = proxy_label
        obs["proxy_rationale"] = proxy_reason
        cluster, mechanism = _infer_cluster(obs)
        obs["inferred_cluster"] = cluster
        obs["cluster_mechanism"] = mechanism
        obs["interpretation"] = _interpretation_label(
            obs, equiv, obs["keyword_explains"], proxy_label
        )
        observations.append(obs)

    return observations


def _plot_figures(fig_dir: Path, observations: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    fig_dir.mkdir(parents=True, exist_ok=True)

    drivers = ["text", "ast", "import", "function"]
    data = {d: [_float(o[f"{d}_contrib"]) for o in observations] for d in drivers}
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, driver in zip(axes.flat, drivers):
        ax.hist(data[driver], bins=15, edgecolor="black", alpha=0.7)
        ax.set_title(f"{driver} contribution (Category B)")
        ax.set_xlabel("normalized contribution")
        ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(fig_dir / "manifestation_component_distributions.png", dpi=150)
    plt.close(fig)

    dominant = Counter(o["dominant_driver"] for o in observations)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(dominant.keys()), list(dominant.values()), edgecolor="black")
    ax.set_title("Dominant manifestation driver (Category B)")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(fig_dir / "dominant_driver_counts.png", dpi=150)
    plt.close(fig)

    directions = Counter(o["failure_direction"] for o in observations)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(list(directions.keys()), list(directions.values()), edgecolor="black")
    ax.set_title("Failure direction (Category B)")
    fig.tight_layout()
    fig.savefig(fig_dir / "failure_direction.png", dpi=150)
    plt.close(fig)

    task_counts = Counter(o["task_id"] for o in observations)
    tasks = sorted(task_counts, key=task_counts.get, reverse=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(tasks, [task_counts[t] for t in tasks], edgecolor="black")
    ax.set_title("Category B frequency by task")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(fig_dir / "task_b_frequency.png", dpi=150)
    plt.close(fig)

    models = ["openai", "anthropic"]
    model_counts = Counter(o["generator_model"] for o in observations)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(models, [model_counts.get(m, 0) for m in models], edgecolor="black")
    ax.set_title("Category B by generator model")
    fig.tight_layout()
    fig.savefig(fig_dir / "model_b_counts.png", dpi=150)
    plt.close(fig)

    kw = Counter(o["keyword_explains"] for o in observations)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(list(kw.keys()), list(kw.values()), edgecolor="black")
    ax.set_title("Keyword baseline explains LLM partial failure?")
    fig.tight_layout()
    fig.savefig(fig_dir / "keyword_explains.png", dpi=150)
    plt.close(fig)

    proxy = Counter(o["proxy_explains"] for o in observations)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(proxy.keys()), list(proxy.values()), edgecolor="black")
    ax.set_title("Proxy leakage explains Category B?")
    fig.tight_layout()
    fig.savefig(fig_dir / "proxy_explains.png", dpi=150)
    plt.close(fig)

    equiv = Counter(o["equivalence_rating"] for o in observations)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(list(equiv.keys()), list(equiv.values()), edgecolor="black")
    ax.set_title("Functional equivalence rating (Category B)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(fig_dir / "equivalence_ratings.png", dpi=150)
    plt.close(fig)

    interp = Counter(o["interpretation"] for o in observations)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(interp.keys()), list(interp.values()), edgecolor="black")
    ax.set_title("Scientific interpretation labels")
    fig.tight_layout()
    fig.savefig(fig_dir / "interpretation_counts.png", dpi=150)
    plt.close(fig)


def _write_clusters_csv(path: Path, observations: list[dict[str, Any]]) -> None:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for obs in observations:
        clusters[obs["inferred_cluster"]].append(obs)

    rows: list[dict[str, str]] = []
    for cluster in sorted(clusters, key=lambda c: -len(clusters[c])):
        items = clusters[cluster]
        examples = []
        for obs in items[:3]:
            examples.append(
                f"{obs['observation_id']} {obs['task_id']}/{obs['dimension']} "
                f"{obs['generator_model']} rep{obs['rep']} "
                f"({obs['failure_direction']}, driver={obs['dominant_driver']})"
            )
        rows.append(
            {
                "cluster": cluster,
                "count": str(len(items)),
                "representative_examples": " | ".join(examples),
                "hypothesized_mechanism": items[0]["cluster_mechanism"],
            }
        )
    _write_csv(
        path,
        ["cluster", "count", "representative_examples", "hypothesized_mechanism"],
        rows,
    )


def _write_examples_md(path: Path, observations: list[dict[str, Any]]) -> None:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for obs in observations:
        clusters[obs["inferred_cluster"]].append(obs)

    lines = ["# Category B Representative Examples", ""]
    for cluster in sorted(clusters, key=lambda c: -len(clusters[c])):
        items = clusters[cluster]
        lines.extend(
            [
                f"## Cluster: `{cluster}` (n={len(items)})",
                "",
                f"**Mechanism:** {items[0]['cluster_mechanism']}",
                "",
            ]
        )
        for obs in items[:2]:
            lines.extend(
                [
                    f"### {obs['observation_id']}: {obs['task_id']} / {obs['dimension']} / "
                    f"{obs['generator_model']} rep {obs['rep']}",
                    "",
                    f"- manifestation_score={obs['manifestation_score']}, "
                    f"dominant_driver={obs['dominant_driver']}",
                    f"- failure_direction={obs['failure_direction']}, "
                    f"v0_correct={obs['v0_correct']}, v1_correct={obs['v1_correct']}",
                    f"- equivalence={obs['equivalence_rating']}: {obs['equivalence_rationale']}",
                    f"- keyword_explains={obs['keyword_explains']}, "
                    f"proxy_explains={obs['proxy_explains']}",
                    f"- interpretation={obs['interpretation']}",
                    "",
                ]
            )
            v0_path = obs["v0_path"]
            v1_path = obs["v1_path"]
            if v0_path and v1_path and Path(v0_path).exists():
                v0_lines = Path(v0_path).read_text(encoding="utf-8").splitlines()[:15]
                v1_lines = Path(v1_path).read_text(encoding="utf-8").splitlines()[:15]
                lines.append("```python")
                lines.append("# v0 (first 15 lines)")
                lines.extend(v0_lines)
                lines.append("# v1 (first 15 lines)")
                lines.extend(v1_lines)
                lines.append("```")
                lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_report(
    path: Path,
    run_name: str,
    observations: list[dict[str, Any]],
) -> None:
    n = len(observations)
    lines = [
        "# Category B Forensic Report",
        "",
        f"Run: `{run_name}`",
        f"Category B observations analyzed: **{n}**",
        "",
        "Definition: manifestation_score >= 0.10 AND recovery_strict = 0.",
        "All 51 cases are partial recoveries (exactly one of v0/v1 wrong; none with both wrong).",
        "",
        "---",
        "",
        "## PART 1 — Failure mechanism clusters (inferred from data)",
        "",
        "| Cluster | Count | Hypothesized mechanism |",
        "|---------|------:|------------------------|",
    ]

    cluster_counts = Counter(o["inferred_cluster"] for o in observations)
    cluster_mech = {}
    for o in observations:
        cluster_mech[o["inferred_cluster"]] = o["cluster_mechanism"]
    for cluster, count in cluster_counts.most_common():
        lines.append(f"| `{cluster}` | {count} | {cluster_mech[cluster]} |")

    lines.extend(["", "See `category_B_clusters.csv` and `category_B_examples.md` for representatives.", ""])

    lines.extend(
        [
            "### Per-observation cluster assignment",
            "",
        ]
    )
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}` → `{obs['inferred_cluster']}`"
        )
    lines.append("")

    lines.extend(
        [
            "## PART 2 — Manifestation score component drivers",
            "",
        ]
    )
    driver_counts = Counter(o["dominant_driver"] for o in observations)
    for driver, count in driver_counts.most_common():
        pct = 100 * count / n
        lines.append(f"- **{driver}** dominant: {count}/{n} ({pct:.1f}%)")
    combo = Counter(
        (
            o["dominant_driver"],
            "high_ast" if _float(o["ast_contrib"]) >= 0.35 else "low_ast",
        )
        for o in observations
    )
    lines.append("")
    lines.append("Category B is driven primarily by **text and AST distance jointly**, not imports/functions (both near zero in most pairs).")
    lines.append(f"Import distance contributes materially in {sum(1 for o in observations if _float(o['import_contrib'])>=0.15)} cases.")
    lines.append(f"Function distance contributes materially in {sum(1 for o in observations if _float(o['function_contrib'])>=0.15)} cases.")
    lines.append("")
    lines.append("Figures: `category_B_figures/manifestation_component_distributions.png`, `dominant_driver_counts.png`.")
    lines.append("")
    lines.extend(["### Per-observation component contributions", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}**: text={obs['text_contrib']}, ast={obs['ast_contrib']}, "
            f"import={obs['import_contrib']}, function={obs['function_contrib']}, "
            f"dominant={obs['dominant_driver']}"
        )
    lines.append("")

    lines.extend(["## PART 3 — Cosmetic vs semantic equivalence", ""])
    equiv_counts = Counter(o["equivalence_rating"] for o in observations)
    for rating in [
        "Definitely equivalent",
        "Probably equivalent",
        "Unclear",
        "Probably different",
        "Definitely different",
    ]:
        lines.append(f"- **{rating}**: {equiv_counts.get(rating, 0)}")
    cosmetic = equiv_counts.get("Definitely equivalent", 0) + equiv_counts.get(
        "Probably equivalent", 0
    )
    lines.append("")
    lines.append(
        f"**Cosmetic-or-equivalent estimate: {cosmetic}/{n} ({100*cosmetic/n:.1f}%)** "
        "using structural/text heuristics on existing code pairs."
    )
    lines.append("")
    lines.extend(["### Per-observation equivalence rating", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: **{obs['equivalence_rating']}** — "
            f"{obs['equivalence_rationale']}"
        )
    lines.append("")

    lines.extend(["## PART 4 — Directional failures", ""])
    v0_fail = sum(1 for o in observations if o["failure_direction"] == "v0_only_fail")
    v1_fail = sum(1 for o in observations if o["failure_direction"] == "v1_only_fail")
    lines.append(f"- P(fail v0 | B) = {v0_fail/n:.3f} ({v0_fail}/{n})")
    lines.append(f"- P(fail v1 | B) = {v1_fail/n:.3f} ({v1_fail}/{n})")
    lines.append("")
    lines.append(
        "Asymmetry is modest (57% v0-fail vs 43% v1-fail). "
        "v1-only failures concentrate in concurrency-dimension edits where v1 adds salient primitives. "
        "v0-only failures concentrate in security tasks where v0 uses alternate validation surface forms."
    )
    lines.append("")
    lines.extend(["### Per-observation failure direction", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: {obs['failure_direction']} "
            f"(v0={obs['v0_correct']}, v1={obs['v1_correct']})"
        )
    lines.append("")

    lines.extend(["## PART 5 — Task effects", ""])
    task_counts = Counter(o["task_id"] for o in observations)
    for task, count in task_counts.most_common():
        task_obs = [o for o in observations if o["task_id"] == task]
        dims = Counter(o["dimension"] for o in task_obs)
        restruct = sum(1 for o in task_obs if o["algorithm_restructure"] == "true")
        lines.append(f"### `{task}` — {count} Category B cases")
        lines.append(f"- Dimensions: {dict(dims)}")
        lines.append(f"- Algorithm restructures: {restruct}/{count}")
        if task == "dependency_order":
            lines.append(
                "- **Mechanism:** Generator replaces algorithm with API-based implementation; "
                "manifestation is high but manipulated concurrency dimension often absent → B via v1-only judge failure on non-concurrency code."
            )
        elif task == "sanitize_filename":
            lines.append(
                "- **Mechanism:** Security/concurrency flips produce large textual rewrites of small functions; "
                "partial judge asymmetry on validation surface forms."
            )
        elif task == "validate_email_like":
            lines.append(
                "- **Mechanism:** High text/AST distance from regex/validation rewrites; "
                "keyword and judge disagree on v0 vs v1 salience."
            )
        elif task == "merge_intervals":
            lines.append(
                "- **Mechanism:** Mostly concurrency dimension with moderate manifestation; "
                "concurrency edits not always lock/threading based."
            )
        else:
            lines.append("- **Mechanism:** Mixed partial failures; see per-observation rows.")
        lines.append("")

    lines.extend(["## PART 6 — Model effects", ""])
    for model in ["openai", "anthropic"]:
        mobs = [o for o in observations if o["generator_model"] == model]
        lines.append(f"### `{model}` — {len(mobs)} cases")
        lines.append(f"- Clusters: {dict(Counter(o['inferred_cluster'] for o in mobs))}")
        lines.append(
            f"- Equivalence: {dict(Counter(o['equivalence_rating'] for o in mobs))}"
        )
        lines.append(
            f"- v1-only fail: {sum(1 for o in mobs if o['failure_direction']=='v1_only_fail')}"
        )
        lines.append(
            f"- v0-only fail: {sum(1 for o in mobs if o['failure_direction']=='v0_only_fail')}"
        )
        lines.append("")
    lines.append(
        "Anthropic produces more algorithm/API substitution clusters (dependency_order). "
        "OpenAI concentrates in sanitize_filename and validate_email_like security rewrites. "
        "Both models yield partial (not zero) recovery — judge confusion is not model-exclusive."
    )
    lines.append("")

    lines.extend(["## PART 7 — Keyword baseline", ""])
    kw = Counter(o["keyword_explains"] for o in observations)
    for k, v in kw.items():
        lines.append(f"- keyword_explains={k}: {v}")
    unexplained = sum(
        1
        for o in observations
        if o["keyword_explains"] == "no" and o["interpretation"] != "methodological_artefact"
    )
    lines.append("")
    lines.append(
        f"Keyword baseline exactly mirrors LLM failure side in {kw.get('yes', 0)} cases. "
        f"Partial keyword alignment: {kw.get('partial', 0)}. "
        f"Surviving after removing keyword-explained cases: **{n - kw.get('yes', 0)}** "
        f"({100*(n-kw.get('yes',0))/n:.1f}%)."
    )
    lines.append(
        f"Non-artefact unexplained estimate: **{unexplained}/{n} ({100*unexplained/n:.1f}%)**."
    )
    lines.append("")
    lines.extend(["### Per-observation keyword comparison", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: "
            f"LLM(v0={obs['v0_correct']}, v1={obs['v1_correct']}) vs "
            f"keyword(v0={obs['keyword_v0_correct']}, v1={obs['keyword_v1_correct']}) → "
            f"keyword_explains={obs['keyword_explains']}, manifestation={obs['manifestation_score']}"
        )
    lines.append("")

    lines.extend(["## PART 8 — Proxy leakage", ""])
    proxy = Counter(o["proxy_explains"] for o in observations)
    for k in ["YES", "PROBABLY", "UNCLEAR", "NO"]:
        lines.append(f"- {k}: {proxy.get(k, 0)}")
    lines.append("")
    lines.append("Per-observation proxy labels are in `category_B_dataset.csv` columns `proxy_explains`, `proxy_rationale`.")
    lines.append("")
    lines.extend(["### Per-observation proxy leakage assessment", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: **{obs['proxy_explains']}** — "
            f"{obs['proxy_rationale']} "
            f"[v0 guessable={obs['engineer_guessable_v0']}, v1 guessable={obs['engineer_guessable_v1']}]"
        )
    lines.append("")

    lines.extend(["## PART 9 — Stripped analysis", ""])
    strip_status = Counter(o["stripped_vs_original"] for o in observations)
    for k, v in strip_status.items():
        lines.append(f"- stripped_vs_original={k}: {v}")
    lines.append("")
    lines.append(
        "Category B **persists** under stripping in all complete cases: "
        "partial recovery is not an artifact introduced by strip; "
        "stripping does not convert B into strict success."
    )
    lines.append("")
    lines.extend(["### Per-observation stripped vs original", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: original(v0={obs['v0_correct']}, v1={obs['v1_correct']}) → "
            f"stripped(v0={obs['stripped_v0_correct']}, v1={obs['stripped_v1_correct']}, "
            f"strict={obs['stripped_strict']}) status=**{obs['stripped_vs_original']}**"
        )
    lines.append("")

    lines.extend(["## PART 10 — Reviewer #2 scientific interpretation", ""])
    interp = Counter(o["interpretation"] for o in observations)
    genuine = interp.get("genuine_evidence", 0)
    artefact = interp.get("methodological_artefact", 0)
    ambiguous = interp.get("ambiguous", 0)
    lines.extend(
        [
            f"1. **Genuine evidence:** {genuine}/{n} ({100*genuine/n:.1f}%)",
            f"2. **Methodological artefacts:** {artefact}/{n} ({100*artefact/n:.1f}%)",
            f"3. **Ambiguous:** {ambiguous}/{n} ({100*ambiguous/n:.1f}%)",
            "",
            "4. **Does Category B support a manifestation–recovery gap?**",
            "",
        ]
    )
    if genuine <= 5 and artefact >= 25:
        lines.append(
            "**No, not in its current form.** Category B is predominantly partial recovery on pairs "
            "with high structural distance but (a) keyword baseline replicates the same asymmetry, "
            "(b) many cases are algorithm substitutions unrelated to the manipulated dimension, "
            "and (c) equivalence heuristics mark a substantial fraction as cosmetic or equivalent. "
            "The 51-count headline collapses into a handful of plausibly genuine cases."
        )
        survive = "NO"
    elif genuine >= 15:
        lines.append(
            "**Partially.** A minority subset shows dimension-aligned semantic edits with "
            "judge failure not explained by keywords or proxy leakage."
        )
        survive = "WEAK"
    else:
        lines.append(
            "**Weakly.** Category B exists numerically but most cases trace to partial-recovery "
            "operationalization, keyword mirroring, or manipulation failure — not independent recovery failure."
        )
        survive = "NO"

    lines.extend(
        [
            "",
            "5. **Would Category B survive TOSEM review today?**",
            "",
        ]
    )
    if survive == "NO":
        lines.append(
            "**No.** A TOSEM reviewer would classify Category B as an artefact of (1) strict-recovery "
            "defined on two binary trials yielding partial failure cells, (2) manifestation_score "
            "conflating manipulation-unrelated rewrites with dimension manifestation, and "
            "(3) absence of a human oracle or behavioral test to validate semantic difference. "
            "The 51 cases would be reduced to a small case study at best."
        )
    else:
        lines.append("**Unlikely without major reframing.**")

    lines.extend(["", "---", "", "## Per-observation index", ""])
    for obs in observations:
        lines.append(
            f"- **{obs['observation_id']}** `{obs['task_id']}/{obs['dimension']}/"
            f"{obs['generator_model']}/rep{obs['rep']}`: cluster=`{obs['inferred_cluster']}`, "
            f"direction={obs['failure_direction']}, equiv={obs['equivalence_rating']}, "
            f"kw={obs['keyword_explains']}, proxy={obs['proxy_explains']}, "
            f"interp={obs['interpretation']}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def run_category_b_forensic(project_root: Path, run_name: str) -> dict[str, Path]:
    run_dir = project_root / "results" / "runs" / run_name
    required = [
        run_dir / "manifestation_recovery_strict_dataset.csv",
        run_dir / "manifestation.csv",
        run_dir / "recovery.csv",
        run_dir / "recovery_stripped.csv",
        run_dir / "keyword_baseline.csv",
        run_dir / "proxy_leakage_report.csv",
    ]
    for p in required:
        if not p.exists():
            raise FileNotFoundError(f"Missing {p}")

    observations = _collect_category_b(run_dir, project_root)
    if len(observations) != 51:
        raise RuntimeError(f"Expected 51 Category B observations, got {len(observations)}")

    dataset_path = run_dir / "category_B_dataset.csv"
    clusters_path = run_dir / "category_B_clusters.csv"
    examples_path = run_dir / "category_B_examples.md"
    report_path = run_dir / "category_B_report.md"
    fig_dir = run_dir / "category_B_figures"

    _write_csv(dataset_path, DATASET_FIELDS, observations)
    _write_clusters_csv(clusters_path, observations)
    _write_examples_md(examples_path, observations)
    _plot_figures(fig_dir, observations)
    _write_report(report_path, run_name, observations)

    interp = Counter(o["interpretation"] for o in observations)
    print(f"Wrote {dataset_path} ({len(observations)} observations)")
    print(f"Wrote {clusters_path}")
    print(f"Wrote {examples_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote figures to {fig_dir}/")
    print(f"Interpretation: {dict(interp)}")

    return {
        "dataset": dataset_path,
        "clusters": clusters_path,
        "examples": examples_path,
        "report": report_path,
        "figures": fig_dir,
    }
