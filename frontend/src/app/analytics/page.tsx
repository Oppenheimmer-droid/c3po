'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

interface AnalyticsData {
  total_users: number
  total_chats: number
  total_documents: number
  total_tokens: number
  active_users: number
  daily_activity: { date: string; chats: number; users: number }[]
}

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await api.get('/analytics/overview')
      return response.data
    },
  })

  // Sample data for demo
  const sampleAnalytics: AnalyticsData = {
    total_users: 156,
    total_chats: 1243,
    total_documents: 89,
    total_tokens: 1250000,
    active_users: 42,
    daily_activity: [
      { date: '2024-01-15', chats: 45, users: 12 },
      { date: '2024-01-16', chats: 67, users: 18 },
      { date: '2024-01-17', chats: 89, users: 25 },
      { date: '2024-01-18', chats: 34, users: 10 },
      { date: '2024-01-19', chats: 123, users: 35 },
      { date: '2024-01-20', chats: 78, users: 22 },
      { date: '2024-01-21', chats: 56, users: 15 },
    ],
  }

  const displayAnalytics = analytics || sampleAnalytics

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analíticas</h1>
          <p className="text-gray-500 mt-1">Métricas y estadísticas de uso de la plataforma</p>
        </div>

        {/* Main Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{displayAnalytics.total_users}</div>
                <div className="text-gray-500 text-sm">Total Usuarios</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{displayAnalytics.total_chats}</div>
                <div className="text-gray-500 text-sm">Conversaciones</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{displayAnalytics.total_documents}</div>
                <div className="text-gray-500 text-sm">Documentos</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{formatNumber(displayAnalytics.total_tokens)}</div>
                <div className="text-gray-500 text-sm">Tokens Usados</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
                </svg>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{displayAnalytics.active_users}</div>
                <div className="text-gray-500 text-sm">Activos Hoy</div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Activity Chart */}
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Actividad Reciente</h3>
            <div className="h-64 flex items-end justify-around gap-2">
              {displayAnalytics.daily_activity.map((day, i) => {
                const maxChats = Math.max(...displayAnalytics.daily_activity.map(d => d.chats))
                const height = (day.chats / maxChats) * 100
                return (
                  <div key={i} className="flex flex-col items-center gap-2 flex-1">
                    <div className="w-full bg-primary-100 rounded-t-lg relative group" style={{ height: `${height}%`, minHeight: '8px' }}>
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                        {day.chats} chats
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">{new Date(day.date).toLocaleDateString('es-ES', { weekday: 'short' })}</div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Top Features */}
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Uso por Categoría</h3>
            <div className="space-y-4">
              {[
                { name: 'Chat con IA', percentage: 65, color: 'bg-primary-500' },
                { name: 'Documentos', percentage: 25, color: 'bg-green-500' },
                { name: 'Evaluaciones', percentage: 10, color: 'bg-purple-500' },
              ].map((item, i) => (
                <div key={i}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{item.name}</span>
                    <span className="text-sm text-gray-500">{item.percentage}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full ${item.color} rounded-full transition-all`} style={{ width: `${item.percentage}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity Table */}
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Actividad por Usuario</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Usuario</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Rol</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Chats</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Tokens</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Última Actividad</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {[
                  { name: 'María García', role: 'Estudiante', chats: 45, tokens: 12500, last: 'Hace 5 min' },
                  { name: 'Carlos López', role: 'Profesor', chats: 23, tokens: 8900, last: 'Hace 15 min' },
                  { name: 'Ana Martínez', role: 'Estudiante', chats: 67, tokens: 15200, last: 'Hace 30 min' },
                ].map((user, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-sm font-medium">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <span className="font-medium text-gray-900">{user.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-500">{user.role}</td>
                    <td className="px-6 py-4 text-gray-900 font-medium">{user.chats}</td>
                    <td className="px-6 py-4 text-gray-900">{formatNumber(user.tokens)}</td>
                    <td className="px-6 py-4 text-gray-500">{user.last}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
