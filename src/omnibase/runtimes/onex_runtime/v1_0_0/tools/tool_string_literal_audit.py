#!/usr/bin/env python3
"""
ONEX Runtime Tool: String Literal Audit

Scans a node directory for all string literals in Python files, and reports:
- All string literals (excluding docstrings, comments, Enum value assignments, and any in constants.py or error_codes.py)
- Whether each string matches a constant in node-local error_codes.py/constants.py or in src/omnibase/constants.py
- The file and line number for each occurrence

Usage:
    python tool_string_literal_audit.py <node_path>
    python tool_string_literal_audit.py <node_path> --propose-replacements
    python tool_string_literal_audit.py <node_path> --add-to-shared-constants
    python tool_string_literal_audit.py <node_path> --apply-replacements

--propose-replacements: Dry-run mode. Proposes sed commands to replace string literals with matching constant names (no files are modified).
--add-to-shared-constants: Dry-run mode. Proposes new constant names and code to add unmatched string literals to src/omnibase/constants.py (no files are modified). Enforces uniqueness by value: skips if value is already present (under any name), flags name/value conflicts, and only adds truly new (name, value) pairs.
--apply-replacements: Actually replaces all string literals that match a constant (node-local or shared) with the constant name in-place in .py files. Only replaces exact matches. Prints a summary of changes made.

Note: The script ignores string literals used as values in Enum class assignments, and ignores all replacements in constants.py and error_codes.py (these should remain as string literals).

Intended for standards enforcement and migration audits.
"""
import ast
import os
import sys
from pathlib import Path
from typing import Dict, Set, Tuple, List
import shlex
import re
import hashlib
import fileinput

# --- Utility: Load all string constants from a Python file ---
def load_constants_from_pyfile(pyfile: Path) -> Dict[str, str]:
    constants = {}
    if not pyfile.exists():
        return constants
    try:
        with open(pyfile, 'r', encoding='utf-8') as f:
            node = ast.parse(f.read(), filename=str(pyfile))
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        constants[target.id] = stmt.value.value
            elif isinstance(stmt, ast.ClassDef):
                # Enum or error code class
                for sub in stmt.body:
                    if isinstance(sub, ast.Assign):
                        for target in sub.targets:
                            if isinstance(target, ast.Name) and isinstance(sub.value, ast.Constant) and isinstance(sub.value.value, str):
                                constants[target.id] = sub.value.value
    except Exception as e:
        print(f"[WARN] Could not parse constants from {pyfile}: {e}")
    return constants

# --- Utility: Recursively find all .py files in a directory ---
def find_py_files(root: Path) -> List[Path]:
    return [p for p in root.rglob('*.py') if p.is_file()]

# --- Utility: Extract all string literals from a .py file (excluding docstrings/comments) ---
def extract_string_literals(pyfile: Path) -> List[Tuple[str, int]]:
    literals = []
    try:
        with open(pyfile, 'r', encoding='utf-8') as f:
            source = f.read()
        node = ast.parse(source, filename=str(pyfile))
        for n in ast.walk(node):
            # Exclude docstrings (only top-level/module, class, or function docstrings)
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                # Only docstring if first statement in module/class/function
                parent = getattr(n, 'parent', None)
                if parent and hasattr(parent, 'body') and parent.body and parent.body[0] is n:
                    continue  # skip docstring
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                # Exclude docstrings (handled above)
                if not hasattr(n, 'parent') or not (isinstance(n.parent, ast.Expr) and isinstance(n.parent.value, ast.Constant)):
                    literals.append((n.value, n.lineno))
    except Exception as e:
        print(f"[WARN] Could not parse string literals from {pyfile}: {e}")
    return literals

# --- Patch AST nodes to track parent relationships (for docstring exclusion) ---
def attach_parents(node):
    for child in ast.iter_child_nodes(node):
        child.parent = node
        attach_parents(child)

