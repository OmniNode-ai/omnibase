from typing import Any

class OrchestratorConfig:
    """
    DI-injectable config object for orchestrator configuration and policy.
    To be used by all orchestrators for consistent, testable config and policy injection.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    # Example config fields (stub)
    file_extensions: Any = None
    template_path: Any = None
    ignore_patterns: Any = None
    output_modes: Any = None
    subprocess_runner: Any = None
    vcs_client: Any = None 