from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol

class SharedOutputFormatter(OutputFormatterProtocol):
    """
    Default implementation of OutputFormatterProtocol for orchestrator and tool output formatting.
    Returns a UnifiedBatchResultModel for compliance.
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