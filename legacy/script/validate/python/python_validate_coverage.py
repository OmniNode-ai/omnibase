#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_coverage
# namespace: omninode.tools.validate_coverage
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:04+00:00
# last_modified_at: 2025-04-27T18:13:04+00:00
# entrypoint: validate_coverage.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_coverage.py
containers.foundation.src.foundation.script.validate.validate_coverage.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult, ValidatorMetadata
from tqdm import tqdm


def find_foundation_dir() -> Path:
    """Find the foundation directory."""
    current_dir = Path.cwd()

    # First check if we're in the foundation container
    if current_dir.name == "foundation":
        foundation_dir = current_dir / "src" / "foundation"
        if foundation_dir.exists():
            return foundation_dir

    # Try to find foundation directory by walking up
    for _ in range(5):  # Limit to 5 levels up
        foundation_dir = current_dir / "src" / "foundation"
        if foundation_dir.exists():
            return foundation_dir
        current_dir = current_dir.parent

    raise FileNotFoundError("foundation directory not found in src/foundation")


def analyze_coverage(test_dir: Path):
    """Run pytest with coverage analysis and return the coverage data using
    coverage.py API."""
    try:
        import coverage

        # Run pytest with coverage
        cmd = ["pytest", "--cov=src/foundation", "--cov-report=", "-v", str(test_dir)]
        logging.getLogger(__name__).info("Running tests with coverage analysis..")
        subprocess.run(cmd, check=True, capture_output=True)
        # Read coverage data using coverage.py API
        cov_data = coverage.CoverageData()
        cov_data.read()
        return cov_data
    except subprocess.CalledProcessError as e:
        logging.getLogger(__name__).error(f"Error running tests: {e}")
        logging.getLogger(__name__).error(f"stdout: {e.stdout.decode()}")
        logging.getLogger(__name__).error(f"stderr: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error analyzing coverage: {e}")
        sys.exit(1)


def get_subsystem_coverage(cov_data, subsystem: str) -> float:
    """Calculate coverage percentage for a specific subsystem using
    CoverageData object."""
    total_statements = 0
    covered_statements = 0
    for file_path in cov_data.measured_files():
        if f"/foundation/{subsystem}/" in file_path:
            lines = cov_data.lines(file_path) or []
            total_statements += len(lines)
            covered_lines = (
                cov_data.executed_lines(file_path)
                if hasattr(cov_data, "executed_lines")
                else lines
            )
            covered_statements += len(covered_lines)
    if total_statements == 0:
        return 0.0
    return (covered_statements / total_statements) * 100


def get_uncovered_lines(cov_data, subsystem: str):
    """Get uncovered lines for a specific subsystem using CoverageData
    object."""
    uncovered = []
    for file_path in cov_data.measured_files():
        if f"/foundation/{subsystem}/" in file_path:
            lines = set(cov_data.lines(file_path) or [])
            executed = set(
                cov_data.executed_lines(file_path)
                if hasattr(cov_data, "executed_lines")
                else lines
            )
            missing = sorted(lines - executed)
            if missing:
                uncovered.append((file_path, missing))
    return uncovered


def main():
    """Main function."""
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(
            description="Validate test coverage for foundation subsystems."
        )
        parser.add_argument(
            "--show-uncovered", action="store_true", help="Show uncovered lines"
        )
        parser.add_argument(
            "--test-dir",
            type=str,
            default=None,
            help="Path to tests directory (default: auto-detect)",
        )
        args = parser.parse_args()
        show_uncovered = args.show_uncovered
        # Find foundation directory
        foundation_dir = find_foundation_dir()
        if args.test_dir:
            test_dir = Path(args.test_dir)
        else:
            test_dir = foundation_dir.parent.parent / "tests"
        if not test_dir.exists():
            logger.error(f"Error: Test directory not found at {test_dir}")
            sys.exit(1)
        # Get coverage data
        cov_data = analyze_coverage(test_dir)
        # Get all subsystems
        subsystems = set()
        for file_path in cov_data.measured_files():
            if "/foundation/" in file_path:
                parts = file_path.split("/foundation/")[1].split("/")
                if parts:
                    subsystems.add(parts[0])
        if not subsystems:
            logger.error("No foundation subsystems found in coverage data")
            sys.exit(1)
        logger.info("\nAnalyzing coverage by subsystem:")
        logger.info("=" * 40)
        failed_subsystems = []
        for subsystem in tqdm(sorted(subsystems)):
            coverage = get_subsystem_coverage(cov_data, subsystem)
            status = "PASS" if coverage >= 30 else "FAIL"
            color = "green" if status == "PASS" else "red"
            msg = f"\n{subsystem:20} {coverage:6.2f}% [{status}]"
            if status == "PASS":
                logger.info(msg)
            else:
                logger.error(msg)
            if show_uncovered and coverage < 100:
                uncovered = get_uncovered_lines(cov_data, subsystem)
                if uncovered:
                    logger.info("\nUncovered lines:")
                    for file_path, missing in uncovered:
                        rel_path = file_path.split("foundation/")[-1]
                        logger.info(f"  {rel_path}:")
                        logger.info(f"    Lines: {', '.join(str(x) for x in missing)}")
            if coverage < 30:
                failed_subsystems.append((subsystem, coverage))
        if failed_subsystems:
            logger.error("\nSubsystems below 30% coverage threshold:")
            for subsystem, coverage in failed_subsystems:
                logger.error(f"  {subsystem:20} {coverage:6.2f}%")
            sys.exit(1)
        logger.info("\nAll subsystems meet minimum coverage requirement (30%)")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


class CoverageValidator(ProtocolValidate):
    def get_name(self) -> str:
        return "coverage"

    @classmethod
    def metadata(cls):
        # TODO: Refactor to use unified models and metadata
        raise NotImplementedError("CoverageValidator.metadata() needs unified model refactor.")

    def validate(self, target: Path, config: Optional[dict] = None):
        # TODO: Refactor to use unified result model
        raise NotImplementedError("CoverageValidator.validate() needs unified model refactor.")

    def _validate(self, *args, **kwargs):
        # Satisfy abstract method requirement
        return self.validate(*args, **kwargs)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
