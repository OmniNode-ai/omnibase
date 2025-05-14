#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_tool_orchestrator_fix_codebase"
# namespace: "omninode.tools.python_tool_orchestrator_fix_codebase"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "python_tool_orchestrator_fix_codebase.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseFixer']
# base_class: ['BaseFixer']
# mock_safe: true
# === /OmniNode:Metadata ===




"""
util_fix_codebase.py
Generic codebase fixer/orchestrator for multi-language support.
Initial implementation: Python fixers (shebang, docstring, isort, black, metadata stamper).
"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

from foundation.script.tool.python.python_tool_fix_base_abc import BaseFixer, FixResult
from foundation.script.tool.python.python_tool_fix_registry import FixerRegistry, register_fixer
from foundation.protocol.protocol_stamper import ProtocolStamper


# --- Python Fixers ---
@register_fixer(name="shebang", version="v1", description="Fixes shebang lines.")
class ShebangFixer(BaseFixer):
    def __init__(self, logger=None, config=None, runner=None):
        self.logger = logger
        self.config = config
        self.runner = runner

    @property
    def name(self) -> str:
        return "shebang"

    def fix(
        self, path: Path, dry_run: bool = False, logger: logging.Logger = None
    ) -> FixResult:
        if logger:
            logger.info(f"[shebang] Fixing {path}")
        # No-op for now
        return FixResult(changed=False)


@register_fixer(name="docstring", version="v1", description="Fixes docstrings.")
class DocstringFixer(BaseFixer):
    def __init__(self, logger=None, config=None, runner=None):
        self.logger = logger
        self.config = config
        self.runner = runner

    @property
    def name(self) -> str:
        return "docstring"

    def fix(
        self, path: Path, dry_run: bool = False, logger: logging.Logger = None
    ) -> FixResult:
        if logger:
            logger.info(f"[docstring] Fixing {path}")
        # No-op for now
        return FixResult(changed=False)


@register_fixer(
    name="isort", version="v1", description="Sorts Python imports with isort."
)
class IsortFixer(BaseFixer):
    def __init__(self, logger=None, config=None, runner=None):
        self.logger = logger
        self.config = config
        self.runner = runner or subprocess.run

    @property
    def name(self) -> str:
        return "isort"

    def fix(
        self, path: Path, dry_run: bool = False, logger: logging.Logger = None
    ) -> FixResult:
        if logger:
            logger.info(f"[isort] Sorting imports in {path}")
        if dry_run:
            return FixResult(changed=False)
        try:
            self.runner(["isort", str(path)], check=True)
            return FixResult(changed=True)
        except Exception as e:
            return FixResult(changed=False, errors=[str(e)])


@register_fixer(
    name="black", version="v1", description="Formats Python code with black."
)
class BlackFixer(BaseFixer):
    def __init__(self, logger=None, config=None, runner=None):
        self.logger = logger
        self.config = config
        self.runner = runner or subprocess.run

    @property
    def name(self) -> str:
        return "black"

    def fix(
        self, path: Path, dry_run: bool = False, logger: logging.Logger = None
    ) -> FixResult:
        if logger:
            logger.info(f"[black] Formatting {path}")
        if dry_run:
            return FixResult(changed=False)
        try:
            self.runner(["black", str(path)], check=True)
            return FixResult(changed=True)
        except Exception as e:
            return FixResult(changed=False, errors=[str(e)])


@register_fixer(
    name="metadata", version="v1", description="Stamps OmniNode metadata block."
)
class MetadataFixer(BaseFixer):
    def __init__(self, logger=None, config=None, runner=None):
        self.logger = logger
        self.config = config
        self.runner = runner

    @property
    def name(self) -> str:
        return "metadata"

    def fix(
        self, path: Path, dry_run: bool = False, logger: logging.Logger = None
    ) -> FixResult:
        if logger:
            logger.info(f"[metadata] Stamping {path}")
        # Use DI/registry to get ProtocolStamper
        stamper_cls = tool_registry.get_tool("metadata_stamper")
        if not stamper_cls:
            return FixResult(changed=False, errors=["No metadata stamper registered in tool_registry."])
        stamper: ProtocolStamper = stamper_cls(logger=logger)
        try:
            changed = stamper.stamp_file(
                path, overwrite=not dry_run, logger=logger
            )
            return FixResult(changed=changed)
        except Exception as e:
            return FixResult(changed=False, errors=[str(e)])


# --- CLI and Main Workflow ---
def get_python_files(targets):
    files = []
    for t in targets:
        p = Path(t)
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir():
            files.extend([f for f in p.rglob("*.py") if f.is_file()])
    return files


def main():
    parser = argparse.ArgumentParser(description="Generic codebase fixer/orchestrator.")
    parser.add_argument(
        "--all", action="store_true", help="Fix all files recursively (default: off)"
    )
    parser.add_argument("--staged", action="store_true", help="Fix only staged files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed, make no changes",
    )
    parser.add_argument("--log", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--language",
        type=str,
        default="python",
        help="Language to fix (default: python)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available fixers and exit"
    )
    parser.add_argument(
        "--describe", action="store_true", help="Describe all fixers and exit"
    )
    parser.add_argument(
        "--compliant-only",
        action="store_true",
        help="Run only fixers that are compliant with the new standards (for refactor phase)",
    )
    parser.add_argument(
        "targets", nargs="*", help="Files or directories to fix (default: .)"
    )
    args = parser.parse_args()
    logger = logging.getLogger("util_fix_codebase")
    if args.log:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # List or describe fixers
    if args.list:
        logger.info("Available Fixers:")
        for meta in FixerRegistry.list_metadata():
            logger.info(
                f"- {meta['name']} (v{meta['version']}) [{', '.join(meta.get('languages', []))}] - {meta.get('description', '')}"
            )
        sys.exit(0)
    if args.describe:
        logger.info("Fixer Descriptions:")
        for meta in FixerRegistry.list_metadata():
            logger.info(
                f"\n{meta['name']} (v{meta['version']}) [{', '.join(meta.get('languages', []))}]:\n  {meta.get('description', '')}"
            )
        sys.exit(0)

    # Determine files to fix
    if args.staged:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            stdout=subprocess.PIPE,
            text=True,
        )
        files = [Path(f) for f in result.stdout.splitlines() if f.endswith(".py")]
        # Patch: strip leading containers/foundation/src/ if present
        files = [Path(str(f).replace("containers/foundation/src/", "", 1)) if str(f).startswith("containers/foundation/src/") else f for f in files]
    elif args.all or not args.targets:
        files = get_python_files(["."])
    else:
        files = get_python_files(args.targets)
    if not files:
        print("No files to fix.")
        sys.exit(0)

    # Discover and instantiate fixers for the selected language
    allowed_fixers = ["chunk", "metadata"]
    fixer_metas = [
        m
        for m in FixerRegistry.list_metadata()
        if m["name"] in allowed_fixers and args.language in m.get("languages", ["python"])
    ]
    fixers = []
    for meta in fixer_metas:
        fixer_cls = FixerRegistry.get(meta["name"])
        if fixer_cls:
            fixers.append(fixer_cls(logger=logger if args.log else None))

    # Run fixers
    for path in files:
        for fixer in fixers:
            try:
                result = fixer.fix(
                    path, dry_run=args.dry_run, logger=logger if args.log else None
                )
                if not isinstance(result, FixResult):
                    logger.error(
                        f"[!] Fixer {fixer.name} did not return a FixResult for {path}. Got: {type(result)}"
                    )
                    continue
                if result.errors:
                    logger.error(
                        f"[!] Fixer {fixer.name} errors on {path}: {result.errors}"
                    )
            except Exception as e:
                logger.error(f"[!] Fixer {fixer.name} failed on {path}: {e}")
    print(f"Fixing complete. {len(files)} file(s) processed.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()