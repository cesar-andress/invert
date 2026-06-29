from __future__ import annotations

from invert_core.check_apis import check_core_api_keys, run_check_apis


def test_check_apis_non_strict_exits_zero(capsys) -> None:
    assert run_check_apis(["openai", "anthropic"], strict=False) == 0
    out = capsys.readouterr().out
    assert "openai:" in out
    assert "anthropic:" in out


def test_check_core_api_keys_cloud_only() -> None:
    results, _details = check_core_api_keys(["local_stub"])
    assert results["local_stub"] is True
