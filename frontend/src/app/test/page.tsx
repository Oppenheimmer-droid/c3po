'use client'

import { useState } from 'react'

export default function TestPage() {
  const [result, setResult] = useState<string>('')

  const testLogin = async () => {
    try {
      const response = await fetch('https://c3po-production-0c24.up.railway.app/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'admin@demo.com', password: 'admin123' })
      })
      const data = await response.json()
      setResult(JSON.stringify(data, null, 2))
    } catch (error) {
      setResult('Error: ' + (error as Error).message)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">API Test</h1>
      <button onClick={testLogin} className="bg-blue-500 text-white px-4 py-2 rounded">
        Test Login
      </button>
      <pre className="mt-4 p-4 bg-gray-100 rounded">{result}</pre>
    </div>
  )
}
