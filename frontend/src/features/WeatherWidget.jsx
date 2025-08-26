import { useState } from 'react'
import { weatherService } from '../services/api'

export default function WeatherWidget() {
  const [city, setCity] = useState('')
  const [weatherData, setWeatherData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!city.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await weatherService.getWeather(city)
      
      if (response.status === 'success') {
        setWeatherData(response.data)
      } else {
        setError(`Error: ${response.error?.message || 'Unknown error'}`)
      }
    } catch (err) {
      setError(`Error: ${err.message || 'Failed to fetch weather data'}`)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="p-4 border border-gray-300 rounded-lg shadow-sm">
      <h2 className="text-xl font-bold mb-4">Weather Query</h2>
      
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter city name..."
            className="flex-grow p-2 border border-gray-300 rounded"
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Search'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded mb-4">
          {error}
        </div>
      )}
      
      {weatherData && (
        <div className="border border-gray-200 rounded p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold">{weatherData.city}</h3>
              <p className="text-sm text-gray-500">{weatherData.date}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{weatherData.temperature.current}</div>
              <div className="text-sm">
                {weatherData.temperature.min} - {weatherData.temperature.max}
              </div>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-2 gap-2">
            <div>
              <div className="text-sm text-gray-500">Condition</div>
              <div>{weatherData.condition}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Humidity</div>
              <div>{weatherData.humidity}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Wind</div>
              <div>{weatherData.wind.direction} {weatherData.wind.speed}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}