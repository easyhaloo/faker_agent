import { useSystemStatus } from '../hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Server, Activity, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function SystemStatusWidget() {
  const { data: statusData, isLoading, error } = useSystemStatus()

  if (isLoading) {
    return (
      <Card className="shadow-lg rounded-2xl border-0">
        <CardHeader className="pb-4 border-b border-gray-200">
          <CardTitle className="flex items-center gap-2 text-lg font-bold text-gray-800">
            <Server className="h-5 w-5 text-gray-700" />
            System Status
            <div className="ml-auto">
              <div className="h-3 w-3 rounded-full bg-gray-300 animate-pulse"></div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="flex items-center justify-center h-24">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="shadow-lg rounded-2xl border-0">
        <CardHeader className="pb-4 border-b border-gray-200">
          <CardTitle className="flex items-center gap-2 text-lg font-bold text-gray-800">
            <Server className="h-5 w-5 text-red-500" />
            System Status
            <Badge variant="destructive" className="ml-auto">
              Offline
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="flex flex-col items-center justify-center h-24 text-center">
            <XCircle className="h-8 w-8 text-red-500 mb-2" />
            <span className="text-red-600 font-medium">Error loading system status</span>
            <span className="text-sm text-gray-500 mt-1">Please try again later</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  const isHealthy = statusData?.status === 'success'
  
  return (
    <Card className="shadow-lg rounded-2xl border-0">
      <CardHeader className="pb-4 border-b border-gray-200">
        <CardTitle className="flex items-center justify-between text-lg font-bold text-gray-800">
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-gray-700" />
            System Status
          </div>
          <Badge variant={isHealthy ? "default" : "destructive"} className="rounded-full">
            {isHealthy ? "Operational" : "Issues Detected"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="h-4 w-4 text-blue-600" />
              </div>
              <span className="text-sm font-medium text-gray-700">API Status</span>
            </div>
            <Badge variant="secondary" className="rounded-full">
              {statusData?.data?.api_status || 'Unknown'}
            </Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Server className="h-4 w-4 text-green-600" />
              </div>
              <span className="text-sm font-medium text-gray-700">Database</span>
            </div>
            <Badge 
              variant={statusData?.data?.database_status === 'connected' ? "default" : "destructive"} 
              className="rounded-full"
            >
              {statusData?.data?.database_status || 'Unknown'}
            </Badge>
          </div>
          
          {statusData?.data?.model_status && (
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <div className="h-4 w-4 rounded-full bg-purple-600"></div>
                </div>
                <span className="text-sm font-medium text-gray-700">Model</span>
              </div>
              <Badge 
                variant={statusData?.data?.model_status === 'available' ? "default" : "destructive"} 
                className="rounded-full"
              >
                {statusData?.data?.model_status}
              </Badge>
            </div>
          )}
          
          {statusData?.data?.uptime && (
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                <span>Uptime: <span className="font-medium text-gray-800">{statusData?.data?.uptime}</span></span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}