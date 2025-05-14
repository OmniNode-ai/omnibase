# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_coverage"
# namespace: "omninode.tools.test_validate_coverage"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_validate_coverage.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import argparse
import sys

import coverage


def main():

    parser = argparse.ArgumentParser(description="Validate code coverage")
    parser.add_argument(
        "--test-dir", type=str, default="tests", help="Directory containing tests"
    )
    parser.add_argument(
        "--show-uncovered", action="store_true", help="Show uncovered lines"
    )
    args = parser.parse_args()

    cov = coverage.Coverage(source=["foundation"])
    cov.start()

    # Discover and run tests
    import unittest

    loader = unittest.TestLoader()
    tests = loader.discover(args.test_dir)
    runner = unittest.TextTestRunner()
    result = runner.run(tests)

    cov.stop()
    cov.save()

    coverage_data = cov.get_data()
    total_covered = 0
    total_statements = 0

    for filename in coverage_data.measured_files():
        total_covered += len(coverage_data.lines(filename))
        analysis = cov._analyze(filename)
        total_statements += len(analysis.statements)

    coverage_percent = (
        (total_covered / total_statements) * 100 if total_statements else 0
    )

    print(f"Coverage: {coverage_percent:.2f}%")

    if args.show_uncovered:
        cov.report(show_missing=True)

    if coverage_percent < 80:
        print("Coverage below threshold")
        sys.exit(1)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()