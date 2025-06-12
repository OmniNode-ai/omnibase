from typing import Any, Dict, Literal, Protocol
from pydantic import BaseModel

# Type alias for summary modes
SummaryMode = Literal["head_tail", "hash", "truncate"]


class FieldSummarizationRequest(BaseModel):
    """Request model for field summarization operations."""
    content: str
    max_length: int = 2048
    summary_mode: SummaryMode = "head_tail"


class FieldSummarizationResult(BaseModel):
    """Result model for field summarization operations."""
    content: str
    truncated: bool
    original_length: int
    summary_mode: SummaryMode | None = None
    content_hash: str | None = None


class BatchSummarizationRequest(BaseModel):
    """Request model for batch field summarization."""
    data: Dict[str, Any]
    field_config: Dict[str, Dict[str, Any]]


class BatchSummarizationResult(BaseModel):
    """Result model for batch field summarization."""
    data: Dict[str, Any]
    summarization_metadata: Dict[str, Any]


class ToolFieldSummarizationProtocol(Protocol):
    """
    Protocol for field summarization tools that prevent log bloat.
    
    This tool provides field summarization capabilities for preventing log events
    from becoming excessively large while preserving essential information.
    """
    
    def summarize_field(self, request: FieldSummarizationRequest) -> FieldSummarizationResult:
        """
        Summarize a single field based on the provided request.
        
        Args:
            request: Field summarization request with content and configuration
        
        Returns:
            Field summarization result with content and metadata
        """
        ...
    
    def summarize_batch(self, request: BatchSummarizationRequest) -> BatchSummarizationResult:
        """
        Apply field summarization to multiple fields in a data dictionary.
        
        Args:
            request: Batch summarization request with data and field configuration
        
        Returns:
            Batch summarization result with processed data and metadata
        """
        ...
    
    def should_summarize(self, content: str, max_length: int = 2048) -> bool:
        """
        Check if content should be summarized based on length threshold.
        
        Args:
            content: Content to check
            max_length: Maximum allowed length threshold
        
        Returns:
            True if content exceeds threshold and should be summarized
        """
        ... 