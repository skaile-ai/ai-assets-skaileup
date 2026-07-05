"""Tests for the dedup guards in contracts/scripts/verify_artifacts.py."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_artifacts.py"
spec = importlib.util.spec_from_file_location("verify_artifacts", SCRIPT)
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)


def test_normalize_lowercases_and_strips_punctuation():
    assert va._normalize("MUST sort  all manifest arrays, lexicographically!") == [
        "must", "sort", "all", "manifest", "arrays", "lexicographically"]


def test_ngrams_sliding_window():
    toks = list("abcdefghij")  # 10 tokens → 3 8-grams
    grams = va._ngrams(toks, 8)
    assert ("a", "b", "c", "d", "e", "f", "g", "h") in grams
    assert len(grams) == 3


def _fake_contracts(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "demo_contract.md").write_text(
        "Renderers must sort all manifest arrays lexicographically "
        "for deterministic diffs across regeneration runs.\n")
    return contracts


def test_restatement_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(va, "CONTRACTS_DIR", _fake_contracts(tmp_path))
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST sort all manifest arrays lexicographically for deterministic "
        "diffs across regeneration runs\n")
    errors = []
    va.check_restatements([skill], errors)
    assert len(errors) == 1
    assert "restate" in errors[0] and "SKILL.md:1" in errors[0]


def test_short_citation_not_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(va, "CONTRACTS_DIR", _fake_contracts(tmp_path))
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST sort manifest arrays (contracts/walkthrough_renderer.md "
        "§ Shared MUST / NEVER)\n")
    errors = []
    va.check_restatements([skill], errors)
    assert errors == []


def test_code_blocks_in_contracts_excluded(tmp_path, monkeypatch):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "demo_contract.md").write_text(
        "```\nvalidator pins the exact anti horizontal nudge template "
        "string match here always\n```\n")
    monkeypatch.setattr(va, "CONTRACTS_DIR", contracts)
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST embed the validator pins the exact anti horizontal nudge "
        "template string match here always\n")
    errors = []
    va.check_restatements([skill], errors)
    assert errors == []  # fenced contract text is exempt (pinned templates)


def test_line_budget_warns_over_400(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("x\n" * 401)
    warns = []
    va.check_line_budget([skill], warns)
    assert len(warns) == 1 and "401 lines > 400" in warns[0]


def test_line_budget_silent_at_400(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("x\n" * 400)
    warns = []
    va.check_line_budget([skill], warns)
    assert warns == []
