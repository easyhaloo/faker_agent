import { useState } from 'react'
import { useWeather } from '../hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Cloud, Thermometer, Droplets, Wind } from 'lucide-react'

export default function WeatherWidget() {
  const [city, setCity] = useState('')
  const { data: weatherData, isLoading, error, refetch } = useWeather(city)

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!city.trim()) return
    
    refetch()
  }
  
  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter city name..."
            disabled={isLoading}
            className="pl-10 py-5 text-base rounded-xl border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200"
          />
          <Cloud className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        </div>
        <Button 
          type="submit" 
          disabled={isLoading}
          className="bg-blue-600 hover:bg-blue-700 px-6 rounded-xl"
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading...
            </span>
          ) : 'Search'}
        </Button>
      </form>
      
      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-200">
          <div className="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">Error:</span>
          </div>
          <p className="mt-1">{error.message || 'Failed to fetch weather data'}</p>
        </div>
      )}
      
      {weatherData && weatherData.status === 'success' && (
        <Card className="border-0 shadow-lg rounded-2xl overflow-hidden">
          <CardContent className="p-0">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-5 text-white">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold">{weatherData.data.city}</h3>
                  <p className="text-blue-100">{weatherData.data.date}</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold">{weatherData.data.temperature.current}</div>
                  <div className="text-blue-100 text-sm">
                    {weatherData.data.temperature.min} - {weatherData.data.temperature.max}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-5">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Thermometer className="h-5 w-5 text-orange-500" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wide">Condition</div>
                    <div className="font-medium">{weatherData.data.condition}</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Droplets className="h-5 w-5 text-blue-500" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wide">Humidity</div>
                    <div className="font-medium">{weatherData.data.humidity}</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Wind className="h-5 w-5 text-gray-500" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wide">Wind</div>
                    <div className="font-medium">{weatherData.data.wind.direction} {weatherData.data.wind.speed}</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}