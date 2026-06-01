/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'api.redrive.edu', 'c3po-production-0c24.up.railway.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app',
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'https://c3po-frontend.vercel.app',
  },
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app'
    return [
      {
        source: '/api/:path*',
        destination: `${backend}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig