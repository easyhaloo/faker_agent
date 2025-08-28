import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService, weatherService, systemService } from '../services/api'

// Agent 相关查询
export const useSendTask = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ query, context }) => agentService.sendTask(query, context),
    onSuccess: (data) => {
      // 可以在这里处理成功后的逻辑
      if (data.status === 'success' && data.data.task_id) {
        // 使任务相关的缓存失效
        queryClient.invalidateQueries(['task', data.data.task_id])
      }
    },
  })
}

export const useTaskStatus = (taskId) => {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => agentService.getTaskStatus(taskId),
    enabled: !!taskId,
    refetchInterval: (data) => {
      // 如果任务仍在处理中，每2秒轮询一次
      return data?.data?.status === 'processing' ? 2000 : false
    },
  })
}

// 天气相关查询
export const useWeather = (city) => {
  return useQuery({
    queryKey: ['weather', city],
    queryFn: () => weatherService.getWeather(city),
    enabled: !!city,
  })
}

// 系统状态查询
export const useSystemStatus = () => {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: systemService.getStatus,
  })
}