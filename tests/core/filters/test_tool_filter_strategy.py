"""
Tests for the tool filter strategies.
"""
import pytest

from backend.core.filters.tool_filter_strategy import (
    CompositeToolFilter,
    PriorityToolFilter,
    TagToolFilter,
    ThresholdToolFilter
)
from backend.core.registry.base_registry import BaseTool


# Create some mock tools for testing
class MockTool1(BaseTool):
    name = "mock_tool_1"
    description = "Mock tool 1"
    tags = ["tag1", "tag2"]
    priority = 10


class MockTool2(BaseTool):
    name = "mock_tool_2"
    description = "Mock tool 2"
    tags = ["tag2", "tag3"]
    priority = 20


class MockTool3(BaseTool):
    name = "mock_tool_3"
    description = "Mock tool 3"
    tags = ["tag3", "tag4"]
    priority = 30


class MockTool4(BaseTool):
    name = "mock_tool_4"
    description = "Mock tool 4"
    tags = ["tag4", "tag5"]
    priority = 5


@pytest.fixture
def mock_tools():
    """Create a list of mock tools."""
    return [
        MockTool1(),
        MockTool2(),
        MockTool3(),
        MockTool4()
    ]


def test_threshold_filter(mock_tools):
    """Test the threshold filter."""
    # Create a threshold filter with max_tools=2
    filter_strategy = ThresholdToolFilter(max_tools=2)
    
    # Apply the filter
    filtered_tools = filter_strategy.filter(mock_tools)
    
    # Check that we got the expected number of tools
    assert len(filtered_tools) == 2
    
    # Check that the tools are in the original order
    assert filtered_tools[0].name == "mock_tool_1"
    assert filtered_tools[1].name == "mock_tool_2"


def test_tag_filter(mock_tools):
    """Test the tag filter."""
    # Create a tag filter with included_tags=["tag2"]
    filter_strategy = TagToolFilter(included_tags={"tag2"})
    
    # Apply the filter
    filtered_tools = filter_strategy.filter(mock_tools)
    
    # Check that we got the expected tools
    assert len(filtered_tools) == 2
    assert filtered_tools[0].name == "mock_tool_1"
    assert filtered_tools[1].name == "mock_tool_2"
    
    # Create a tag filter with excluded_tags=["tag2"]
    filter_strategy = TagToolFilter(excluded_tags={"tag2"})
    
    # Apply the filter
    filtered_tools = filter_strategy.filter(mock_tools)
    
    # Check that we got the expected tools
    assert len(filtered_tools) == 2
    assert filtered_tools[0].name == "mock_tool_3"
    assert filtered_tools[1].name == "mock_tool_4"


def test_priority_filter(mock_tools):
    """Test the priority filter."""
    # Create a priority filter with max_tools=2
    filter_strategy = PriorityToolFilter(max_tools=2)
    
    # Apply the filter
    filtered_tools = filter_strategy.filter(mock_tools)
    
    # Check that we got the expected tools
    assert len(filtered_tools) == 2
    
    # Check that the tools are in priority order (highest first)
    assert filtered_tools[0].name == "mock_tool_3"  # priority 30
    assert filtered_tools[1].name == "mock_tool_2"  # priority 20


def test_composite_filter(mock_tools):
    """Test the composite filter."""
    # Create a composite filter with tag filter and threshold filter
    tag_filter = TagToolFilter(included_tags={"tag3"})
    threshold_filter = ThresholdToolFilter(max_tools=1)
    
    filter_strategy = CompositeToolFilter([tag_filter, threshold_filter])
    
    # Apply the filter
    filtered_tools = filter_strategy.filter(mock_tools)
    
    # Check that we got the expected tools
    assert len(filtered_tools) == 1
    assert filtered_tools[0].name == "mock_tool_2"  # First tool with tag3