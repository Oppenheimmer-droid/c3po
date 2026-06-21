/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'api.redrive.edu', 'c3po-production-0c24.up.railway.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app/api',
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'https://c3po-lime.vercel.app',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://c3po-production-0c24.up.railway.app',
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app/api'
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS, PATCH' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization, X-Tenant-ID, X-Requested-With' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Max-Age', value: '86400' },
        ],
      },
    ]
  },
}

module.exports = nextConfig
