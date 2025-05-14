# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_bootstrap_import"
# namespace: "omninode.tools.python_validate_bootstrap_import"
# meta_type: "validator"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:30:00+00:00"
# last_modified_at: "2025-05-07T11:30:00+00:00"
# entrypoint: "python_validate_bootstrap_import.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Validator for ensuring Python entrypoints import and call the bootstrap() function.

This validator checks that any Python file that is an entrypoint (has `if __name__ == "__main__"`)
imports and calls the bootstrap() function from foundation.bootstrap.bootstrap.
"""

import ast
import sys
from pathlib import Path
from typing import Optional, List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedStatus, UnifiedMessageModel
from foundation.model.model_metadata import MetadataBlockModel

class BootstrapImportValidator(ProtocolValidate):
    """Validator for ensuring Python entrypoints import and call the bootstrap() function."""

    def __init__(self, logger: Optional[ProtocolLogger] = None, utility_registry=None):
        """Initialize the validator."""
        super().__init__(logger=logger, utility_registry=utility_registry)

    @classmethod
    def metadata(cls) -> MetadataBlockModel:
        """Get metadata for this validator."""
        return MetadataBlockModel(
            metadata_version="0.1",
            name="python_bootstrap_import",
            namespace="omninode.tools.python_validate_bootstrap_import",
            version="1.0.0",
            entrypoint="python_validate_bootstrap_import.py",
            protocols_supported=["O.N.E. v0.1"],
            protocol_version="0.1.0",
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-05-07T11:30:00+00:00",
            last_modified_at="2025-05-07T11:30:00+00:00",
            description="Validator for Python entrypoint bootstrap import.",
            tags=["python", "bootstrap", "validator"],
            dependencies=[],
            config={}
        )

    def validate(self, path: Path) -> UnifiedResultModel:
        """Validate that the file imports and calls bootstrap() if it's an entrypoint."""
        if not path.is_file():
            return UnifiedResultModel(
                status=UnifiedStatus.success,
                messages=[]
            )

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return UnifiedResultModel(
                status=UnifiedStatus.error,
                messages=[
                    UnifiedMessageModel(
                        severity="error",
                        level="error",
                        summary=f"Failed to read file: {e}",
                        detail=str(e)
                    )
                ]
            )

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Not a valid Python file, so it can't be an entrypoint
            return UnifiedResultModel(
                status=UnifiedStatus.success,
                messages=[]
            )

        # Check if this is an entrypoint
        is_entrypoint = False
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                    if isinstance(node.test.ops[0], ast.Eq):
                        if isinstance(node.test.comparators[0], ast.Constant) and node.test.comparators[0].value == "__main__":
                            is_entrypoint = True
                            break

        if not is_entrypoint:
            return UnifiedResultModel(
                status=UnifiedStatus.success,
                messages=[]
            )

        # Check for bootstrap import
        has_bootstrap_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "foundation.bootstrap.bootstrap":
                    for name in node.names:
                        if name.name == "bootstrap":
                            has_bootstrap_import = True
                            break
            elif isinstance(node, ast.Import):
                for name in node.names:
                    if name.name == "foundation.bootstrap.bootstrap":
                        has_bootstrap_import = True
                        break

        # Check for bootstrap call
        has_bootstrap_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "bootstrap":
                    has_bootstrap_call = True
                    break
                elif isinstance(node.func, ast.Attribute):
                    # Handle foundation.bootstrap.bootstrap.bootstrap()
                    attr = node.func
                    parts = []
                    while isinstance(attr, ast.Attribute):
                        parts.append(attr.attr)
                        attr = attr.value
                    if isinstance(attr, ast.Name):
                        parts.append(attr.id)
                    parts.reverse()
                    if parts == ["foundation", "bootstrap", "bootstrap", "bootstrap"]:
                        has_bootstrap_call = True
                        break

        messages: List[UnifiedMessageModel] = []
        if not has_bootstrap_import:
            messages.append(
                UnifiedMessageModel(
                    severity="error",
                    level="error",
                    summary="Missing bootstrap import",
                    detail="Entrypoint must import bootstrap from foundation.bootstrap.bootstrap"
                )
            )
        if not has_bootstrap_call:
            messages.append(
                UnifiedMessageModel(
                    severity="error",
                    level="error",
                    summary="Missing bootstrap call",
                    detail="Entrypoint must call bootstrap() before any other code"
                )
            )

        return UnifiedResultModel(
            status=UnifiedStatus.error if messages else UnifiedStatus.success,
            messages=messages
        )

    def main(self) -> int:
        """CLI entrypoint."""
        if len(sys.argv) < 2:
            print("Usage: python_validate_bootstrap_import.py <file>")
            return 1

        path = Path(sys.argv[1])
        if not path.exists():
            print(f"Bootstrap import validation FAILED: File {path} does not exist")
            return 1

        result = self.validate(path)
        if result.status == UnifiedStatus.error:
            print("Bootstrap import validation FAILED:")
            for msg in result.messages:
                print(f"  - {msg.summary}")
            return 1
        else:
            print("Bootstrap import validation PASSED.")
            return 0

if __name__ == "__main__":
    sys.exit(BootstrapImportValidator().main()) 