from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from invert_discovery.latent_process_risk.eps.opcodes import (
    OPCODE_CATEGORY_SLOTS,
    category_index,
    opcode_to_category,
)
from invert_discovery.latent_process_risk.types import ProgramInput, PublicRun, reject_label_kwargs


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _jsd(p: list[float], q: list[float]) -> float:
    eps = 1e-12
    m = [(a + b) / 2 for a, b in zip(p, q, strict=True)]
    s = 0.0
    for pi, qi, mi in zip(p, q, m, strict=True):
        if pi > eps:
            s += pi * math.log2(pi / mi)
        if qi > eps:
            s += qi * math.log2(qi / mi)
    return math.sqrt(max(0.0, 0.5 * s))


@dataclass(frozen=True)
class EPSVector:
    P1: tuple[str, ...]
    P2: float
    P3: float
    P4: tuple[float, float, float]
    P5: float
    P6: float
    P7: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "P1": list(self.P1),
            "P2": self.P2,
            "P3": self.P3,
            "P4": list(self.P4),
            "P5": self.P5,
            "P6": self.P6,
            "P7": list(self.P7),
        }


class EPSExtractor:
    """Frozen EPS dimensions P1–P7 per EPS_SPECIFICATION.md."""

    REPEAT_COUNT = 3
    P1_BINS = 8

    def __init__(self, pool_medians: dict[str, tuple[float, ...]] | None = None) -> None:
        self._pool_medians = pool_medians or {}

    def extract(self, program: ProgramInput, **kwargs: Any) -> EPSVector:
        reject_label_kwargs(kwargs)
        runs_by_test: dict[int, list[PublicRun]] = defaultdict(list)
        for run in program.public_runs:
            runs_by_test[run.test_index].append(run)

        p1_hashes: list[str] = []
        p2_vals: list[float] = []
        p3_vals: list[float] = []
        p4_rows: list[tuple[float, float, float]] = []
        micro_sigs: list[str] = []

        for test_idx in sorted(runs_by_test):
            runs = sorted(runs_by_test[test_idx], key=lambda r: r.repeat_index)
            outputs = [_sha256_text(r.output) for r in runs]
            if runs:
                p1_hashes.append(outputs[0])
            mode = Counter(outputs).most_common(1)[0][0]
            p2_vals.append(sum(1 for h in outputs if h != mode) / max(1, len(outputs)))

            pmfs: list[list[float]] = []
            for run in runs:
                pmfs.append(self._opcode_pmf(run))
            if len(pmfs) >= 2:
                pair_jsd = []
                for i in range(len(pmfs)):
                    for j in range(i + 1, len(pmfs)):
                        pair_jsd.append(_jsd(pmfs[i], pmfs[j]))
                p3_vals.append(sum(pair_jsd) / len(pair_jsd))
            else:
                p3_vals.append(0.0)

            wall = sorted(r.wall_time for r in runs)
            cpu = sorted(r.cpu_time for r in runs)
            rss = sorted(float(r.peak_rss) for r in runs)
            med = len(wall) // 2
            p4_rows.append((wall[med], cpu[med], rss[med]))

            if runs:
                r0 = runs[0]
                micro = _sha256_text(f"{self._opcode_pmf(r0)!s}:{r0.wall_time}:{r0.peak_rss}")
                micro_sigs.append(micro)

        p4 = self._coefficient_of_variation([row[0] for row in p4_rows]), self._coefficient_of_variation(
            [row[1] for row in p4_rows]
        ), self._coefficient_of_variation([row[2] for row in p4_rows])

        p5 = self._entropy(Counter(micro_sigs))
        p7 = self._aggregate_opcode_pmf(program.public_runs)
        p2 = sum(p2_vals) / max(1, len(p2_vals))
        p3 = sum(p3_vals) / max(1, len(p3_vals))
        p6 = self._stereotypy(program.program_id, p2, p3, p4, p5, p7)

        return EPSVector(
            P1=tuple(p1_hashes),
            P2=p2,
            P3=p3,
            P4=p4,
            P5=p5,
            P6=p6,
            P7=tuple(p7),
        )

    def _opcode_pmf(self, run: PublicRun) -> list[float]:
        counts = [0.0] * len(OPCODE_CATEGORY_SLOTS)
        for name, cnt in run.opcode_counts:
            counts[category_index(opcode_to_category(name))] += float(cnt)
        total = sum(counts) or 1.0
        return [c / total for c in counts]

    def _aggregate_opcode_pmf(self, runs: tuple[PublicRun, ...]) -> list[float]:
        counts = [0.0] * len(OPCODE_CATEGORY_SLOTS)
        for run in runs:
            for name, cnt in run.opcode_counts:
                counts[category_index(opcode_to_category(name))] += float(cnt)
        total = sum(counts) or 1.0
        return [c / total for c in counts]

    @staticmethod
    def _coefficient_of_variation(values: list[float]) -> float:
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        if mean < 1e-9:
            return 0.0
        var = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(var) / mean

    @staticmethod
    def _entropy(counter: Counter[str]) -> float:
        total = sum(counter.values())
        if total == 0:
            return 0.0
        ent = 0.0
        for c in counter.values():
            p = c / total
            ent -= p * math.log2(p)
        return ent

    def _stereotypy(
        self,
        program_id: str,
        p2: float,
        p3: float,
        p4: tuple[float, float, float],
        p5: float,
        p7: list[float],
    ) -> float:
        med = self._pool_medians.get(program_id)
        vec = (p2, p3, *p4, p5, *p7[:8])
        if med is None:
            return 0.0
        n = min(len(vec), len(med))
        return math.sqrt(sum((vec[i] - med[i]) ** 2 for i in range(n)))
