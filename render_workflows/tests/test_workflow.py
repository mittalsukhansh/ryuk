"""Isolated Render adapter checks; never invoke Render, PayPal, models or existing ledgers."""

import ast
import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from render_workflows.logic import verify_catalog

ROOT = Path(__file__).resolve().parents[2]


def intent():
    return json.loads((ROOT / "render_workflows/demo-input.json").read_text())


def test_existing_verifier_returns_same_currency_canonical_synthetic_offers_without_network(
    monkeypatch,
):
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("No network in verification task")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    report = verify_catalog(intent())
    assert report["synthetic"] and report["advisory_only"]
    assert len(report["offers"]) == 6
    assert all(
        "verification_snapshot_id" in row["verification"] for row in report["offers"]
    )
    assert {row["verification"]["status"] for row in report["offers"]} >= {
        "PASS",
        "FAIL",
    }
    assert not {"payment", "policy", "approval", "capture"} & report.keys()


@pytest.mark.parametrize(
    "change", [{"user_id": "forged"}, {"budget_max_minor": 1.5}, {"currency": ""}]
)
def test_untrusted_extra_authority_and_invalid_intent_rejected(change):
    with pytest.raises(ValidationError):
        verify_catalog({**intent(), **change})


def test_input_bound_and_fresh_results():
    with pytest.raises(ValueError, match="too large"):
        verify_catalog({"query": "x" * 16385})
    first = verify_catalog(intent())
    first["offers"].clear()
    assert len(verify_catalog(intent())["offers"]) == 6


def test_task_has_no_payment_authority_or_ledger_imports():
    forbidden = {
        "app.services.checkout",
        "app.services.checkout_store",
        "app.services.paypal",
        "app.services.approvals",
        "app.services.provisioning",
        "app.services.policy",
    }
    for filename in ["logic.py", "main.py"]:
        tree = ast.parse((ROOT / "render_workflows" / filename).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module not in forbidden
    import render_workflows.main as module

    assert (
        module.app is not None
    )  # Real pinned SDK registers without starting network execution.


def test_blueprint_separates_private_authority_and_credential_free_workflow():
    config = yaml.safe_load((ROOT / "render.yaml").read_text())
    services = config["services"]
    assert len(services) == 4
    public = [s for s in services if s["type"] == "web"]
    assert (
        len(public) == 1 and public[0]["dockerfilePath"] == "deploy/render/Dockerfile"
    )
    backend = next(s for s in services if s["name"].endswith("backend"))
    assert backend["type"] == "pserv" and backend["disk"]["mountPath"] == "/app/data"
    workflow = next(s for s in services if s["type"] == "workflow")
    assert "disk" not in workflow
    assert all(
        not e["key"].startswith(("PAYPAL_", "GROQ_", "OPENAI_", "RYUK_"))
        for e in workflow["envVars"]
    )
    assert all(s["autoDeployTrigger"] == "off" for s in services)


def test_operator_demo_dispatches_only_public_fixture_data(monkeypatch, capsys):
    from types import SimpleNamespace

    from render_workflows import run_demo

    calls = []

    class Client:
        workflows = None

        def __init__(self):
            self.workflows = self

        def start_task(self, slug, args):
            calls.append((slug, args))
            return SimpleNamespace(id="trn-synthetic")

    monkeypatch.setattr(run_demo, "Render", Client)
    monkeypatch.setenv("RENDER_API_KEY", "synthetic-test-only-not-a-real-key")
    monkeypatch.setattr("sys.argv", ["run_demo", "workflow/verify_catalog"])
    run_demo.main()
    assert calls == [("workflow/verify_catalog", [intent()])]
    assert json.loads(capsys.readouterr().out)["run_id"] == "trn-synthetic"


def test_operator_demo_error_does_not_reflect_credentials(monkeypatch, capsys):
    from render_workflows import run_demo

    def unavailable():
        raise ValueError("synthetic-secret-must-not-be-reflected")

    monkeypatch.setattr(run_demo, "Render", unavailable)
    monkeypatch.setenv("RENDER_API_KEY", "synthetic-test-only-not-a-real-key")
    monkeypatch.setattr("sys.argv", ["run_demo", "workflow/verify_catalog"])
    with pytest.raises(SystemExit):
        run_demo.main()
    assert "synthetic-secret-must-not-be-reflected" not in capsys.readouterr().err
