"""
File generation utilities for NodeGeneratorNode.

Handles copying template structures, file operations, and post-generation
tasks like stamping and .onextree generation.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List
import json

from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from omnibase.enums import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
from ..protocols.protocol_file_generator import ProtocolFileGenerator
from ..models.model_generated_models import ModelGeneratedModels
from ..models.model_validation_result import ModelValidationResult
from ..models.model_template_context import ModelTemplateContext
from omnibase.core.core_error_codes import ModelOnexError, CoreErrorCode


class ToolFileGenerator(ProtocolFileGenerator):
    """
    Implements ProtocolFileGenerator for file operations during node generation.

    Handles template copying, directory creation, and post-generation
    tasks like stamping and .onextree generation.
    """

    def __init__(self, event_bus=None, logger_tool: ProtocolLoggerEmitLogEvent = None):
        """Initialize the file generator."""
        self.generated_files = []
        self._event_bus = event_bus
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool

    def copy_template_structure(
        self,
        template_path: Path,
        target_path: Path,
        node_name: str,
        context: ModelTemplateContext,
    ) -> ModelGeneratedModels:
        """
        Copy the template directory structure to the target location.

        Args:
            template_path: Path to the template directory
            target_path: Path where the new node will be created
            node_name: Name of the new node
            context: ModelTemplateContext for the generation

        Returns:
            ModelGeneratedModels: Mapping of model names to generated file paths.
        """
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Copying template structure from {template_path} to {target_path}",
            node_id=node_name,
            event_bus=self._event_bus,
        )
        generated_files = []
        target_path = Path(target_path)
        target_path.mkdir(parents=True, exist_ok=True)
        try:
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(template_path, target_path)
            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    generated_files.append(str(file_path))
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.INFO,
                f"Successfully copied {len(generated_files)} files",
                node_id=node_name,
                data={"generated_files_count": len(generated_files)},
                event_bus=self._event_bus,
            )
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to copy template structure: {e}",
                node_id=node_name,
                data={
                    "template_path": str(template_path),
                    "target_path": str(target_path),
                },
                event_bus=self._event_bus,
            )
            raise
        self.generated_files.extend(generated_files)
        return ModelGeneratedModels(files=generated_files)

    def run_initial_stamping(self, node_path: Path) -> None:
        """
        Run initial stamping on the generated node files.

        Args:
            node_path: Path to the generated node directory
        """
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Running initial stamping on {node_path}",
            context=make_log_context(node_id=str(node_path)),
            event_bus=self._event_bus,
        )
        try:
            python_files = list(node_path.rglob("*.py"))
            for py_file in python_files:
                try:
                    result = subprocess.run(
                        ["poetry", "run", "onex", "stamp", "file", str(py_file)],
                        capture_output=True,
                        text=True,
                        cwd=Path.cwd(),
                    )
                    if result.returncode != 0:
                        self.logger_tool.emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"Failed to stamp {py_file}: {result.stderr}",
                            context=make_log_context(
                                node_id=str(py_file), file=str(py_file)
                            ),
                            event_bus=self._event_bus,
                        )
                except Exception as e:
                    self.logger_tool.emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"Error stamping {py_file}: {e}",
                        context=make_log_context(
                            node_id=str(py_file), file=str(py_file)
                        ),
                        event_bus=self._event_bus,
                    )
            yaml_files = list(node_path.rglob("*.yaml"))
            for yaml_file in yaml_files:
                try:
                    result = subprocess.run(
                        ["poetry", "run", "onex", "stamp", "file", str(yaml_file)],
                        capture_output=True,
                        text=True,
                        cwd=Path.cwd(),
                    )
                    if result.returncode != 0:
                        self.logger_tool.emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"Failed to stamp {yaml_file}: {result.stderr}",
                            context=make_log_context(
                                node_id=str(yaml_file), file=str(yaml_file)
                            ),
                            event_bus=self._event_bus,
                        )
                except Exception as e:
                    self.logger_tool.emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"Error stamping {yaml_file}: {e}",
                        context=make_log_context(
                            node_id=str(yaml_file), file=str(yaml_file)
                        ),
                        event_bus=self._event_bus,
                    )
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.INFO,
                "Initial stamping completed",
                context=make_log_context(
                    node_id=str(node_path),
                    stamped_files=len(python_files) + len(yaml_files),
                ),
                event_bus=self._event_bus,
            )
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to run initial stamping: {e}",
                context=make_log_context(node_id=str(node_path)),
                event_bus=self._event_bus,
            )
            raise

    def generate_onextree(self, node_path: Path) -> None:
        """
        Generate .onextree file for the new node.

        Args:
            node_path: Path to the generated node directory
        """
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Generating .onextree for {node_path}",
            context=make_log_context(node_id=str(node_path)),
            event_bus=self._event_bus,
        )
        try:
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "onex",
                    "run",
                    "node_tree_generator",
                    "--args",
                    f'["--root-directory", "{node_path}", "--output-path", "{node_path}/.onextree"]',
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            if result.returncode == 0:
                self.logger_tool.emit_log_event_sync(
                    LogLevelEnum.INFO,
                    "Successfully generated .onextree",
                    context=make_log_context(
                        node_id=str(node_path), output_path=str(node_path / ".onextree")
                    ),
                    event_bus=self._event_bus,
                )
            else:
                self.logger_tool.emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Failed to generate .onextree: {result.stderr}",
                    context=make_log_context(node_id=str(node_path)),
                    event_bus=self._event_bus,
                )
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Error generating .onextree: {e}",
                context=make_log_context(node_id=str(node_path)),
                event_bus=self._event_bus,
            )
            raise

    def _wrap_errors(self, errors):
        wrapped = []
        for err in errors:
            if isinstance(err, dict):
                try:
                    wrapped.append(ModelOnexError(**err))
                except Exception:
                    wrapped.append(ModelOnexError(
                        code=CoreErrorCode.VALIDATION_ERROR,
                        message=str(err),
                    ))
            else:
                wrapped.append(ModelOnexError(
                    code=CoreErrorCode.VALIDATION_ERROR,
                    message=str(err),
                ))
        return wrapped

    def run_parity_validation(self, node_path: Path) -> ModelValidationResult:
        """
        Run parity validation on the generated node.

        Args:
            node_path: Path to the generated node directory

        Returns:
            ModelValidationResult: Validation result model
        """
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Running parity validation on {node_path}",
            context=make_log_context(node_id=str(node_path)),
            event_bus=self._event_bus,
        )
        try:
            # Run JSON output for errors
            result_json = subprocess.run(
                [
                    "poetry",
                    "run",
                    "onex",
                    "run",
                    "node_parity_validator",
                    "--args",
                    f'["--nodes-directory", "{node_path}", "--format", "json"]',
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            # Run markdown output for human-readable details
            result_md = subprocess.run(
                [
                    "poetry",
                    "run",
                    "onex",
                    "run",
                    "node_parity_validator",
                    "--args",
                    f'["--nodes-directory", "{node_path}", "--format", "markdown"]',
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            # Filter markdown output to remove debug/log/JSON lines
            def _filter_markdown(md: str) -> str:
                lines = md.splitlines()
                filtered = [
                    line for line in lines
                    if not line.strip().startswith("{")
                    and not line.strip().startswith("[DEBUG]")
                    and not line.strip().startswith("[ERROR]")
                    and not line.strip().startswith("[WARNING]")
                    and not line.strip().startswith("[INFO]")
                    and not line.strip().startswith("[TRACE]")
                    and not line.strip().startswith("[LOG]")
                    and not line.strip().startswith("[KafkaEventBus]")
                ]
                return "\n".join(filtered).strip()
            details = _filter_markdown(result_md.stdout) if result_md.returncode == 0 else "Could not generate markdown output"
            if result_json.returncode == 0:
                try:
                    validation_data = json.loads(result_json.stdout)
                    errors = validation_data.get("errors") or validation_data.get("failures") or []
                    wrapped_errors = self._wrap_errors(errors)
                    success = not wrapped_errors
                    self.logger_tool.emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"Parity validation completed. Errors: {wrapped_errors}",
                        context=make_log_context(
                            node_id=str(node_path),
                            validation_status=validation_data.get("status", "unknown"),
                            errors=len(wrapped_errors),
                        ),
                        event_bus=self._event_bus,
                    )
                    return ModelValidationResult(
                        success=success,
                        details=details,
                        errors=wrapped_errors,
                        metadata=None,
                    )
                except json.JSONDecodeError:
                    self.logger_tool.emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        "Could not parse parity validation output",
                        context=make_log_context(
                            node_id=str(node_path), stdout=result_json.stdout
                        ),
                        event_bus=self._event_bus,
                    )
                    return ModelValidationResult(success=False, details=details, errors=self._wrap_errors([result_json.stdout]), metadata=None)
            else:
                self.logger_tool.emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Parity validation failed: {result_json.stderr}",
                    context=make_log_context(node_id=str(node_path)),
                    event_bus=self._event_bus,
                )
                return ModelValidationResult(success=False, details=details, errors=self._wrap_errors([result_json.stderr]), metadata=None)
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[run_parity_validation] Exception: {e}",
                node_id=str(node_path),
                event_bus=self._event_bus,
            )
            return ModelValidationResult(success=False, details=str(e), errors=self._wrap_errors([str(e)]), metadata=None)

    def create_directory_structure(
        self, base_path: Path, directories: List[str]
    ) -> None:
        """
        Create a directory structure.

        Args:
            base_path: Base path where directories will be created
            directories: List of directory paths to create
        """
        for directory in directories:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"Created directory: {dir_path}",
                context=make_log_context(
                    node_id=str(dir_path), directory=str(dir_path)
                ),
                event_bus=self._event_bus,
            )

    def write_file(self, file_path: Path, content: str) -> None:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            self.generated_files.append(str(file_path))
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"Created file: {file_path}",
                context=make_log_context(node_id=str(file_path), file=str(file_path)),
                event_bus=self._event_bus,
            )
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to write file {file_path}: {e}",
                context=make_log_context(node_id=str(file_path), file=str(file_path)),
                event_bus=self._event_bus,
            )
            raise

    def generate_file(self, path: str, content: str, overwrite: bool = False) -> None:
        """
        Generate or overwrite a file at the given path with the provided content.
        Args:
            path (str): The file path to write to.
            content (str): The file content to write.
            overwrite (bool): Whether to overwrite if the file exists.
        """
        file_path = Path(path)
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {file_path}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Generated file: {file_path}",
            context=make_log_context(file=str(file_path)),
            event_bus=self._event_bus,
        )
