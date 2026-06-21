import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('Authorization')
  const res = await fetch('https://c3po-production-0c24.up.railway.app/api/v1/auth/me', {
    headers: { Authorization: authHeader || '' }
  })
  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
