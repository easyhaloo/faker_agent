"""
Filter strategies and management for the Faker Agent.

This package provides filtering capabilities for tools and protocols
before they're used in the system, allowing for fine-grained control
over which components are available in different contexts.
"""
from backend.core.filters.tool_filter_strategy import (
    ToolFilterStrategy,
    ThresholdToolFilter,
    TagToolFilter,
    PriorityToolFilter,
    CompositeToolFilter,
    create_filter_strategy
)
from backend.core.filters.protocol_filter_strategy import (
    ProtocolFilterStrategy,
    AllowAllProtocolFilter,
    DenyAllProtocolFilter,
    WhitelistProtocolFilter,
    BlacklistProtocolFilter,
    CompositeProtocolFilter,
    create_protocol_filter_strategy
)
from backend.core.filters.filter_manager import FilterManager, filter_manager

__all__ = [
    # Tool filter strategies
    'ToolFilterStrategy',
    'ThresholdToolFilter',
    'TagToolFilter',
    'PriorityToolFilter',
    'CompositeToolFilter',
    'create_filter_strategy',
    
    # Protocol filter strategies
    'ProtocolFilterStrategy',
    'AllowAllProtocolFilter',
    'DenyAllProtocolFilter',
    'WhitelistProtocolFilter',
    'BlacklistProtocolFilter',
    'CompositeProtocolFilter',
    'create_protocol_filter_strategy',
    
    # Filter manager
    'FilterManager',
    'filter_manager'
]