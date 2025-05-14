#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: utils
# namespace: omninode.tools.utils
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:01+00:00
# last_modified_at: 2025-04-27T18:13:01+00:00
# entrypoint: utils.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""utils.py containers.foundation.src.foundation.script.validate.utils.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic functions
T = TypeVar("T")


class ValidationCache:
    """Cache for validation results."""

    def __init__(
        self, cache_dir: Path = Path(".validation_cache"), duration: int = 3600
    ):
        """Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            duration: Cache duration in seconds
        """
        self.cache_dir = cache_dir
        self.duration = duration
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, validator_name: str, target: Path, config: Dict) -> str:
        """Generate a cache key from inputs.

        Args:
            validator_name: Name of the validator
            target: Path being validated
            config: Validator configuration

        Returns:
            str: Cache key
        """
        # Get file modification time if target is a file
        mtime = os.path.getmtime(target) if target.is_file() else 0

        # Create string to hash
        to_hash = f"{validator_name}:{str(target)}:{mtime}:{json.dumps(config, sort_keys=True)}"

        # Generate hash
        return hashlib.sha256(to_hash.encode()).hexdigest()

    def get(self, validator_name: str, target: Path, config: Dict) -> Optional[Dict]:
        """Get cached validation results.

        Args:
            validator_name: Name of the validator
            target: Path being validated
            config: Validator configuration

        Returns:
            Optional[Dict]: Cached results or None if not found/expired
        """
        key = self._get_cache_key(validator_name, target, config)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            # Check if cache has expired
            cached_time = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - cached_time > timedelta(seconds=self.duration):
                return None

            return data["results"]
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None

    def set(self, validator_name: str, target: Path, config: Dict, results: Dict):
        """Cache validation results.

        Args:
            validator_name: Name of the validator
            target: Path being validated
            config: Validator configuration
            results: Validation results to cache
        """
        key = self._get_cache_key(validator_name, target, config)
        cache_file = self.cache_dir / f"{key}.json"

        try:
            data = {"timestamp": datetime.now().isoformat(), "results": results}
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")


def run_parallel(
    func: Callable[[T], Any], items: List[T], max_workers: int = 4
) -> List[Tuple[T, Any]]:
    """Run a function on items in parallel.

    Args:
        func: Function to run
        items: Items to process
        max_workers: Maximum number of parallel workers

    Returns:
        List[Tuple[T, Any]]: List of (item, result) tuples
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item): item for item in items}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append((item, result))
            except Exception as e:
                logger.error(f"Error processing {item}: {e}")
                results.append((item, None))
    return results


def generate_report(results: Dict[str, Dict], format: str = "text") -> str:
    """Generate a validation report.

    Args:
        results: Dictionary of validator results
        format: Output format (text, json, html)

    Returns:
        str: Formatted report
    """
    if format == "json":
        return json.dumps(results, indent=2)
    elif format == "html":
        return _generate_html_report(results)
    else:  # text
        return _generate_text_report(results)


def _generate_text_report(results: Dict[str, Dict]) -> str:
    """Generate a text format report."""
    lines = ["Validation Report", "================"]

    for validator, data in results.items():
        lines.append(f"\n{validator}:")
        lines.append("-" * (len(validator) + 1))

        if "errors" in data:
            lines.append("\nErrors:")
            for error in data["errors"]:
                lines.append(f"- {error}")

        if "warnings" in data:
            lines.append("\nWarnings:")
            for warning in data["warnings"]:
                lines.append(f"- {warning}")

    return "\n".join(lines)


def _generate_html_report(results: Dict[str, Dict]) -> str:
    """Generate an HTML format report."""
    html = [
        "<html><head><style>",
        "body { font-family: Arial, sans-serif; margin: 20px; }",
        ".validator { margin-bottom: 20px; }",
        ".errors { color: red; }",
        ".warnings { color: orange; }",
        "</style></head><body>",
        "<h1>Validation Report</h1>",
    ]

    for validator, data in results.items():
        html.append('<div class="validator">')
        html.append(f"<h2>{validator}</h2>")

        if "errors" in data:
            html.append('<div class="errors">')
            html.append("<h3>Errors:</h3><ul>")
            for error in data["errors"]:
                html.append(f"<li>{error}</li>")
            html.append("</ul></div>")

        if "warnings" in data:
            html.append('<div class="warnings">')
            html.append("<h3>Warnings:</h3><ul>")
            for warning in data["warnings"]:
                html.append(f"<li>{warning}</li>")
            html.append("</ul></div>")

        html.append("</div>")

    html.append("</body></html>")
    return "\n".join(html)


def load_json_file(path: Path) -> Dict:
    """Load and parse a JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Dict: Parsed JSON data
    """
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {path}: {e}")
        return {}
