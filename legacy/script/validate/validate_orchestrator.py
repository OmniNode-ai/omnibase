# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "validate_orchestrator"
# namespace: "omninode.tools.validate_orchestrator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "validate_orchestrator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["OrchestratorProtocol"]
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Validator Orchestrator (refactored): Implements OrchestratorProtocol, uses DI, registry, and shared utilities.
See: validator_refactor_checklist.yaml, validator_testing_standards.md
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
import re
from typing import Optional, Any

import pydantic
from foundation.di.di_container import DIContainer
from foundation.script.validate.common.common_validator_utils import get_staged_files
from foundation.script.validate.config.config_manager import ConfigurationManager
from foundation.script.validate.validate_registry import (
    ValidatorRegistry,
    register_validators_with_di,
)
from foundation.model.model_metadata import StamperIgnoreModel
from foundation.protocol.protocol_stamper_ignore import ProtocolStamperIgnore
from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.protocol.protocol_orchestrator import OrchestratorProtocol
from foundation.script.orchestrator.orchestrator_registry import OrchestratorRegistry
from foundation.script.orchestrator.orchestrator_config import OrchestratorConfig
from foundation.script.orchestrator.shared.orchestrator_cli_utils import OrchestratorCLIUtils
from foundation.script.orchestrator.shared.orchestrator_file_discovery import OrchestratorFileDiscovery
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol
from foundation.script.orchestrator.shared.shared_output_formatter import SharedOutputFormatter
from foundation.protocol.protocol_process_runner import ProcessRunnerProtocol
from foundation.protocol.protocol_vcs_client import VCSClientProtocol
from foundation.bootstrap.bootstrap import bootstrap
from foundation.util.util_file_output_writer import OutputWriter

class ValidateOrchestrator(OrchestratorProtocol):
    """
    DI/registry-compliant orchestrator for validation workflows.
    Implements OrchestratorProtocol and uses shared utilities.
    """
    def __init__(self, registry=None, di_container=None, logger=None, config=None, process_runner=None, vcs_client=None, output_formatter: Optional[OutputFormatterProtocol] = None):
        self.registry = registry
        self.di_container = di_container
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or OrchestratorConfig()
        self.process_runner = process_runner  # type: ProcessRunnerProtocol
        self.vcs_client = vcs_client  # type: VCSClientProtocol
        self.output_formatter = output_formatter or SharedOutputFormatter()

    def run(self) -> UnifiedBatchResultModel:
        self.logger.info("[Orchestrator] Running validation orchestration...")
        args = self.parse_args()
        files = self.discover_targets(args)
        results = self.execute_actions(files, args)
        return self.summarize_results()

    def parse_args(self, args=None):
        return OrchestratorCLIUtils.parse_args(args)

    def discover_targets(self, args=None):
        return OrchestratorFileDiscovery.discover_targets(args)

    def execute_actions(self, files, args=None):
        # TODO: Refactor main validation loop here using DI/registry
        return []

    def summarize_results(self) -> Any:
        # This method should be implemented to match the protocol signature.
        # If you need to pass results, store them as an instance variable or refactor as needed.
        pass

# Update registry with actual class
OrchestratorRegistry().register("validate_orchestrator", ValidateOrchestrator)

if __name__ == "__main__":
    bootstrap()
    orchestrator = ValidateOrchestrator()
    orchestrator.run()

    # TODO: Migrate all legacy logic into ValidateOrchestrator methods and remove old function-based code.

def is_result_valid(result) -> bool:
    """
    Canonical validity check for validator results.
    - For new models: status == ValidateStatus.VALID
    - For legacy models: is_valid attribute
    Reference: docs/validation/validator_testing_standards.md
    """
    status = getattr(result, "status", None)
    if status is not None:
        return status == UnifiedStatus.success
    return getattr(result, "is_valid", False)


def extract_issues(result, severity):
    """
    Helper to extract issues of a given severity from a result object.
    - For new models: filter result.messages by severity
    - For legacy models: use result.errors or result.warnings
    """
    if hasattr(result, "messages"):
        return [m for m in getattr(result, "messages", []) if getattr(m, "severity", None) == severity]
    return []


