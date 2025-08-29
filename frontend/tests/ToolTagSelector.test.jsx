import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ToolTagSelector from '../src/components/ToolTagSelector';

// Mock the agent store
const mockAddToolTag = vi.fn();
const mockRemoveToolTag = vi.fn();
const mockClearToolTags = vi.fn();
const mockFetchAvailableTools = vi.fn();

vi.mock('../src/store/agentStore', () => ({
  useAgentStore: (selector) => {
    const mockState = {
      toolTags: [],
      availableTools: [
        {
          name: 'weather_query',
          description: 'Queries weather information',
          tags: ['weather', 'data'],
          parameters: [],
          priority: 10
        },
        {
          name: 'weather_assistant',
          description: 'Get weather information by asking questions',
          tags: ['weather', 'assistant', 'natural_language'],
          parameters: [],
          priority: 20
        }
      ],
      addToolTag: mockAddToolTag,
      removeToolTag: mockRemoveToolTag,
      clearToolTags: mockClearToolTags,
      fetchAvailableTools: mockFetchAvailableTools,
      isLoading: false
    };
    
    return selector(mockState);
  }
}));

describe('ToolTagSelector', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    mockAddToolTag.mockClear();
    mockRemoveToolTag.mockClear();
    mockClearToolTags.mockClear();
    mockFetchAvailableTools.mockClear();
  });

  it('renders without crashing', () => {
    render(<ToolTagSelector />);
    
    // Check if the component renders
    expect(screen.getByText('工具过滤')).toBeInTheDocument();
    expect(screen.getByText('展开')).toBeInTheDocument();
  });

  it('displays "未选择任何工具标签" when no tags are selected', () => {
    render(<ToolTagSelector />);
    
    // Expand the selector
    fireEvent.click(screen.getByText('展开'));
    
    // Check if the default message is displayed
    expect(screen.getByText('未选择任何工具标签，将使用所有可用工具')).toBeInTheDocument();
  });

  it('expands and collapses when the toggle button is clicked', () => {
    render(<ToolTagSelector />);
    
    // Initially collapsed
    expect(screen.queryByText('搜索标签...')).not.toBeInTheDocument();
    
    // Expand
    fireEvent.click(screen.getByText('展开'));
    expect(screen.getByPlaceholderText('搜索标签...')).toBeInTheDocument();
    
    // Collapse
    fireEvent.click(screen.getByText('收起'));
    expect(screen.queryByPlaceholderText('搜索标签...')).not.toBeInTheDocument();
  });

  it('displays available tags when expanded', () => {
    render(<ToolTagSelector />);
    
    // Expand the selector
    fireEvent.click(screen.getByText('展开'));
    
    // Check if tags are displayed
    expect(screen.getByText('weather')).toBeInTheDocument();
    expect(screen.getByText('data')).toBeInTheDocument();
    expect(screen.getByText('assistant')).toBeInTheDocument();
    expect(screen.getByText('natural_language')).toBeInTheDocument();
  });

  it('adds a tag when clicked', () => {
    render(<ToolTagSelector />);
    
    // Expand the selector
    fireEvent.click(screen.getByText('展开'));
    
    // Click on a tag
    fireEvent.click(screen.getByText('weather'));
    
    // Check if addToolTag was called with the correct tag
    expect(mockAddToolTag).toHaveBeenCalledWith('weather');
  });

  it('removes a tag when clicked from selected tags', () => {
    // Mock the store to return a selected tag
    vi.mock('../src/store/agentStore', async () => {
      const actual = await vi.importActual('../src/store/agentStore');
      return {
        ...actual,
        useAgentStore: (selector) => {
          const mockState = {
            toolTags: ['weather'],
            availableTools: [
              {
                name: 'weather_query',
                description: 'Queries weather information',
                tags: ['weather', 'data'],
                parameters: [],
                priority: 10
              }
            ],
            addToolTag: mockAddToolTag,
            removeToolTag: mockRemoveToolTag,
            clearToolTags: mockClearToolTags,
            fetchAvailableTools: mockFetchAvailableTools,
            isLoading: false
          };
          
          return selector(mockState);
        }
      };
    });
    
    // Re-render with the new mock
    render(<ToolTagSelector />);
    
    // Click on the selected tag to remove it
    fireEvent.click(screen.getByText('weather').closest('div'));
    
    // Check if removeToolTag was called with the correct tag
    expect(mockRemoveToolTag).toHaveBeenCalledWith('weather');
  });

  it('clears all tags when clear button is clicked', () => {
    // Mock the store to return selected tags
    vi.mock('../src/store/agentStore', async () => {
      const actual = await vi.importActual('../src/store/agentStore');
      return {
        ...actual,
        useAgentStore: (selector) => {
          const mockState = {
            toolTags: ['weather', 'data'],
            availableTools: [
              {
                name: 'weather_query',
                description: 'Queries weather information',
                tags: ['weather', 'data'],
                parameters: [],
                priority: 10
              }
            ],
            addToolTag: mockAddToolTag,
            removeToolTag: mockRemoveToolTag,
            clearToolTags: mockClearToolTags,
            fetchAvailableTools: mockFetchAvailableTools,
            isLoading: false
          };
          
          return selector(mockState);
        }
      };
    });
    
    render(<ToolTagSelector />);
    
    // Click the clear button
    fireEvent.click(screen.getByText('清除全部'));
    
    // Check if clearToolTags was called
    expect(mockClearToolTags).toHaveBeenCalledTimes(1);
  });

  it('filters tags based on search query', () => {
    render(<ToolTagSelector />);
    
    // Expand the selector
    fireEvent.click(screen.getByText('展开'));
    
    // Enter search query
    const searchInput = screen.getByPlaceholderText('搜索标签...');
    fireEvent.change(searchInput, { target: { value: 'data' } });
    
    // Check if only matching tags are displayed
    expect(screen.getByText('data')).toBeInTheDocument();
    expect(screen.queryByText('weather')).not.toBeInTheDocument();
    expect(screen.queryByText('assistant')).not.toBeInTheDocument();
  });
});