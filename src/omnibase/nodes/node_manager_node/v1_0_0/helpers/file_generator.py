"""
File generation utilities for NodeGeneratorNode.

Handles copying template structures, file operations, and post-generation
tasks like stamping and .onextree generation.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum


class FileGenerator:
    """
    Utility class for file operations during node generation.

    Handles template copying, directory creation, and post-generation
    tasks like stamping and .onextree generation.
    """

    def __init__(self, event_bus=None):
        """Initialize the file generator."""
        self.generated_files = []
        self._event_bus = event_bus

    def copy_template_structure(
        self,
        template_path: Path,
        target_path: Path,
        node_name: str,
        customizations: Dict[str, Any],
    ) -> List[str]:
        """
        Copy the template directory structure to the target location.

        Args:
            template_path: Path to the template directory
            target_path: Path where the new node will be created
            node_name: Name of the new node
            customizations: Custom values for the generation

        Returns:
            List of generated file paths
        """
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Copying template structure from {template_path} to {target_path}",
            context={"node_name": node_name},
            event_bus=self._event_bus,
        )
        generated_files = []
        target_path.mkdir(parents=True, exist_ok=True)
        try:
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(template_path, target_path)
            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    generated_files.append(str(file_path))
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"Successfully copied {len(generated_files)} files",
                context={"generated_files_count": len(generated_files)},
                event_bus=self._event_bus,
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to copy template structure: {e}",
                context={
                    "template_path": str(template_path),
                    "target_path": str(target_path),
                },
                event_bus=self._event_bus,
            )
            raise
        self.generated_files.extend(generated_files)
        return generated_files

    def run_initial_stamping(self, node_path: Path) -> None:
        """
        Run initial stamping on the generated node files.

        Args:
            node_path: Path to the generated node directory
        """
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Running initial stamping on {node_path}",
            context={"node_path": str(node_path)},
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
                        emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"Failed to stamp {py_file}: {result.stderr}",
                            context={"file": str(py_file)},
                            event_bus=self._event_bus,
                        )
                except Exception as e:
                    emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"Error stamping {py_file}: {e}",
                        context={"file": str(py_file)},
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
                        emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"Failed to stamp {yaml_file}: {result.stderr}",
                            context={"file": str(yaml_file)},
                            event_bus=self._event_bus,
                        )
                except Exception as e:
                    emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"Error stamping {yaml_file}: {e}",
                        context={"file": str(yaml_file)},
                        event_bus=self._event_bus,
                    )
            emit_log_event_sync(
                LogLevelEnum.INFO,
                "Initial stamping completed",
                context={"stamped_files": len(python_files) + len(yaml_files)},
                event_bus=self._event_bus,
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to run initial stamping: {e}",
                context={"node_path": str(node_path)},
                event_bus=self._event_bus,
            )
            raise

    def generate_onextree(self, node_path: Path) -> None:
        """
        Generate .onextree file for the new node.

        Args:
            node_path: Path to the generated node directory
        """
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Generating .onextree for {node_path}",
            context={"node_path": str(node_path)},
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
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    "Successfully generated .onextree",
                    context={"output_path": str(node_path / ".onextree")},
                    event_bus=self._event_bus,
                )
            else:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Failed to generate .onextree: {result.stderr}",
                    context={"node_path": str(node_path)},
                    event_bus=self._event_bus,
                )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Error generating .onextree: {e}",
                context={"node_path": str(node_path)},
                event_bus=self._event_bus,
            )
            raise

    def run_parity_validation(self, node_path: Path) -> Dict[str, Any]:
        """
        Run parity validation on the generated node.

        Args:
            node_path: Path to the generated node directory

        Returns:
            Dictionary containing validation results
        """
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Running parity validation on {node_path}",
            context={"node_path": str(node_path)},
            event_bus=self._event_bus,
        )
        try:
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "onex",
                    "run",
                    "parity_validator_node",
                    "--args",
                    f'["--nodes-directory", "{node_path}", "--format", "json"]',
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            if result.returncode == 0:
                import json

                try:
                    validation_data = json.loads(result.stdout)
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        "Parity validation completed",
                        context={
                            "validation_status": validation_data.get(
                                "status", "unknown"
                            )
                        },
                        event_bus=self._event_bus,
                    )
                    return validation_data
                except json.JSONDecodeError:
                    emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        "Could not parse parity validation output",
                        context={"stdout": result.stdout},
                        event_bus=self._event_bus,
                    )
                    return {"status": "unknown", "output": result.stdout}
            else:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Parity validation failed: {result.stderr}",
                    context={"node_path": str(node_path)},
                    event_bus=self._event_bus,
                )
                return {"status": "failed", "error": result.stderr}
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Error running parity validation: {e}",
                context={"node_path": str(node_path)},
                event_bus=self._event_bus,
            )
            return {"status": "error", "error": str(e)}

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
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"Created directory: {dir_path}",
                context={"directory": str(dir_path)},
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
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"Created file: {file_path}",
                context={"file": str(file_path)},
                event_bus=self._event_bus,
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to write file {file_path}: {e}",
                context={"file": str(file_path)},
                event_bus=self._event_bus,
            )
            raise