# --- Main audit logic ---
def audit_strings(node_path: Path, node_constants: Dict[str, str], shared_constants: Dict[str, str], py_files: List[Path]):
    report = []  # List of (string, file, line, match_status, constant_name)
    for pyfile in py_files:
        # Ignore constants.py and error_codes.py
        if pyfile.name in ("constants.py", "error_codes.py"):
            continue
        try:
            with open(pyfile, 'r', encoding='utf-8') as f:
                source = f.read()
            node = ast.parse(source, filename=str(pyfile))
            attach_parents(node)
            # Find all Enum class value assignments
            enum_value_lines = set()
            for n in ast.walk(node):
                if isinstance(n, ast.ClassDef):
                    bases = [b.id for b in n.bases if isinstance(b, ast.Name)]
                    if 'Enum' in bases:
                        for sub in n.body:
                            if isinstance(sub, ast.Assign):
                                if isinstance(sub.value, ast.Constant) and isinstance(sub.value.value, str):
                                    enum_value_lines.add(sub.value.lineno)
            for n in ast.walk(node):
                if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                    parent = getattr(n, 'parent', None)
                    if parent and hasattr(parent, 'body') and parent.body and parent.body[0] is n:
                        continue  # skip docstring
                if isinstance(n, ast.Constant) and isinstance(n.value, str):
                    if not hasattr(n, 'parent') or not (isinstance(n.parent, ast.Expr) and isinstance(n.parent.value, ast.Constant)):
                        s = n.value
                        line = n.lineno
                        # Ignore Enum value assignments
                        if line in enum_value_lines:
                            continue
                        match = None
                        const_name = None
                        if s in node_constants.values():
                            match = 'node-local'
                            const_name = [k for k, v in node_constants.items() if v == s][0]
                        elif s in shared_constants.values():
                            match = 'shared'
                            const_name = [k for k, v in shared_constants.items() if v == s][0]
                        else:
                            match = 'none'
                        report.append((s, str(pyfile.relative_to(node_path)), line, match, const_name))
        except Exception as e:
            print(f"[WARN] Could not process {pyfile}: {e}")
    return report

# --- Propose sed replacements for string literals matching constants ---
def propose_sed_replacements(node_path: Path, report: List[Tuple[str, str, int, str, str]]):
    print("\n=== Proposed sed Replacements (Dry Run) ===")
    replacements = []
    for s, file, line, match, const_name in report:
        if match in ('node-local', 'shared') and const_name:
            # Escape for sed (single quotes)
            sed_str = s.replace("'", "'\\''")
            # Only replace exact string literals (with quotes)
            sed_cmd = f"sed -i '' -e 's/{shlex.quote('"' + s + '"')}/{const_name}/g' {shlex.quote(str(node_path / file))}"
            print(f"{sed_cmd}  # {file}:{line}  {repr(s)} -> {const_name}")
            replacements.append((file, line, s, const_name, sed_cmd))
    print(f"\nTotal proposed replacements: {len(replacements)}")
    if not replacements:
        print("No string literals matched constants for replacement.")
    return replacements

# --- Propose new shared constants for unmatched string literals ---
def propose_add_to_shared_constants(report: List[Tuple[str, str, int, str, str]], shared_constants: Dict[str, str], constants_py: Path):
    print("\n=== Proposed Additions to src/omnibase/constants.py (Uniqueness Enforced, Dry Run) ===")
    # Build value->name and name->value dicts for all existing constants
    value_to_name = {v: k for k, v in shared_constants.items()}
    name_to_value = {k: v for k, v in shared_constants.items()}
    additions = []
    skipped_by_value = []
    conflicts = []
    used_names = set(name_to_value.keys())
    generic_names = {"YES", "NO", "TRUE", "FALSE", "1", "0", "MESSAGE", "ERROR", "DESCRIPTION", "ID", "NAME", "VALUE", "TYPE", "DATA", "INFO", "RESULT", "STATUS", "FIELD", "OPTION", "KEY", "CODE", "LEVEL", "PATH", "FILE", "LINE", "TEXT", "TITLE", "COUNT", "INDEX", "ITEM", "ENTRY", "OUTPUT", "INPUT", "DATE", "TIME", "USER", "LOG", "DEBUG", "WARN", "WARNING", "INFO", "SUCCESS", "FAIL", "FAILED", "PASSED", "OK", "NONE", "NULL", "ON", "OFF"}
    for s, file, line, match, const_name in report:
        if match == 'none' and s.strip():
            base = re.sub(r'[^a-zA-Z0-9]+', '_', s.strip()).upper().strip('_')
            if not base:
                base = f"AUTO_CONST_{hashlib.md5(s.encode()).hexdigest()[:8]}"
            name = base
            is_generic = name in generic_names or base in generic_names
            # Uniqueness by value
            if s in value_to_name:
                skipped_by_value.append((name, s, value_to_name[s]))
                continue
            # Name conflict with different value
            if name in name_to_value and name_to_value[name] != s:
                conflicts.append((name, s, name_to_value[name]))
                continue
            additions.append((name, s, file, line, is_generic))
            used_names.add(name)
            value_to_name[s] = name
    if additions:
        print("\n# --- Add the following to src/omnibase/constants.py ---\n")
        for name, s, file, line, is_generic in additions:
            warn = []
            if is_generic:
                warn.append("[GENERIC NAME]")
            warn_str = " ".join(warn)
            print(f"{name} = {repr(s)}  # from {file}:{line} {warn_str}")
            if warn_str:
                print(f"  # WARNING: {warn_str} Review this constant name for clarity and uniqueness.")
    else:
        print("No unmatched string literals found for addition.")
    if skipped_by_value:
        print(f"\n# Skipped (already present by value):")
        for name, s, existing_name in skipped_by_value:
            print(f"# {name} = {repr(s)}  # Already present as {existing_name}")
    if conflicts:
        print(f"\n# Conflicts (name already used for different value, not added):")
        for name, s, existing_value in conflicts:
            print(f"# {name} = {repr(s)}  # Name already used for {repr(existing_value)}")
    print(f"\nTotal proposed new constants: {len(additions)}")
    print(f"Total skipped (already present by value): {len(skipped_by_value)}")
    print(f"Total conflicts (name collision): {len(conflicts)}")
    return additions

