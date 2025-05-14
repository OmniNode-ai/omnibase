from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol
import json
import yaml

class SharedOutputFormatter(OutputFormatterProtocol):
    """
    Default implementation of OutputFormatterProtocol for orchestrator and tool output formatting.
    Returns a UnifiedBatchResultModel for compliance, and can render as string for CLI/CI.
    """
    def format_output(self, result, format_type: str = "text") -> UnifiedBatchResultModel:
        """
        Format orchestrator results as a UnifiedBatchResultModel.
        Args:
            result: dict, list of dicts, or UnifiedResultModel(s)
            format_type: "json" (default) or "text"
        Returns:
            UnifiedBatchResultModel
        Raises:
            ValueError if input cannot be converted
        """
        # Normalize input to a list of dicts
        if isinstance(result, dict):
            results = [result]
        elif isinstance(result, list):
            results = result
        elif isinstance(result, UnifiedResultModel):
            results = [result.model_dump()]
        elif isinstance(result, UnifiedBatchResultModel):
            results = result.results
        else:
            raise ValueError("Result must be a dict, list of dicts, UnifiedResultModel, or UnifiedBatchResultModel")

        # Convert all to UnifiedResultModel
        unified_results = []
        for r in results:
            if isinstance(r, UnifiedResultModel):
                unified_results.append(r)
            elif isinstance(r, dict):
                try:
                    unified_results.append(UnifiedResultModel(**r))
                except Exception as e:
                    raise ValueError(f"Could not convert result to UnifiedResultModel: {e}")
            else:
                raise ValueError("Each result must be a dict or UnifiedResultModel")

        batch = UnifiedBatchResultModel(results=unified_results)
        return batch

    def render_output(self, result, format_type: str = "text") -> str:
        batch = self.format_output(result, format_type)
        # Only support single result for now (tree validator)
        res = batch.results[0] if batch.results else None
        if format_type == "json":
            return json.dumps(batch.model_dump(mode='json'), indent=2)
        elif format_type == "yaml":
            return yaml.safe_dump(batch.model_dump(mode='json'), sort_keys=False, allow_unicode=True)
        # Default: text with emoji
        if not res:
            return "❌ No result returned."
        emoji = "✅" if res.status == UnifiedStatus.success or (hasattr(res, 'is_valid') and getattr(res, 'is_valid', False)) else "❌"
        lines = [f"{emoji} Validation {'passed' if emoji == '✅' else 'failed'}"]
        # Always show all message summaries
        if hasattr(res, 'messages') and res.messages:
            lines.append("")
            lines.append("Messages:")
            for m in res.messages:
                if hasattr(m, "summary"):
                    lines.append(f"  - {getattr(m, 'summary', '')}")
                elif isinstance(m, dict):
                    lines.append(f"  - {m.get('summary', '')}")
                else:
                    lines.append(f"  - {m}")
        # Always show errors if present and not success
        show_errors = False
        if hasattr(res, 'is_valid') and not getattr(res, 'is_valid', True):
            show_errors = True
        elif hasattr(res, 'errors') and res.errors and (not hasattr(res, 'is_valid') or res.status != UnifiedStatus.success):
            show_errors = True
        if show_errors:
            lines.append("")
            if hasattr(res, 'errors') and res.errors:
                lines.append("Errors:")
                for e in res.errors:
                    # Support both dict and object
                    if hasattr(e, "type") and hasattr(e, "message"):
                        loc = f"{getattr(e, 'file', '') or ''}" + (f":{getattr(e, 'line', '')}" if getattr(e, 'line', None) else "")
                        lines.append(f"  ❌ [{getattr(e, 'type', '').upper()}] {loc} {getattr(e, 'message', '')}")
                    elif isinstance(e, dict):
                        loc = f"{e.get('file', '') or ''}" + (f":{e.get('line', '')}" if e.get('line', None) else "")
                        lines.append(f"  ❌ [{e.get('type', '').upper()}] {loc} {e.get('message', '')}")
                    else:
                        lines.append(f"  ❌ {e}")
        if hasattr(res, 'warnings') and res.warnings:
            lines.append("")
            lines.append("Warnings:")
            for w in res.warnings:
                if hasattr(w, "type") and hasattr(w, "message"):
                    loc = f"{getattr(w, 'file', '') or ''}" + (f":{getattr(w, 'line', '')}" if getattr(w, 'line', None) else "")
                    lines.append(f"  ⚠️ [{getattr(w, 'type', '').upper()}] {loc} {getattr(w, 'message', '')}")
                elif isinstance(w, dict):
                    loc = f"{w.get('file', '') or ''}" + (f":{w.get('line', '')}" if w.get('line', None) else "")
                    lines.append(f"  ⚠️ [{w.get('type', '').upper()}] {loc} {w.get('message', '')}")
                else:
                    lines.append(f"  ⚠️ {w}")
        return "\n".join(lines) 