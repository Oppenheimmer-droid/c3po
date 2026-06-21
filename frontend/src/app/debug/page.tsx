'use client'
import { useEffect, useState } from 'react'
export default function DebugPage() {
  const [result, setResult] = useState<string>('Loading...')
  useEffect(() => {
    fetch('https://c3po-production-0c24.up.railway.app/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'admin@demo.com', password: 'admin123' })
    })
    .then(r => r.json())
    .then(d => setResult(JSON.stringify(d)))
    .catch(e => setResult('Error: ' + e.message))
  }, [])
  return (
    <div className="p-8">
      <h1>API Debug</h1>
      <pre className="bg-gray-100 p-4 mt-4 rounded whitespace-pre-wrap">{result}</pre>
    </div>
  )
}
