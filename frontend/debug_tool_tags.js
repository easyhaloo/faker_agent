// 调试脚本：检查工具标签数据结构
import axios from 'axios';

// 检查API响应格式
async function debugToolTags() {
  try {
    console.log('Fetching tools from API...');
    const response = await axios.get('http://localhost:8000/api/tools');
    console.log('API Response:', response.data);
    
    // 检查数据结构
    console.log('Response type:', typeof response.data);
    console.log('Response keys:', Object.keys(response.data));
    
    if (response.data.data && response.data.data.tools) {
      console.log('Tools data type:', typeof response.data.data.tools);
      console.log('Is tools an array:', Array.isArray(response.data.data.tools));
      console.log('Tools content:', response.data.data.tools);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error fetching tools:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    }
  }
}

// 运行调试
debugToolTags();