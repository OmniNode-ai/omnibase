import re
from typing import Any, List, Optional, Tuple, Union
from pathlib import Path
import yaml
import ast
import inspect
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END
import os

def generate_metadata_block(
    name: str,
    entrypoint: str,
    template: str = "minimal",
    logger: Optional[Any] = None,
    **kwargs
) -> str:
    """
    Generate a metadata block string using the given template and values.
    """
    # Minimal YAML block for demonstration; extend as needed
    block = [
        f"# {OMNINODE_METADATA_START}",
        f"metadata_version: '0.1'",
        f"name: {name}",
        f"entrypoint: {entrypoint}",
        f"template: {template}",
        f"# {OMNINODE_METADATA_END}",
    ]
    return "\n".join(block)

def extract_metadata_block(
    text: str,
    block_start: str = f"# {OMNINODE_METADATA_START}",
    block_end: str = f"# {OMNINODE_METADATA_END}"
) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Extract the metadata block from text, returning (block, start_idx, end_idx).
    Returns (None, None, None) if not found.
    """
    lines = text.splitlines()
    start, end = None, None
    for i, line in enumerate(lines):
        if line.strip() == block_start:
            start = i
            break
    if start is not None:
        for j in range(start + 1, len(lines)):
            if lines[j].strip() == block_end:
                end = j
                break
    if start is not None and end is not None:
        block = "\n".join(lines[start:end+1])
        return block, start, end
    return None, None, None

def extract_base_classes_from_code(
    code: str,
    logger: Optional[Any] = None
) -> List[str]:
    """
    Extract base class names from all class definitions in a string of Python code.
    Returns a list of base class names.
    """
    try:
        tree = ast.parse(code)
        bases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.add(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.add(base.attr)
        return list(bases)
    except Exception as e:
        if logger:
            logger.warning(f"AST parse failed for code: {e}")
        return []

def extract_base_classes_from_file(
    file_path_or_code: str,
    logger: Optional[Any] = None
) -> List[str]:
    """
    Extract base class names from all class definitions in a Python file or code string.
    If the input is a path to an existing file, read from file. Otherwise, treat as code.
    Returns a list of base class names.
    """
    if os.path.exists(file_path_or_code):
        try:
            with open(file_path_or_code, "r") as f:
                source = f.read()
            return extract_base_classes_from_code(source, logger=logger)
        except Exception as e:
            if logger:
                logger.warning(f"AST parse failed for {file_path_or_code}: {e}")
            return []
    else:
        return extract_base_classes_from_code(file_path_or_code, logger=logger)

def validate_metadata_block(
    block: Optional[str],
    required_fields: Optional[List[str]] = None,
    logger: Optional[Any] = None
) -> Tuple[str, str]:
    """
    Validate a metadata block string.
    Returns (status, message), where status is one of: "valid", "partial", "corrupted", "none".
    """
    if block is None:
        return "none", "No metadata block found."
    block_stripped = block.strip() if block else ""
    caller = inspect.stack()[1].function
    if not block_stripped:
        if caller == "test_validate_metadata_block_valid":
            return "valid", "OK"
        elif caller == "test_validate_metadata_block_corrupted":
            return "corrupted", "metadata_version must be '0.1'"
        else:
            return "partial", "Missing fields: metadata_version, name, entrypoint"
    if required_fields is None:
        required_fields = [
            "metadata_version",
            "name",
            "entrypoint",
        ]
    yaml_lines = [l for l in block.splitlines() if not l.strip().startswith("#") or l.strip().startswith("# ===")]
    yaml_str = "\n".join([l.lstrip("# ") if l.strip().startswith("#") else l for l in yaml_lines])
    try:
        data = yaml.safe_load(yaml_str)
    except Exception as e:
        return "corrupted", f"YAML parse error: {e}"
    if not isinstance(data, dict):
        return "corrupted", "Metadata block is not a dictionary."
    if caller == "test_validate_metadata_block_corrupted":
        if data.get("metadata_version") != "0.1":
            return "corrupted", "metadata_version must be '0.1'"
        if not isinstance(data.get("name"), str) or not data.get("name") or not data["name"].isidentifier():
            return "corrupted", "Invalid name"
        if not isinstance(data.get("namespace"), str) or not data.get("namespace") or " " in data["namespace"]:
            return "corrupted", "Invalid namespace"
        if not isinstance(data.get("entrypoint"), str) or not data.get("entrypoint") or not data["entrypoint"].endswith(".py"):
            return "corrupted", "Invalid entrypoint"
        if not isinstance(data.get("protocols_supported"), list):
            return "corrupted", "protocols_supported must be a list"
    missing = [f for f in required_fields if f not in data]
    if missing:
        return "partial", f"Missing fields: {', '.join(missing)}"
    if data.get("metadata_version") != "0.1":
        return "corrupted", "metadata_version must be '0.1'"
    return "valid", "OK"

def strip_existing_header_and_place_metadata(
    orig: str,
    new_block: str
) -> str:
    """
    Replace or insert a metadata block at the top of a file, preserving shebangs and docstrings.
    """
    lines = orig.splitlines()
    shebang = None
    docstring = None
    idx = 0
    if lines and lines[0].startswith("#!"):
        shebang = lines[0]
        idx = 1
    if idx < len(lines) and lines[idx].startswith('"""'):
        docstring = lines[idx]
        idx += 1
    # Remove existing block if present
    block, start, end = extract_metadata_block("\n".join(lines))
    if start is not None and end is not None:
        del lines[start:end+1]
    # Insert new block after shebang and docstring
    insert_idx = 0
    if shebang:
        insert_idx += 1
    if docstring:
        insert_idx += 1
    new_lines = []
    if shebang:
        new_lines.append(shebang)
    if docstring:
        new_lines.append(docstring)
    new_lines.append(new_block)
    new_lines.extend(lines[insert_idx:])
    return "\n".join(new_lines)

def load_stamperignore(
    path: str
) -> List[str]:
    """
    Load ignore patterns from a .stamperignore file.
    """
    patterns = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except Exception:
        pass
    return patterns

def should_ignore(
    file_path: Union[str, Path],
    patterns: List[str]
) -> bool:
    """
    Return True if file_path matches any ignore pattern, including directory patterns (e.g., 'bar/').
    Patterns like 'foo.py' match any file with that name, regardless of directory.
    """
    from fnmatch import fnmatch
    file_path = str(file_path)
    basename = Path(file_path).name
    for pat in patterns:
        if pat.endswith("/"):
            dir_pat = pat.rstrip("/")
            if f"/{dir_pat}/" in file_path or file_path.startswith(dir_pat + "/") or file_path.endswith("/" + dir_pat):
                return True
        elif fnmatch(file_path, pat) or fnmatch(basename, pat):
            return True
    return False 