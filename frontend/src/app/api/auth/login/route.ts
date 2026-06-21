import { NextRequest, NextResponse } from 'next/server'

const RAILWAY_API = 'https://c3po-production-0c24.up.railway.app'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log('Proxy login request:', body.email)
    
    // Forward to Railway with /v1 prefix
    const response = await fetch(`${RAILWAY_API}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'https://c3po-lime.vercel.app',
      },
      body: JSON.stringify(body),
    })
    
    const data = await response.json()
    console.log('Railway response:', response.status, data.access_token ? 'success' : 'error')
    
    // Return response with CORS headers
    return NextResponse.json(data, { 
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json({ detail: 'Proxy error' }, { status: 500 })
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
