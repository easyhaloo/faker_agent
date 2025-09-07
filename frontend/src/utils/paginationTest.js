/**
 * Pagination Test for Conversation Store
 * 
 * Test script to verify the new pagination implementation
 */

import { useConversationStore } from '../src/store/conversationStore';

/**
 * Test the pagination functionality
 */
export async function testPagination() {
  console.group('🧪 Testing Conversation Pagination');
  
  const store = useConversationStore.getState();
  
  try {
    // Test 1: Initial state
    console.log('1️⃣ Initial state:');
    console.log('- Conversations:', store.conversations.length);
    console.log('- Pagination:', store.pagination);
    console.log('- List loading:', store.listLoading);
    console.log('- Main loading:', store.isLoading);
    
    // Test 2: Load first page
    console.log('\n2️⃣ Loading first page...');
    const page1Result = await store.loadConversationsPage(1, false);
    console.log('- First page loaded:', page1Result.conversations.length, 'conversations');
    console.log('- Has more:', page1Result.hasMore);
    console.log('- Total count:', page1Result.totalCount);
    
    // Test 3: Load second page (append)
    if (page1Result.hasMore) {
      console.log('\n3️⃣ Loading second page (append mode)...');
      const page2Result = await store.loadConversationsPage(2, true);
      console.log('- Second page loaded:', page2Result.conversations.length, 'conversations');
      console.log('- Total conversations now:', store.conversations.length);
      console.log('- Has more:', page2Result.hasMore);
    }
    
    // Test 4: Test loading state separation
    console.log('\n4️⃣ Testing loading state separation...');
    const loadPromise = store.loadConversationsPage(1, false);
    console.log('- During loading:');
    console.log('  - listLoading:', store.listLoading);
    console.log('  - isLoading:', store.isLoading);
    
    await loadPromise;
    console.log('- After loading:');
    console.log('  - listLoading:', store.listLoading);
    console.log('  - isLoading:', store.isLoading);
    
    // Test 5: Test next page loading
    if (store.pagination.hasMore) {
      console.log('\n5️⃣ Testing next page loading...');
      const nextPagePromise = store.loadNextPage();
      console.log('- During next page loading:');
      console.log('  - isLoadingMore:', store.pagination.isLoadingMore);
      
      await nextPagePromise;
      console.log('- After next page loading:');
      console.log('  - isLoadingMore:', store.pagination.isLoadingMore);
      console.log('  - Current page:', store.pagination.currentPage);
    }
    
    console.log('\n✅ Pagination test completed successfully!');
    
  } catch (error) {
    console.error('❌ Pagination test failed:', error);
  } finally {
    console.groupEnd();
  }
}

/**
 * Test scroll behavior simulation
 */
export function testScrollBehavior() {
  console.group('📜 Testing Scroll Behavior');
  
  // Simulate scroll events
  const mockElement = {
    scrollTop: 800,
    scrollHeight: 1000,
    clientHeight: 200
  };
  
  // Test scroll threshold calculation
  const threshold = 100;
  const isNearBottom = mockElement.scrollHeight - mockElement.scrollTop - mockElement.clientHeight <= threshold;
  
  console.log('Mock element:', mockElement);
  console.log('Threshold:', threshold);
  console.log('Is near bottom:', isNearBottom);
  
  console.groupEnd();
}

/**
 * Test conversation filtering
 */
export function testConversationFiltering() {
  console.group('🔍 Testing Conversation Filtering');
  
  const mockConversations = [
    { id: '1', title: 'Weather Discussion', last_message: 'What is the weather today?' },
    { id: '2', title: 'Code Review', last_message: 'Please review my code' },
    { id: '3', title: 'Weather API', last_message: 'How to use weather API?' }
  ];
  
  const searchQuery = 'weather';
  
  const filtered = mockConversations.filter(conversation => 
    conversation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (conversation.last_message && conversation.last_message.toLowerCase().includes(searchQuery.toLowerCase()))
  );
  
  console.log('Search query:', searchQuery);
  console.log('Original conversations:', mockConversations.length);
  console.log('Filtered conversations:', filtered.length);
  console.log('Filtered results:', filtered.map(c => c.title));
  
  console.groupEnd();
}

// Export all test functions
export default {
  testPagination,
  testScrollBehavior,
  testConversationFiltering
};