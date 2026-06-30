# LPR Implementation Smoke Report

**Decision:** GO
**BASELINE_LOCK commit:** `b80cc321628ca03865d26df8c4e51c6555a00b8a`

## Criteria

- baseline_lock_present: True
- toy_fixtures_deterministic: True
- split_deterministic: True
- no_invert_import_in_lpr_module: True
- label_separation_ok: True

## Fixture results

- public_pass_hidden_pass: {'fixture': 'public_pass_hidden_pass', 'label_status': 'public_pass_hidden_pass', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': 0.0, 'baseline_size_dim': 7}
- public_pass_hidden_fail: {'fixture': 'public_pass_hidden_fail', 'label_status': 'public_pass_hidden_fail', 'latent_incorrect': True, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': 0.0, 'baseline_size_dim': 7}
- public_fail: {'fixture': 'public_fail', 'label_status': 'outright_fail', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': 0.0, 'baseline_size_dim': 7}
- timeout: {'fixture': 'timeout', 'label_status': 'timeout', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': None, 'baseline_size_dim': 0}
- syntax_error: {'fixture': 'syntax_error', 'label_status': 'syntax_error', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': None, 'baseline_size_dim': 0}
- deterministic_execution: {'fixture': 'deterministic_execution', 'label_status': 'public_pass_hidden_pass', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': 0.0, 'baseline_size_dim': 7}
- unstable_execution: {'fixture': 'unstable_execution', 'label_status': 'public_pass_hidden_pass', 'latent_incorrect': False, 'eps_ok': True, 'baseline_ok': True, 'eps_P2': 0.3333333333333333, 'baseline_size_dim': 7}
