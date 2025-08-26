import { useState } from 'react'
import './App.css'
import WeatherWidget from './features/WeatherWidget'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!query.trim()) return
    
    setLoading(true)
    try {
      // TODO: Replace with actual API call from services
      const result = await fetch('http://localhost:8000/api/agent/task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })
      
      const data = await result.json()
      if (data.status === 'success') {
        setResponse(data.data.response)
      } else {
        setResponse(`Error: ${data.error.message}`)
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Faker Agent</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-bold mb-4">Ask the Agent</h2>
          <form onSubmit={handleSubmit} className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask something..."
                className="flex-grow p-2 border border-gray-300 rounded"
                disabled={loading}
              />
              <button 
                type="submit" 
                className="bg-blue-500 text-white px-4 py-2 rounded"
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Send'}
              </button>
            </div>
          </form>
          
          {response && (
            <div className="border border-gray-300 rounded p-4">
              <h2 className="font-bold mb-2">Response:</h2>
              <p>{response}</p>
            </div>
          )}
        </div>
        
        <div>
          <WeatherWidget />
        </div>
      </div>
    </div>
  )
}

export default App