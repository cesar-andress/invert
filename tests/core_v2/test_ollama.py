from __future__ import annotations

from unittest.mock import patch

import pytest

from invert_core.check_apis import run_check_apis
from invert_core.models import (
    OllamaClient,
    check_ollama_model,
    sanitize_model_for_storage,
)
from invert_core.pilot_config import CoreV2PilotConfig, plan_core_v2_generations
from invert_core.tasks import project_root


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("ollama:qwen2.5-coder:32b", "ollama__qwen2_5-coder__32b"),
        ("ollama:qwen3-coder:30b", "ollama__qwen3-coder__30b"),
        ("ollama:qwen2.5-coder:14b", "ollama__qwen2_5-coder__14b"),
        ("ollama:devstral:latest", "ollama__devstral__latest"),
        ("ollama:deepseek-coder-v2:lite", "ollama__deepseek-coder-v2__lite"),
        ("openai", "openai"),
    ],
)
def test_sanitize_model_for_storage(spec: str, expected: str) -> None:
    assert sanitize_model_for_storage(spec) == expected


def test_ollama_paths_use_sanitized_names() -> None:
    pilot = CoreV2PilotConfig.from_yaml(
        project_root() / "configs" / "core_v2_euler_rk4_pilot_local.yaml",
        project_root(),
    )
    items = plan_core_v2_generations(pilot, pilot.load_tasks())
    item = next(i for i in items if i.model == "ollama:qwen2.5-coder:32b")
    assert "ollama__qwen2_5-coder__32b" in str(item.code_path(pilot.data_root))


@patch("invert_core.models._ollama_request")
def test_check_ollama_model_available(mock_request) -> None:
    mock_request.return_value = {
        "models": [
            {"name": "qwen2.5-coder:32b"},
            {"name": "deepseek-coder-v2:lite"},
        ]
    }
    ok, detail = check_ollama_model("ollama:qwen2.5-coder:32b")
    assert ok
    assert "available" in detail
    mock_request.assert_called_once()


@patch("invert_core.models._ollama_request")
def test_check_ollama_model_missing(mock_request) -> None:
    mock_request.return_value = {"models": [{"name": "other:latest"}]}
    ok, detail = check_ollama_model("ollama:qwen2.5-coder:32b")
    assert not ok
    assert "not found" in detail


@patch("invert_core.models._ollama_request")
def test_run_check_apis_ollama_enforced(mock_request, capsys) -> None:
    mock_request.return_value = {
        "models": [
            {"name": "qwen2.5-coder:32b"},
            {"name": "deepseek-coder-v2:lite"},
        ]
    }
    code = run_check_apis(
        ["ollama:qwen2.5-coder:32b", "ollama:deepseek-coder-v2:lite"],
        strict=False,
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "ollama:qwen2.5-coder:32b: ok" in out


@patch("invert_core.models._ollama_request")
def test_ollama_client_generate(mock_request) -> None:
    mock_request.return_value = {"response": "def integrate_ode(f, y0, t0, tf, dt):\n    return y0\n"}
    client = OllamaClient(model="qwen2.5-coder:32b", temperature=0, generate_timeout=900)
    text = client.generate("prompt")
    assert "integrate_ode" in text
    assert mock_request.call_args[0][1] == "/api/generate"
    assert mock_request.call_args[1]["timeout"] == 900
    payload = mock_request.call_args[1]["payload"]
    assert payload["model"] == "qwen2.5-coder:32b"
    assert payload["stream"] is False
    assert payload["options"]["temperature"] == 0


@patch("invert_core.models._ollama_request")
def test_ollama_generate_retries_on_timeout(mock_request) -> None:
    mock_request.side_effect = [TimeoutError("timed out"), {"response": "ok"}]
    client = OllamaClient(model="deepseek-coder-v2:lite", max_retries=2, generate_timeout=60)
    assert client.generate("prompt") == "ok"
    assert mock_request.call_count == 2


def test_local_pilot_dry_run_expected_generations(capsys) -> None:
    from invert_core.generate import run_core_v2_generation

    pilot = CoreV2PilotConfig.from_yaml(
        project_root() / "configs" / "core_v2_euler_rk4_pilot_local.yaml",
        project_root(),
    )
    run_core_v2_generation(pilot, dry_run=True)
    out = capsys.readouterr().out
    assert "Total expected generations: 36" in out
    assert "ollama__qwen2_5-coder__32b" in out
