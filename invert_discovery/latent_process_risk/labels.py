from __future__ import annotations

from invert_discovery.latent_process_risk.types import LabelRecord, LabelStatus


def build_label(
    *,
    public_pass: bool,
    withheld_pass: bool,
    timed_out: bool = False,
    syntax_error: bool = False,
    execution_error: bool = False,
) -> LabelRecord:
    if syntax_error:
        return LabelRecord(False, False, LabelStatus.SYNTAX_ERROR)
    if timed_out:
        return LabelRecord(False, False, LabelStatus.TIMEOUT)
    if execution_error:
        return LabelRecord(False, False, LabelStatus.EXECUTION_ERROR)
    if not public_pass:
        return LabelRecord(False, withheld_pass, LabelStatus.OUTRIGHT_FAIL)
    if withheld_pass:
        return LabelRecord(True, True, LabelStatus.PUBLIC_PASS_HIDDEN_PASS)
    return LabelRecord(True, False, LabelStatus.PUBLIC_PASS_HIDDEN_FAIL)
