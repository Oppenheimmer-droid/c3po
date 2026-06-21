/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'api.redrive.edu', 'c3po-production-0c24.up.railway.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app',
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'https://c3po-lime.vercel.app',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://c3po-production-0c24.up.railway.app',
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'https://c3po-production-0c24.up.railway.app/api/v1/:path*',
      },
    ]
  },
}

module.exports = nextConfig
