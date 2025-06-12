import pytest

from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_field_summarization import (
    ToolFieldSummarization,
    tool_field_summarization,
)
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_field_summarization_protocol import (
    FieldSummarizationRequest,
    FieldSummarizationResult,
    BatchSummarizationRequest,
    BatchSummarizationResult,
)


@pytest.fixture
def field_summarization_tool():
    """Fixture providing field summarization tool instance."""
    return ToolFieldSummarization()


@pytest.fixture
def short_content():
    """Fixture providing short content that should not be summarized."""
    return "This is short content that fits within limits."


@pytest.fixture
def long_content():
    """Fixture providing long content that should be summarized."""
    return "x" * 3000  # 3000 characters


class TestToolFieldSummarization:
    """Test suite for field summarization tool."""
    
    def test_tool_instance_creation(self, field_summarization_tool):
        """Test that tool instance can be created and follows protocol."""
        assert field_summarization_tool is not None
        assert hasattr(field_summarization_tool, 'summarize_field')
        assert hasattr(field_summarization_tool, 'summarize_batch')
        assert hasattr(field_summarization_tool, 'should_summarize')
    
    def test_registry_tool_instance(self):
        """Test that registry tool instance is available."""
        assert tool_field_summarization is not None
        assert isinstance(tool_field_summarization, ToolFieldSummarization)
    
    def test_summarize_field_short_content(self, field_summarization_tool, short_content):
        """Test summarization of short content that should not be truncated."""
        request = FieldSummarizationRequest(
            content=short_content,
            max_length=2048,
            summary_mode="head_tail"
        )
        
        result = field_summarization_tool.summarize_field(request)
        
        assert isinstance(result, FieldSummarizationResult)
        assert result.content == short_content
        assert result.truncated is False
        assert result.original_length == len(short_content)
        assert result.summary_mode is None
        assert result.content_hash is None
    
    def test_summarize_field_long_content_head_tail(self, field_summarization_tool, long_content):
        """Test summarization of long content using head_tail mode."""
        request = FieldSummarizationRequest(
            content=long_content,
            max_length=100,
            summary_mode="head_tail"
        )
        
        result = field_summarization_tool.summarize_field(request)
        
        assert isinstance(result, FieldSummarizationResult)
        assert len(result.content) <= 100
        assert result.truncated is True
        assert result.original_length == 3000
        assert result.summary_mode == "head_tail"
        assert result.content_hash is not None
        assert "... [TRUNCATED] ..." in result.content
    
    def test_summarize_field_long_content_hash_mode(self, field_summarization_tool, long_content):
        """Test summarization of long content using hash mode."""
        request = FieldSummarizationRequest(
            content=long_content,
            max_length=100,
            summary_mode="hash"
        )
        
        result = field_summarization_tool.summarize_field(request)
        
        assert isinstance(result, FieldSummarizationResult)
        assert result.truncated is True
        assert result.original_length == 3000
        assert result.summary_mode == "hash"
        assert result.content_hash is not None
        assert "[CONTENT_HASH:" in result.content
        assert "LENGTH: 3000" in result.content
    
    def test_should_summarize_true(self, field_summarization_tool, long_content):
        """Test should_summarize returns True for long content."""
        result = field_summarization_tool.should_summarize(long_content, max_length=100)
        assert result is True
    
    def test_should_summarize_false(self, field_summarization_tool, short_content):
        """Test should_summarize returns False for short content."""
        result = field_summarization_tool.should_summarize(short_content, max_length=2048)
        assert result is False
    
    def test_summarize_batch_basic(self, field_summarization_tool):
        """Test batch summarization with mixed field types and lengths."""
        sample_data = {
            "short_field": "Short content",
            "long_field": "y" * 5000,  # 5000 characters
            "error_details": "z" * 2500,  # 2500 characters
        }
        
        field_config = {
            "long_field": {"max_length": 100, "summary_mode": "head_tail"},
            "error_details": {"max_length": 200, "summary_mode": "hash"},
        }
        
        request = BatchSummarizationRequest(
            data=sample_data,
            field_config=field_config
        )
        
        result = field_summarization_tool.summarize_batch(request)
        
        assert isinstance(result, BatchSummarizationResult)
        
        # Check that configured fields were processed
        assert "long_field" in result.summarization_metadata
        assert "error_details" in result.summarization_metadata
        
        # Verify long_field was summarized with head_tail mode
        long_field_meta = result.summarization_metadata["long_field"]
        assert long_field_meta["truncated"] is True
        assert long_field_meta["original_length"] == 5000
        assert long_field_meta["summary_mode"] == "head_tail"
        assert len(result.data["long_field"]) <= 100 