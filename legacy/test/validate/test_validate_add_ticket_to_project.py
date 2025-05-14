# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_add_ticket_to_project"
# namespace: "omninode.tools.test_validate_add_ticket_to_project"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_validate_add_ticket_to_project.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import foundation.script.git.add_ticket_to_project as add_ticket_to_project
import pytest
from foundation.script.git.omninode_issue_model import OmniNodeIssue


def make_issue(**kwargs):
    defaults = dict(
        title="Test Title",
        status="Todo",
        priority="Medium",
        notes="",
        context="Test context",
        requirements=["Req1", "Req2"],
        acceptance_criteria=["Acc1", "Acc2"],
        additional_notes="",
    )
    defaults.update(kwargs)
    return OmniNodeIssue(**defaults)


def test_check_gh_cli_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/gh")
    # Should not raise
    add_ticket_to_project.check_gh_cli()


def test_check_gh_cli_not_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    with pytest.raises(SystemExit):
        add_ticket_to_project.check_gh_cli()


def test_add_ticket_dry_run(capsys):
    rc = add_ticket_to_project.add_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1", dry_run=True
    )
    out = capsys.readouterr().out
    assert "[DRY RUN] Would execute:" in out
    assert rc == 0


def test_add_ticket_success(monkeypatch, capsys):
    class Result:
        returncode = 0
        stdout = "Added item"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: Result())
    rc = add_ticket_to_project.add_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Successfully added issue" in out
    assert rc == 0


def test_add_ticket_failure(monkeypatch, capsys):
    class Result:
        returncode = 1
        stdout = ""
        stderr = "error: something went wrong"

    monkeypatch.setattr("subprocess.run", lambda *a, **k: Result())
    rc = add_ticket_to_project.add_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Error adding issue" in out
    assert rc == 1


def test_add_ticket_exception(monkeypatch, capsys):
    monkeypatch.setattr(
        "subprocess.run", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )
    rc = add_ticket_to_project.add_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Exception: fail" in out
    assert rc == 1


def test_create_issue_success(monkeypatch, capsys):
    class Result:
        returncode = 0
        stdout = "\nhttps://github.com/OmniNode-ai/ai-dev/issues/999\n"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: Result())
    issue = make_issue()
    url = add_ticket_to_project.create_issue("OmniNode-ai/ai-dev", issue)
    out = capsys.readouterr().out
    assert "Successfully created issue" in out
    assert url == "https://github.com/OmniNode-ai/ai-dev/issues/999"


def test_create_issue_dry_run(capsys):
    issue = make_issue()
    url = add_ticket_to_project.create_issue("OmniNode-ai/ai-dev", issue, dry_run=True)
    out = capsys.readouterr().out
    assert "[DRY RUN] Would execute:" in out
    assert url.startswith("https://github.com/OmniNode-ai/ai-dev/issues/")


def test_create_issue_failure(monkeypatch, capsys):
    class Result:
        returncode = 1
        stdout = ""
        stderr = "error: could not create issue"

    monkeypatch.setattr("subprocess.run", lambda *a, **k: Result())
    issue = make_issue()
    url = add_ticket_to_project.create_issue("OmniNode-ai/ai-dev", issue)
    out = capsys.readouterr().out
    assert "Error creating issue" in out
    assert url is None


def test_create_issue_exception(monkeypatch, capsys):
    monkeypatch.setattr(
        "subprocess.run", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )
    issue = make_issue()
    url = add_ticket_to_project.create_issue("OmniNode-ai/ai-dev", issue)
    out = capsys.readouterr().out
    assert "Exception: fail" in out
    assert url is None


def test_create_and_add_integration(monkeypatch, capsys):
    # Simulate both creation and add_ticket
    class CreateResult:
        returncode = 0
        stdout = "\nhttps://github.com/OmniNode-ai/ai-dev/issues/1000\n"
        stderr = ""

    class AddResult:
        returncode = 0
        stdout = "Added item"
        stderr = ""

    call_log = []

    def fake_run(cmd, *a, **k):
        if "issue" in cmd:
            call_log.append("create")
            return CreateResult()
        elif "project" in cmd:
            call_log.append("add")
            return AddResult()
        raise Exception("Unknown command")

    monkeypatch.setattr("subprocess.run", fake_run)
    # Simulate CLI args
    issue = make_issue()
    url = add_ticket_to_project.create_issue("OmniNode-ai/ai-dev", issue)
    rc = add_ticket_to_project.add_ticket("OmniNode-ai", 1, url)
    out = capsys.readouterr().out
    assert "Successfully created issue" in out
    assert "Successfully added issue" in out
    assert call_log == ["create", "add"]


def test_remove_ticket_dry_run(capsys):
    rc = add_ticket_to_project.remove_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1", dry_run=True
    )
    out = capsys.readouterr().out
    assert "[DRY RUN] Would execute:" in out
    assert "Would remove issue" in out
    assert rc == 0


def test_remove_ticket_success(monkeypatch, capsys):
    # Simulate finding the item and successful removal
    class ListResult:
        returncode = 0
        stdout = (
            '[{"id": "123", "content_url": "https://github.com/org/repo/issues/1"}]'
        )
        stderr = ""

    class RmResult:
        returncode = 0
        stdout = "Removed"
        stderr = ""

    def fake_run(cmd, *a, **k):
        if "item-list" in cmd:
            return ListResult()
        elif "item-remove" in cmd:
            return RmResult()
        raise Exception("Unknown command")

    monkeypatch.setattr("subprocess.run", fake_run)
    rc = add_ticket_to_project.remove_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Successfully removed issue" in out
    assert rc == 0


def test_remove_ticket_not_found(monkeypatch, capsys):
    class ListResult:
        returncode = 0
        stdout = (
            '[{"id": "123", "content_url": "https://github.com/org/repo/issues/2"}]'
        )
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **k: ListResult())
    rc = add_ticket_to_project.remove_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "not found in project" in out
    assert rc == 1


def test_remove_ticket_list_error(monkeypatch, capsys):
    class ListResult:
        returncode = 1
        stdout = ""
        stderr = "error: cannot list"

    monkeypatch.setattr("subprocess.run", lambda *a, **k: ListResult())
    rc = add_ticket_to_project.remove_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Error listing project items" in out
    assert rc == 1


def test_remove_ticket_remove_error(monkeypatch, capsys):
    class ListResult:
        returncode = 0
        stdout = (
            '[{"id": "123", "content_url": "https://github.com/org/repo/issues/1"}]'
        )
        stderr = ""

    class RmResult:
        returncode = 1
        stdout = ""
        stderr = "error: cannot remove"

    def fake_run(cmd, *a, **k):
        if "item-list" in cmd:
            return ListResult()
        elif "item-remove" in cmd:
            return RmResult()
        raise Exception("Unknown command")

    monkeypatch.setattr("subprocess.run", fake_run)
    rc = add_ticket_to_project.remove_ticket(
        "OmniNode-ai", 1, "https://github.com/org/repo/issues/1"
    )
    out = capsys.readouterr().out
    assert "Error removing issue" in out
    assert rc == 1