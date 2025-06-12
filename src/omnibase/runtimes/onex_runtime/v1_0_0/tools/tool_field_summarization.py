import hashlib
from typing import Any, Dict

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_field_summarization_protocol import (
    ToolFieldSummarizationProtocol,
    FieldSummarizationRequest,
    FieldSummarizationResult,
    BatchSummarizationRequest,
    BatchSummarizationResult,
    SummaryMode,
)

# Default configuration constants
TRUNCATION_MARKER = "... [TRUNCATED] ..."
HASH_PREFIX = "[CONTENT_HASH:"
HASH_SUFFIX = "]"


class ToolFieldSummarization(ToolFieldSummarizationProtocol):
    """
    Runtime tool for field summarization to prevent log bloat.
    
    This tool provides field summarization capabilities for preventing log events
    from becoming excessively large while preserving essential information and
    metadata about the summarization process.
    """
    
    def summarize_field(self, request: FieldSummarizationRequest) -> FieldSummarizationResult:
        """
        Summarize a single field based on the provided request.
        
        Args:
            request: Field summarization request with content and configuration
        
        Returns:
            Field summarization result with content and metadata
        """
        # Validate inputs
        if not isinstance(request.content, str):
            raise OnexError(
                f"content must be a string, got {type(request.content).__name__}",
                CoreErrorCode.INVALID_PARAMETER,
            )
        
        if request.max_length <= 0:
            raise OnexError(
                f"max_length must be positive, got {request.max_length}",
                CoreErrorCode.INVALID_PARAMETER,
            )
        
        original_length = len(request.content)
        
        # No summarization needed
        if original_length <= request.max_length:
            return FieldSummarizationResult(
                content=request.content,
                truncated=False,
                original_length=original_length,
            )
        
        # Generate content hash for metadata
        content_hash = hashlib.sha256(request.content.encode('utf-8')).hexdigest()[:16]
        
        # Apply summarization based on mode
        if request.summary_mode == "head_tail":
            summarized_content = self._summarize_head_tail(request.content, request.max_length)
        elif request.summary_mode == "hash":
            summarized_content = self._summarize_hash(content_hash, original_length)
        else:  # truncate
            summarized_content = self._summarize_truncate(request.content, request.max_length)
        
        return FieldSummarizationResult(
            content=summarized_content,
            truncated=True,
            original_length=original_length,
            summary_mode=request.summary_mode,
            content_hash=content_hash,
        )
    
    def summarize_batch(self, request: BatchSummarizationRequest) -> BatchSummarizationResult:
        """
        Apply field summarization to multiple fields in a data dictionary.
        
        Args:
            request: Batch summarization request with data and field configuration
        
        Returns:
            Batch summarization result with processed data and metadata
        """
        result_data = request.data.copy()
        metadata = {}
        
        for field_name, config in request.field_config.items():
            if field_name in request.data and isinstance(request.data[field_name], str):
                # Create field summarization request
                field_request = FieldSummarizationRequest(
                    content=request.data[field_name],
                    max_length=config.get("max_length", 2048),
                    summary_mode=config.get("summary_mode", "head_tail"),
                )
                
                # Summarize the field
                field_result = self.summarize_field(field_request)
                
                # Update result data and metadata
                result_data[field_name] = field_result.content
                metadata[field_name] = {
                    "truncated": field_result.truncated,
                    "original_length": field_result.original_length,
                    "summary_mode": field_result.summary_mode,
                    "content_hash": field_result.content_hash,
                }
        
        return BatchSummarizationResult(
            data=result_data,
            summarization_metadata=metadata,
        )
    
    def should_summarize(self, content: str, max_length: int = 2048) -> bool:
        """
        Check if content should be summarized based on length threshold.
        
        Args:
            content: Content to check
            max_length: Maximum allowed length threshold
        
        Returns:
            True if content exceeds threshold and should be summarized
        """
        return isinstance(content, str) and len(content) > max_length
    
    def _summarize_head_tail(self, content: str, max_length: int) -> str:
        """
        Summarize content by keeping head and tail with truncation marker.
        
        Args:
            content: Original content to summarize
            max_length: Maximum allowed length
        
        Returns:
            Summarized content with head, marker, and tail
        """
        # Reserve space for truncation marker
        marker_length = len(TRUNCATION_MARKER)
        available_length = max_length - marker_length
        
        if available_length <= 0:
            return TRUNCATION_MARKER
        
        # Split available space between head and tail
        head_length = available_length // 2
        tail_length = available_length - head_length
        
        head = content[:head_length].rstrip()
        tail = content[-tail_length:].lstrip()
        
        return f"{head}{TRUNCATION_MARKER}{tail}"
    
    def _summarize_hash(self, content_hash: str, original_length: int) -> str:
        """
        Summarize content by replacing with hash and length information.
        
        Args:
            content_hash: SHA256 hash of the original content
            original_length: Length of the original content
        
        Returns:
            Hash-based summary string
        """
        return f"{HASH_PREFIX} {content_hash}, LENGTH: {original_length}{HASH_SUFFIX}"
    
    def _summarize_truncate(self, content: str, max_length: int) -> str:
        """
        Summarize content by simple truncation with marker.
        
        Args:
            content: Original content to summarize
            max_length: Maximum allowed length
        
        Returns:
            Truncated content with marker
        """
        marker_length = len(TRUNCATION_MARKER)
        if max_length <= marker_length:
            return TRUNCATION_MARKER
        
        truncate_length = max_length - marker_length
        return content[:truncate_length].rstrip() + TRUNCATION_MARKER


# Create tool instance for registry
tool_field_summarization = ToolFieldSummarization() 