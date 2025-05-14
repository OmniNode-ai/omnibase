from typing import List, Optional, Tuple
import re
from foundation.protocol.protocol_util_header import ProtocolUtilHeader
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END

class UtilHeader(ProtocolUtilHeader):
    """
    Implementation of ProtocolUtilHeader for Python header normalization utilities.
    All methods are DI-compliant and ready for registry registration.
    """
    def extract_shebang(self, lines: list[str]) -> tuple[Optional[str], list[str]]:
        """Extract and remove the shebang line from the given lines, if present."""
        for idx, line in enumerate(lines[:5]):
            if line.startswith("#!"):
                return line, lines[:idx] + lines[idx+1:]
        return None, lines

    def extract_module_docstring(self, lines: list[str]) -> tuple[Optional[str], list[str]]:
        """Extract and remove the module docstring from the given lines, if present."""
        in_docstring = False
        docstring = []
        start = None
        for idx, line in enumerate(lines):
            if not in_docstring and line.strip().startswith(("'"*3, '"'*3)):
                in_docstring = True
                start = idx
                docstring.append(line)
                if line.strip().endswith(("'"*3, '"'*3)) and len(line.strip()) > 6:
                    # Single-line docstring
                    return line, lines[:idx] + lines[idx+1:]
            elif in_docstring:
                docstring.append(line)
                if line.strip().endswith(("'"*3, '"'*3)):
                    return '\n'.join(docstring), lines[:start] + lines[idx+1:]
            elif line.strip() and not line.strip().startswith('#'):
                break
        return None, lines

    def extract_future_imports(self, lines: list[str]) -> tuple[list[str], list[str]]:
        """Extract and remove all contiguous 'from __future__ import ...' lines at the top of the file."""
        future_imports = []
        idx = 0
        for line in lines:
            if line.strip().startswith('from __future__ import '):
                future_imports.append(line)
                idx += 1
            else:
                break
        return future_imports, lines[idx:]

    def normalize_python_header(self, lines: list[str]) -> tuple[list[str], list[str]]:
        """
        Extract shebang, docstring, and future imports, returning (header_lines, rest_lines).
        Header lines are in canonical order: shebang, docstring, future imports.
        """
        shebang, lines_wo_shebang = self.extract_shebang(lines)
        docstring, lines_wo_docstring = self.extract_module_docstring(lines_wo_shebang)
        future_imports, rest = self.extract_future_imports(lines_wo_docstring)
        header = []
        if shebang:
            header.append(shebang)
        if docstring:
            header.append(docstring)
        header.extend(future_imports)
        return header, rest

    def update_metadata_block_hash(self, text: str, hash_value: str) -> str | None:
        """
        Locate the metadata block, update the tree_hash, and return the updated file content.
        If no metadata block is found, return None.
        """
        import yaml
        import re
        lines = text.splitlines()
        # Find start and end of metadata block
        start_idx = None
        end_idx = None
        start_marker = f"# {OMNINODE_METADATA_START}"
        end_marker = f"# {OMNINODE_METADATA_END}"
        for i, line in enumerate(lines):
            if line.strip().startswith(start_marker):
                start_idx = i
            if line.strip().startswith(end_marker):
                end_idx = i
                break
        if start_idx is None or end_idx is None:
            return None
        # Extract block lines (excluding markers)
        block_lines = lines[start_idx+1:end_idx]
        # Remove leading comment prefix
        decommented = [re.sub(r"^# ?", "", l) for l in block_lines]
        block_str = "\n".join(decommented)
        try:
            meta = yaml.safe_load(block_str)
        except Exception:
            return None
        if not isinstance(meta, dict):
            return None
        meta['tree_hash'] = hash_value
        # Reconstruct block
        new_block = [start_marker]
        for l in yaml.safe_dump(meta, sort_keys=True).splitlines():
            new_block.append(f"# {l}")
        new_block.append(end_marker)
        # Replace block in file
        updated_lines = lines[:start_idx] + new_block + lines[end_idx+1:]
        return "\n".join(updated_lines)

def extract_shebang(lines: List[str]) -> Tuple[Optional[str], List[str]]:
    """
    Find a shebang (#!...) anywhere in the file, remove it, and return (shebang, lines_without_shebang).
    If no shebang is found, returns (None, lines).
    """
    shebang = None
    new_lines = []
    for line in lines:
        if shebang is None and line.startswith("#!"):
            shebang = line
        else:
            new_lines.append(line)
    return shebang, new_lines

def extract_module_docstring(lines: List[str]) -> Tuple[Optional[str], List[str]]:
    """
    Find a module docstring (triple-quoted string at the top, after comments/blank lines), remove it, and return (docstring, lines_without_docstring).
    If no docstring is found, returns (None, lines).
    """
    docstring = None
    start = None
    end = None
    # Skip comments and blank lines
    idx = 0
    while idx < len(lines) and (lines[idx].strip().startswith("#") or not lines[idx].strip()):
        idx += 1
    # Check for triple-quoted docstring
    if idx < len(lines) and (lines[idx].strip().startswith('"""') or lines[idx].strip().startswith("'''")):
        quote = lines[idx].strip()[:3]
        start = idx
        idx += 1
        while idx < len(lines):
            if quote in lines[idx]:
                end = idx
                break
            idx += 1
        if start is not None and end is not None:
            docstring = "\n".join(lines[start:end+1])
            new_lines = lines[:start] + lines[end+1:]
            return docstring, new_lines
    return None, lines

def extract_future_imports(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Find all contiguous 'from __future__ import ...' lines at the top (after shebang), remove them, and return (future_imports, lines_without_future_imports).
    """
    future_imports = []
    idx = 0
    while idx < len(lines) and lines[idx].strip().startswith("from __future__ import"):
        future_imports.append(lines[idx])
        idx += 1
    return future_imports, lines[idx:]

def normalize_python_header(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extract and normalize the canonical Python header: shebang, future imports, docstring.
    Returns (header_lines, rest_of_file_lines) in canonical order.
    """
    shebang, lines_wo_shebang = extract_shebang(lines)
    future_imports, rest = extract_future_imports(lines_wo_shebang)
    docstring, rest = extract_module_docstring(rest)
    header = []
    if shebang:
        header.append(shebang)
    header.extend(future_imports)
    if docstring:
        header.append(docstring)
    return header, rest 