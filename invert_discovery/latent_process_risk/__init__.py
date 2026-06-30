"""Latent Process Risk (LPR) — independent study module.

See results/research_extension/LPR/ for frozen protocols.
Must not import invert_core or INVERT detectors.
"""

from invert_discovery.latent_process_risk.paths import lpr_results_dir, project_root

__all__ = ["lpr_results_dir", "project_root"]
