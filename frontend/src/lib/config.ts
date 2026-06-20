// Backend URL - base URL without /api (endpoints add /api prefix)
export const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app'

// App URL for redirects and links  
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://c3po-frontend.vercel.app'

// WebSocket URL for real-time features
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'wss://c3po-production-0c24.up.railway.app'
