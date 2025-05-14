# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_util_fix_python_staged"
# namespace: "omninode.tools.test_tool_util_fix_python_staged"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_tool_util_fix_python_staged.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import sys
from pathlib import Path

# Compute the absolute path to the utility script
util_path = Path(__file__).resolve().parents[3] / "src/foundation/scripts/utils"
sys.path.insert(0, str(util_path))
try:
    import util_fix_python as fixer
except ModuleNotFoundError:
    print(f"[DEBUG] util_path used for import: {util_path}")
    raise


def fake_subprocess_run(cmd, **kwargs):
    class Result:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    # Simulate git diff
    if "git" in cmd:
        if "--name-only" in cmd:
            return Result(stdout="foo.py\nbar.py\nbaz.txt\n")
    # Simulate isort/black
    return Result()


def test_get_staged_python_files_none():
    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0

        return Result()

    files = fixer.get_staged_python_files(fake_run)
    assert files == []


def test_get_staged_python_files_some():
    def fake_run(cmd, **kwargs):
        class Result:
            stdout = "foo.py\nbar.py\nbaz.txt\n"
            returncode = 0

        return Result()

    files = fixer.get_staged_python_files(fake_run)
    assert files == ["foo.py", "bar.py"]


def test_run_isort_and_black_called():
    calls = []

    def fake_isort(files, subprocess_run):
        calls.append(("isort", list(files)))

    def fake_black(files, subprocess_run):
        calls.append(("black", list(files)))

    def fake_get_staged(subprocess_run):
        return ["foo.py", "bar.py"]

    def fake_metadata_stamp(files):
        calls.append(("metadata_stamp", list(files)))

    rc = fixer.main(
        get_staged_files_fn=fake_get_staged,
        run_isort_fn=fake_isort,
        run_black_fn=fake_black,
        run_metadata_stamp_fn=fake_metadata_stamp,
        subprocess_run=fake_subprocess_run,
    )
    assert rc == 0
    assert ("isort", ["foo.py", "bar.py"]) in calls
    assert ("black", ["foo.py", "bar.py"]) in calls
    assert ("metadata_stamp", ["foo.py", "bar.py"]) in calls


def test_run_isort_failure():
    def fake_isort(files, subprocess_run):
        raise fixer.subprocess.CalledProcessError(1, "isort")

    def fake_black(files, subprocess_run):
        pass

    def fake_get_staged(subprocess_run):
        return ["foo.py"]

    rc = fixer.main(
        get_staged_files_fn=fake_get_staged,
        run_isort_fn=fake_isort,
        run_black_fn=fake_black,
        subprocess_run=fake_subprocess_run,
    )
    assert rc == 1


def test_run_black_failure():
    def fake_isort(files, subprocess_run):
        pass

    def fake_black(files, subprocess_run):
        raise fixer.subprocess.CalledProcessError(1, "black")

    def fake_get_staged(subprocess_run):
        return ["foo.py"]

    rc = fixer.main(
        get_staged_files_fn=fake_get_staged,
        run_isort_fn=fake_isort,
        run_black_fn=fake_black,
        subprocess_run=fake_subprocess_run,
    )
    assert rc == 1