'use client'

import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@/services'
import { useAuthStore } from '@/lib/store'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'

export default function AnalyticsPage() {
  const { user } = useAuthStore()

  // Fetch tenant overview
  const { data: tenantAnalytics, isLoading: loadingTenant } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => analyticsService.getTenantOverview(),
  })

  // Fetch student progress (if student)
  const { data: studentProgress } = useQuery({
    queryKey: ['student-progress'],
    queryFn: () => analyticsService.getMyProgress(),
    enabled: user?.role === 'student',
  })

  // Fetch usage over time
  const { data: usageData = [] } = useQuery({
    queryKey: ['analytics-usage'],
    queryFn: () => analyticsService.getUsageOverTime(14),
  })

  // Mock data for demo
  const subjectPerformance = [
    { name: 'Matemáticas', score: 85 },
    { name: 'Física', score: 72 },
    { name: 'Química', score: 90 },
    { name: 'Historia', score: 68 },
    { name: 'Literatura', score: 78 },
  ]

  const gradeDistribution = [
    { name: 'Excelente', value: 15, color: '#22c55e' },
    { name: 'Bueno', value: 35, color: '#0ea5e9' },
    { name: 'Regular', value: 30, color: '#f59e0b' },
    { name: 'Necesita mejorar', value: 20, color: '#ef4444' },
  ]

  const weeklyActivity = usageData.length > 0 ? usageData.map(d => ({
    date: d.date.split('-')[2],
    mensajes: d.chat_messages,
    evaluaciones: d.evaluation_attempts,
  })) : [
    { date: 'Lun', mensajes: 24, evaluaciones: 3 },
    { date: 'Mar', mensajes: 18, evaluaciones: 5 },
    { date: 'Mié', mensajes: 32, evaluaciones: 2 },
    { date: 'Jue', mensajes: 28, evaluaciones: 4 },
    { date: 'Vie', mensajes: 15, evaluaciones: 6 },
    { date: 'Sáb', mensajes: 8, evaluaciones: 1 },
    { date: 'Dom', mensajes: 12, evaluaciones: 2 },
  ]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Analíticas</h1>
          <p className="text-gray-500 mt-1">Resumen de actividad y rendimiento</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-500">Usuarios activos</p>
            <p className="text-3xl font-bold text-gray-900">{tenantAnalytics?.active_users || 0}</p>
            <p className="text-xs text-gray-400 mt-1">de {tenantAnalytics?.total_users || 0} total</p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-accent-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-500">Documentos</p>
            <p className="text-3xl font-bold text-gray-900">{tenantAnalytics?.total_documents || 0}</p>
            <p className="text-xs text-gray-400 mt-1">procesados</p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-500">Conversaciones</p>
            <p className="text-3xl font-bold text-gray-900">{tenantAnalytics?.total_chat_sessions || 0}</p>
            <p className="text-xs text-gray-400 mt-1">sesiones de chat</p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-500">Tokens usados</p>
            <p className="text-3xl font-bold text-gray-900">{(tenantAnalytics?.total_tokens_used || 0).toLocaleString()}</p>
            <p className="text-xs text-gray-400 mt-1">en consultas RAG</p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Weekly Activity */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Actividad semanal</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyActivity}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Bar dataKey="mensajes" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="evaluaciones" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-primary-500 rounded-full" />
                <span className="text-sm text-gray-500">Mensajes</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-accent-500 rounded-full" />
                <span className="text-sm text-gray-500">Evaluaciones</span>
              </div>
            </div>
          </div>

          {/* Grade Distribution */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Distribución de calificaciones</h3>
            <div className="h-64 flex items-center">
              <ResponsiveContainer width="50%" height="100%">
                <PieChart>
                  <Pie
                    data={gradeDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {gradeDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="w-1/2 space-y-3">
                {gradeDistribution.map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-gray-600 flex-1">{item.name}</span>
                    <span className="text-sm font-medium text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Performance by Subject */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Rendimiento por materia</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={subjectPerformance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" />
                <YAxis dataKey="name" type="category" stroke="#9ca3af" width={100} />
                <Tooltip formatter={(value) => [`${value}%`, 'Puntuación']} />
                <Bar dataKey="score" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Student-specific progress */}
        {user?.role === 'student' && studentProgress && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl p-6 text-white">
              <p className="text-sm opacity-80">Promedio de puntuación</p>
              <p className="text-4xl font-bold mt-2">{studentProgress.avg_score.toFixed(1)}%</p>
              <p className="text-sm opacity-80 mt-2">{studentProgress.completed_attempts} evaluaciones completadas</p>
            </div>
            <div className="bg-gradient-to-br from-accent-500 to-accent-600 rounded-2xl p-6 text-white">
              <p className="text-sm opacity-80">Mejor puntuación</p>
              <p className="text-4xl font-bold mt-2">{studentProgress.best_score.toFixed(1)}%</p>
              <p className="text-sm opacity-80 mt-2">tu mejor resultado</p>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
              <p className="text-sm opacity-80">Tasa de aprobación</p>
              <p className="text-4xl font-bold mt-2">{studentProgress.pass_rate.toFixed(1)}%</p>
              <p className="text-sm opacity-80 mt-2">{studentProgress.total_attempts} intentos totales</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}