def apply_replacements(node_path: Path, report: List[Tuple[str, str, int, str, str]]):
    print("\n=== Applying Replacements (In-Place) ===")
    # Build a mapping: file -> list of (line, old, new)
    replacements_by_file = {}
    for s, file, line, match, const_name in report:
        if file.endswith("constants.py") or file.endswith("error_codes.py"):
            continue
        if match in ('node-local', 'shared') and const_name:
            replacements_by_file.setdefault(file, []).append((line, s, const_name))
    changed_files = set()
    for file, repls in replacements_by_file.items():
        abs_path = node_path / file
        # Read all lines
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        changed = False
        for i, line_text in enumerate(lines):
            for _, old, new in repls:
                # Replace only exact string literal occurrences (with quotes)
                # Handles both single and double quotes
                for quote in ("'", '"'):
                    target = f"{quote}{old}{quote}"
                    if target in line_text:
                        line_text = line_text.replace(target, new)
                        changed = True
            lines[i] = line_text
        if changed:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            changed_files.add(file)
            print(f"[CHANGED] {file}")
    print(f"\nTotal files changed: {len(changed_files)}")
    if not changed_files:
        print("No replacements made.")

# --- Main CLI logic ---
def main():
    if len(sys.argv) < 2:
        print("Usage: python tool_string_literal_audit.py <node_path> [--propose-replacements] [--add-to-shared-constants] [--apply-replacements]")
        sys.exit(1)
    node_path = Path(sys.argv[1]).resolve()
    if not node_path.exists() or not node_path.is_dir():
        print(f"[ERROR] Not a directory: {node_path}")
        sys.exit(1)
    propose = '--propose-replacements' in sys.argv
    add_consts = '--add-to-shared-constants' in sys.argv
    apply = '--apply-replacements' in sys.argv
    # Find node-local constant files
    error_codes_py = node_path / 'v1_0_0' / 'error_codes.py'
    constants_py = node_path / 'v1_0_0' / 'constants.py'
    node_constants = load_constants_from_pyfile(error_codes_py)
    node_constants.update(load_constants_from_pyfile(constants_py))
    # Load shared/common constants
    shared_constants_py = Path(__file__).parent.parent.parent.parent / 'constants.py'
    shared_constants = load_constants_from_pyfile(shared_constants_py)
    # Find all .py files in the node directory
    py_files = find_py_files(node_path)
    # Audit string literals
    report = audit_strings(node_path, node_constants, shared_constants, py_files)
    if propose:
        propose_sed_replacements(node_path, report)
    elif add_consts:
        propose_add_to_shared_constants(report, shared_constants, shared_constants_py)
    elif apply:
        apply_replacements(node_path, report)
    else:
        # Print audit report
        print("\n=== String Literal Audit Report ===")
        for s, file, line, match, const_name in sorted(report, key=lambda x: (x[3], x[0])):
            print(f"[{match.upper():9}] {file}:{line}: {repr(s)}")
        print(f"\nTotal string literals: {len(report)}")
        print(f"Node-local constant matches: {sum(1 for r in report if r[3]=='node-local')}")
        print(f"Shared constant matches: {sum(1 for r in report if r[3]=='shared')}")
        print(f"Unmatched: {sum(1 for r in report if r[3]=='none')}")

if __name__ == "__main__":
    main() 