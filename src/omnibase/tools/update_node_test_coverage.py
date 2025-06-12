import argparse
from pathlib import Path
import sys
import yaml
from typing import Optional
import enum

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.protocol.protocol_coverage_provider import ProtocolCoverageProvider
from omnibase.core.core_bootstrap import emit_log_event_sync
from omnibase.enums import LogLevelEnum

class CoverageXMLProvider:
    """
    Default ProtocolCoverageProvider implementation for coverage.xml (Cobertura/pytest-cov XML).
    """
    def get_coverage_percentage(self, source: Path) -> float:
        import xml.etree.ElementTree as ET
        tree = ET.parse(source)
        root = tree.getroot()
        coverage_attr = root.attrib.get("line-rate") or root.attrib.get("branch-rate")
        if coverage_attr:
            return float(coverage_attr) * 100.0
        # Cobertura format
        coverage = root.attrib.get("coverage")
        if coverage:
            return float(coverage)
        # Try summary element
        summary = root.find(".//coverage")
        if summary is not None and "line-rate" in summary.attrib:
            return float(summary.attrib["line-rate"]) * 100.0
        raise ValueError(f"Could not extract coverage from {source}")

PROVIDER_REGISTRY = {
    "xml": CoverageXMLProvider(),
}

def get_provider(name: Optional[str]) -> ProtocolCoverageProvider:
    if not name or name == "xml":
        return PROVIDER_REGISTRY["xml"]
    raise ValueError(f"Unknown coverage provider: {name}")

def enum_to_value(obj):
    if isinstance(obj, dict):
        return {k: enum_to_value(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [enum_to_value(i) for i in obj]
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        return obj

def main():
    parser = argparse.ArgumentParser(description="Update test_coverage in node.onex.yaml using protocol-driven coverage extraction.")
    parser.add_argument("--node-metadata", required=True, type=Path, help="Path to node.onex.yaml")
    parser.add_argument("--coverage-source", required=True, type=Path, help="Path to coverage report (e.g., coverage.xml)")
    parser.add_argument("--provider", default="xml", help="Coverage provider (default: xml)")
    parser.add_argument("--apply", action="store_true", help="Actually update the file (default: dry-run)")
    args = parser.parse_args()

    # Load node metadata
    with open(args.node_metadata, "r") as f:
        data = yaml.safe_load(f)
    meta = NodeMetadataBlock.model_validate(data)
    old_coverage = meta.test_coverage

    # Get coverage
    provider = get_provider(args.provider)
    try:
        new_coverage = provider.get_coverage_percentage(args.coverage_source)
    except Exception as e:
        emit_log_event_sync(
            level=LogLevelEnum.ERROR,
            message=f"Failed to extract coverage: {e}",
            event_type="coverage_extraction_failed",
            data={"coverage_source": str(args.coverage_source), "provider": args.provider}
        )
        sys.exit(1)

    emit_log_event_sync(
        level=LogLevelEnum.INFO,
        message="Coverage comparison",
        event_type="coverage_comparison",
        data={"old_coverage": old_coverage, "new_coverage": new_coverage}
    )
    
    if not args.apply:
        emit_log_event_sync(
            level=LogLevelEnum.INFO,
            message="Dry run mode - not writing changes. Use --apply to update the file.",
            event_type="dry_run_mode",
            data={"node_metadata": str(args.node_metadata)}
        )
        return
        
    meta.test_coverage = new_coverage
    serializable = enum_to_value(meta.model_dump(mode="python", exclude_none=True))
    with open(args.node_metadata, "w") as f:
        yaml.safe_dump(serializable, f, sort_keys=False)
    
    emit_log_event_sync(
        level=LogLevelEnum.INFO,
        message=f"Updated test coverage to {new_coverage}",
        event_type="coverage_updated",
        data={
            "node_metadata": str(args.node_metadata),
            "old_coverage": old_coverage,
            "new_coverage": new_coverage
        }
    )

if __name__ == "__main__":
    main() 