from __future__ import annotations

from invert_core.check_apis import run_check_apis


def test_check_apis_non_strict_exits_zero(capsys) -> None:
    assert run_check_apis(["openai", "anthropic"], strict=False) == 0
    out = capsys.readouterr().out
    assert "openai:" in out
    assert "anthropic:" in out