def run_orchestration(ignore_provider: Optional[ProtocolStamperIgnore] = None):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", force=True
    )
    logger = logging.getLogger(__name__)
    logger.info("[DEBUG] Entered run_orchestration()")
    try:
        args = OrchestratorCLIUtils.parse_args()
        registry = ValidatorRegistry()
        di_container = DIContainer()
        register_validators_with_di(di_container, registry)
        config_manager = ConfigurationManager()

        if ignore_provider is None:
            ignore_provider = StamperIgnoreModel()
        ignore_files = set(ignore_provider.get_ignore_files())

        if args.version:
            logger.info("Validator Orchestrator v2.0 (Registry+DI)")
            sys.exit(0)

        if args.list:
            logger.info("Available Validators:")
            for meta in getattr(registry, '_metadata', []):
                logger.info(
                    f"- {meta['name']} (v{meta['version']}) [{meta.get('group', 'default')}] - {meta.get('description', '')}"
                )
            sys.exit(0)

        if args.describe:
            logger.info("Validator Descriptions:")
            for meta in getattr(registry, '_metadata', []):
                logger.info(
                    f"\n{meta['name']} (v{meta['version']}) [{meta.get('group', 'default')}]:\n  {meta.get('description', '')}"
                )
            sys.exit(0)

        # Universal validator enforcement: enumerate all validators
        if getattr(args, "validator", None):
            requested_validators = args.validator
            all_validators = set(registry.list_validators())
            unknown = [v for v in requested_validators if v not in all_validators]
            if unknown:
                logger.error(f"Unknown validator(s) specified: {unknown}. Available: {sorted(all_validators)}")
                sys.exit(2)
            validator_names = requested_validators
            logger.info(f"[FILTERED] Running only specified validators: {validator_names}")
        else:
            validator_names = registry.list_validators()
            logger.info(f"[UNIVERSAL] Running all validators: {validator_names}")

        # Load config (with optional override)
        config = config_manager.default_config
        if args.config:
            with open(args.config) as f:
                override = json.load(f)
            config_manager._merge_configs(config, override)

        # Determine files to check
        staged_files = []
        if getattr(args, "staged", False):
            logger.info("[STAGED MODE] Validating only staged files.")
            staged_files = get_staged_files()
            logger.info(f"Staged files: {staged_files}")
            if not staged_files:
                logger.info("No staged files to validate. Exiting.")
                sys.exit(0)
            files_to_check = [Path(f) for f in staged_files if str(f).endswith(".py") and str(f) not in ignore_files]
        elif args.target:
            target = Path(args.target)
            if target.is_file() and str(target).endswith(".py") and str(target) not in ignore_files:
                files_to_check = [target]
            else:
                files_to_check = [f for f in target.rglob("*.py") if str(f) not in ignore_files]
        else:
            files_to_check = [f for f in Path.cwd().rglob("*.py") if str(f) not in ignore_files]
        logger.info(f"Files to check: {[str(f) for f in files_to_check]}")
        if not files_to_check:
            logger.info("No Python files to validate. Exiting.")
            sys.exit(0)

        logger.info(f"Validators to run: {validator_names}")
        logger.info("Starting main validation loop.")
        # Run all validators on all files
        summary: list = []
        any_fail = False

        def serialize_issues(issues):
            return [
                (
                    i.model_dump()
                    if hasattr(i, "model_dump")
                    else i.dict() if hasattr(i, "dict") else i
                )
                for i in issues
            ]

        def serialize_summary(summary):
            def convert_status(status):
                if hasattr(status, "name"):
                    return status.name
                return status
            for file_result in summary:
                for v in file_result["validators"]:
                    if "errors" in v:
                        v["errors"] = serialize_issues(v["errors"])
                    if "warnings" in v:
                        v["warnings"] = serialize_issues(v["warnings"])
                    if "status" in v:
                        v["status"] = convert_status(v["status"])
            return summary

        for file_path in files_to_check:
            logger.info(f"Validating file: {file_path}")
            file_result: dict = {"file": str(file_path), "validators": []}
            for name in validator_names:
                # Per-validator file filtering
                if name == "registry_consistency":
                    if not (re.search(r"registry", str(file_path), re.IGNORECASE) and str(file_path).lower().endswith((".yaml", ".yml"))):
                        logger.info(f"[FILTER] Skipping file for registry_consistency: {file_path}")
                        continue
                logger.info(f"  Running validator: {name}")
                validator_cls = registry.get_validator(name)
                if not validator_cls:
                    logger.warning(f"  Validator {name} not found in registry.")
                    continue
                validator = di_container.resolve(validator_cls)
                try:
                    result = validator.validate(str(file_path))
                except pydantic.ValidationError as e:
                    logger.error(
                        f"Pydantic ValidationError in validator '{name}' for file '{file_path}': {e}"
                    )
                    result = UnifiedResultModel(
                        messages=[UnifiedMessageModel(
                            summary=f"Pydantic ValidationError: {e}",
                            file=str(file_path),
                            level="error",
                            type="error",
                            context={"validator": name}
                        )],
                        status=UnifiedStatus.error
                    )
                except Exception as e:
                    logger.error(
                        f"Exception in validator '{name}' for file '{file_path}': {e}"
                    )
                    result = UnifiedResultModel(
                        messages=[UnifiedMessageModel(
                            summary=f"Exception: {e}",
                            file=str(file_path),
                            level="error",
                            type="error",
                            context={"validator": name}
                        )],
                        status=UnifiedStatus.error
                    )
                logger.info(
                    f"    Result: is_valid={is_result_valid(result)}, status={getattr(result, 'status', None)}, errors={extract_issues(result, 'error')}, warnings={extract_issues(result, 'warning')}"
                )
                file_result["validators"].append(
                    {
                        "name": name,
                        "is_valid": is_result_valid(result),
                        "errors": extract_issues(result, "error"),
                        "warnings": extract_issues(result, "warning"),
                        "status": getattr(result, "status", None),
                    }
                )
                if getattr(result, "status", None) == UnifiedStatus.SKIPPED:
                    logger.info(f"[SKIPPED] {name} skipped file: {file_path}")
                elif getattr(result, "status", None) == UnifiedStatus.error:
                    any_fail = True
            summary.append(file_result)
        logger.info(
            f"Validation summary: {json.dumps(serialize_summary(summary), indent=2)}"
        )

        # Output structured summary
        output_mode = getattr(args, "output", "text")
        formatter = SharedOutputFormatter()
        batch_result = formatter.format_output(summary, format_type="json")
        if output_mode == "json" or getattr(args, "summary", False):
            # Canonical CI error serialization: always output UnifiedBatchResultModel as JSON
            print(formatter.render_output(batch_result, format_type="json"))  # See docs/validation/validator_standards.md
        else:
            logger.info("\nVALIDATOR SUMMARY:")
            for file_result in summary:
                logger.info(f"File: {file_result['file']}")
                for v in file_result["validators"]:
                    if v.get("status") == UnifiedStatus.SKIPPED:
                        logger.info(f"  - {v['name']}: SKIPPED")
                    else:
                        status = "PASS" if v["is_valid"] else "FAIL"
                        logger.info(f"  - {v['name']}: {status}")
                    if v["errors"]:
                        for err in v["errors"]:
                            if hasattr(err, "model_dump"):
                                err = err.model_dump()
                            logger.error(f"      Error: {err}")
                    if v["warnings"]:
                        for warn in v["warnings"]:
                            if hasattr(warn, "model_dump"):
                                warn = warn.model_dump()
                            logger.warning(f"      Warning: {warn}")
            logger.info(f"\nTotals:")
            logger.info(f"  Files checked: {len(summary)}")
            logger.info(f"  Files with errors: {sum(1 for f in summary if any(not v['is_valid'] for v in f['validators']))}")

        # After validation, auto-stamp files that failed metadata_block validation
        SAFE_EXTS = {
            ".py",
            ".sh",
            ".bash",
            ".yaml",
            ".yml",
            ".ini",
            ".cfg",
            ".conf",
            ".toml",
            ".rb",
            ".pl",
            ".r",
            ".env",
            ".txt",
            ".md",
            ".rst",
        }
        TEMPLATE_PATH = "foundation/template/metadata/"
        files_to_stamp: list = []
        for file_result in summary:
            file_path = file_result["file"]
            ext = Path(file_path).suffix.lower()
            if TEMPLATE_PATH in str(file_path):
                continue
            if ext in SAFE_EXTS:
                files_to_stamp.append(file_path)
        if files_to_stamp:
            logger.info(f"Auto-stamping metadata for: {files_to_stamp}")
            for file_path in files_to_stamp:
                subprocess.run(
                    [
                        sys.executable,
                        str(
                            Path(__file__).parent.parent
                            / "metadata"
                            / "metadata_stamper.py"
                        ),
                        file_path,
                        "--overwrite",
                    ],
                    check=False,
                )
                # Auto-stage the file
                subprocess.run(["git", "add", file_path], check=False)
            # Re-run validation on auto-stamped files
            logger.info("Re-running validation on auto-stamped files...")
            # Only re-validate the stamped files
            revalidate_summary: list = []
            revalidate_fail = False
            for file_path in files_to_stamp:
                logger.info(f"Re-validating file: {file_path}")
                file_result_reval: dict = {"file": str(file_path), "validators": []}
                for name in validator_names:
                    # Per-validator file filtering (re-validation loop)
                    if name == "registry_consistency":
                        if not (re.search(r"registry", str(file_path), re.IGNORECASE) and str(file_path).lower().endswith((".yaml", ".yml"))):
                            logger.info(f"[FILTER] Skipping file for registry_consistency (revalidation): {file_path}")
                            continue
                    logger.info(f"  Running validator: {name} (revalidation)")
                    validator_cls = registry.get_validator(name)
                    if not validator_cls:
                        logger.warning(f"  Validator {name} not found in registry.")
                        continue
                    validator = di_container.resolve(validator_cls)
                    try:
                        result = validator.validate(str(file_path))
                    except Exception as e:
                        logger.error(f"Exception in validator '{name}' for file '{file_path}': {e}")
                        result = UnifiedResultModel(
                            messages=[UnifiedMessageModel(
                                summary=f"Exception: {e}",
                                file=str(file_path),
                                level="error",
                                type="error",
                                context={"validator": name}
                            )],
                            status=UnifiedStatus.error
                        )
                    logger.info(
                        f"    Result: is_valid={is_result_valid(result)}, status={getattr(result, 'status', None)}, errors={extract_issues(result, 'error')}, warnings={extract_issues(result, 'warning')}"
                    )
                    file_result_reval["validators"].append(
                        {
                            "name": name,
                            "is_valid": is_result_valid(result),
                            "errors": extract_issues(result, "error"),
                            "warnings": extract_issues(result, "warning"),
                            "status": getattr(result, "status", None),
                        }
                    )
                    if getattr(result, "status", None) == UnifiedStatus.SKIPPED:
                        logger.info(f"[SKIPPED] {name} skipped file: {file_path}")
                    elif getattr(result, "status", None) == UnifiedStatus.error:
                        revalidate_fail = True
                revalidate_summary.append(file_result_reval)
            logger.info(f"Re-validation summary: {json.dumps(serialize_summary(revalidate_summary), indent=2)}")
            if revalidate_fail:
                logger.error("[ERROR] Some files still fail validation after auto-stamping. Please fix errors and try again.")
                sys.exit(1)
            else:
                logger.info("[INFO] Metadata blocks were auto-stamped and all files now pass validation. Commit can proceed.")
                sys.exit(0)

        # Exit with code 1 if any validator result is invalid
        if any_fail:
            if output_mode == "json":
                print(formatter.render_output(batch_result, format_type="json"))  # Canonical CI error serialization
            logger.debug("At least one validator failed. Exiting with code 1.")
            sys.exit(1)
        logger.debug("All validators passed. Exiting with code 0.")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"[FATAL] Exception in run_orchestration: {exc}", exc_info=True)
        sys.exit(2)


# (Old tuple-based logic is commented out below for reference)
# PATCH: Run both 'chunk' and 'metadata_block' validators for refactor phase
# validator_names = ["chunk", "metadata_block"]
# logger.info("[PATCH] Running 'chunk' and 'metadata_block' tuple validators. Others are skipped until refactored and marked complete. This is a temporary restriction.")
# END PATCH

def run_metadata_block_validators(file_paths, logger):
    results = []
    for file_path in file_paths:
        ext = Path(file_path).suffix.lower()
        validator_cls = validator_cls