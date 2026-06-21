import { NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app'

export function middleware(request: Request) {
  const url = new URL(request.url)
  
  // Proxy API requests to backend
  if (url.pathname.startsWith('/api/')) {
    const targetUrl = `${API_URL}${url.pathname}${url.search}`
    const headers = new Headers(request.headers)
    headers.set('Origin', url.origin)
    
    return fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'follow',
    })
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
