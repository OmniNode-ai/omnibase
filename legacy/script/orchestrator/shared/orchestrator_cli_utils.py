import argparse

class OrchestratorCLIUtils:
    """
    Shared utility for orchestrator CLI argument parsing and helpers.
    To be used by all orchestrators for consistent CLI behavior.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    @staticmethod
    def parse_args(args=None):
        parser = argparse.ArgumentParser(description="Orchestrator CLI for running validators.")
        parser.add_argument(
            "--validator",
            type=str,
            help="Comma-separated list of validator names to run. If omitted, all validators are run.",
            default=None,
        )
        parser.add_argument(
            "--staged",
            action="store_true",
            help="Validate only staged files."
        )
        parser.add_argument(
            "--output",
            type=str,
            choices=["json", "text"],
            default="text",
            help="Output format: json or text (default: text)."
        )
        parser.add_argument(
            "--target",
            type=str,
            help="Target file or directory to validate."
        )
        parsed = parser.parse_args(args)
        if parsed.validator:
            parsed.validator = [v.strip() for v in parsed.validator.split(",") if v.strip()]
        else:
            parsed.validator = None
        return parsed 