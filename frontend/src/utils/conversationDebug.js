/**
 * 会话切换调试工具
 * 用于测试和调试会话切换功能
 */

import { useConversationStore } from '../store/conversationStore';

/**
 * 测试会话切换功能
 */
export function testConversationSwitching() {
  console.group('🔧 会话切换调试');
  
  const store = useConversationStore.getState();
  const { conversations, currentConversationId } = store;
  
  console.log('📊 当前状态:');
  console.log('- 总会话数:', conversations.length);
  console.log('- 当前会话ID:', currentConversationId);
  console.log('- 当前会话:', conversations.find(c => c.id === currentConversationId));
  
  // 检查每个会话的消息状态
  conversations.forEach((conv, index) => {
    console.log(`\n💬 会话 ${index + 1}:`);
    console.log('- ID:', conv.id);
    console.log('- 标题:', conv.title);
    console.log('- 消息数量:', conv.messages?.length || 0);
    console.log('- 是否有消息:', !!conv.messages);
    console.log('- 最后更新时间:', conv.updated_at);
    
    if (conv.messages && conv.messages.length > 0) {
      console.log('- 最新消息角色:', conv.messages[conv.messages.length - 1]?.role);
      console.log('- 最新消息预览:', conv.messages[conv.messages.length - 1]?.content?.substring(0, 50) + '...');
    }
  });
  
  console.groupEnd();
}

/**
 * 强制重新加载当前会话的消息
 */
export async function reloadCurrentConversation() {
  const store = useConversationStore.getState();
  const { currentConversationId, loadConversation } = store;
  
  if (!currentConversationId) {
    console.warn('❌ 没有当前会话');
    return;
  }
  
  console.log('🔄 重新加载当前会话消息:', currentConversationId);
  
  try {
    await loadConversation(currentConversationId);
    console.log('✅ 会话消息重新加载完成');
  } catch (error) {
    console.error('❌ 重新加载失败:', error);
  }
}

/**
 * 检查会话消息状态
 */
export function checkConversationMessages() {
  const store = useConversationStore.getState();
  const { conversations } = store;
  
  const conversationsWithMessages = conversations.filter(c => c.messages && c.messages.length > 0);
  const conversationsWithoutMessages = conversations.filter(c => !c.messages || c.messages.length === 0);
  
  console.group('📋 会话消息状态检查');
  console.log('✅ 有消息的会话:', conversationsWithMessages.length);
  console.log('❌ 无消息的会话:', conversationsWithoutMessages.length);
  
  if (conversationsWithoutMessages.length > 0) {
    console.log('\n需要加载消息的会话:');
    conversationsWithoutMessages.forEach(conv => {
      console.log('- ID:', conv.id, '标题:', conv.title);
    });
  }
  
  console.groupEnd();
  
  return {
    withMessages: conversationsWithMessages,
    withoutMessages: conversationsWithoutMessages
  };
}

/**
 * 模拟点击会话记录
 */
export async function simulateConversationClick(conversationId) {
  const store = useConversationStore.getState();
  const { setCurrentConversation } = store;
  
  console.log('🖱️ 模拟点击会话:', conversationId);
  
  const conversation = store.conversations.find(c => c.id === conversationId);
  if (!conversation) {
    console.error('❌ 会话不存在:', conversationId);
    return;
  }
  
  console.log('📋 会话信息:', {
    id: conversation.id,
    title: conversation.title,
    hasMessages: !!conversation.messages,
    messageCount: conversation.messages?.length || 0
  });
  
  // 模拟点击会话记录
  setCurrentConversation(conversationId);
  
  console.log('✅ 会话切换完成');
  
  // 等待一会儿让状态更新
  setTimeout(() => {
    const newStore = useConversationStore.getState();
    const currentConv = newStore.conversations.find(c => c.id === conversationId);
    console.log('📊 切换后的状态:', {
      currentConversationId: newStore.currentConversationId,
      messagesLoaded: !!currentConv?.messages,
      messageCount: currentConv?.messages?.length || 0
    });
  }, 100);
}

export default {
  testConversationSwitching,
  reloadCurrentConversation,
  checkConversationMessages,
  simulateConversationClick
};