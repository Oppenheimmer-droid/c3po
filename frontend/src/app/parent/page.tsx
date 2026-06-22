'use client'

import { useAuthStore } from '@/lib/store'
import Link from 'next/link'

export default function ParentDashboard() {
  const { user } = useAuthStore()

  // Sample children data
  const children = [
    {
      id: '1',
      name: 'Ana García',
      grade: '3° de Secundaria',
      progress: 85,
      recentActivity: [
        { type: 'chat', text: 'Preguntó sobre matemáticas', time: 'Hace 1 hora' },
        { type: 'quiz', text: 'Completó quiz de ciencias (92%)', time: 'Ayer' },
        { type: 'document', text: 'Subió tarea de historia', time: 'Hace 2 días' },
      ],
      strengths: ['Matemáticas', 'Ciencias'],
      areasToImprove: ['Historia', 'Inglés'],
    },
    {
      id: '2',
      name: 'Luis García',
      grade: '1° de Preparatoria',
      progress: 72,
      recentActivity: [
        { type: 'chat', text: 'Preguntó sobre física cuántica', time: 'Hace 3 horas' },
        { type: 'quiz', text: 'Inició examen de cálculo', time: 'Hace 1 día' },
        { type: 'document', text: 'Descargó apuntes de química', time: 'Hace 3 días' },
      ],
      strengths: ['Física', 'Matemáticas Avanzadas'],
      areasToImprove: ['Español', 'Historia'],
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl p-6 border border-gray-100 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">👨‍👩‍👧</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Panel de Padres</h1>
                <p className="text-gray-500">Seguimiento académico de sus hijos</p>
              </div>
            </div>
            <Link
              href="/analytics"
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition flex items-center gap-2"
            >
              <span>📊</span>
              Ver Reportes
            </Link>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-primary-600 mb-1">{children.length}</div>
            <div className="text-gray-500">Hijos Registrados</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {Math.round(children.reduce((acc, c) => acc + c.progress, 0) / children.length)}%
            </div>
            <div className="text-gray-500">Promedio General</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-blue-600 mb-1">156</div>
            <div className="text-gray-500">Sesiones de Chat</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-purple-600 mb-1">12</div>
            <div className="text-gray-500">Quizzes Completados</div>
          </div>
        </div>

        {/* Children List */}
        <div className="space-y-6">
          {children.map((child) => (
            <div key={child.id} className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              {/* Child Header */}
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-blue-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-purple-600 font-bold text-lg shadow-sm">
                      {child.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900">{child.name}</h2>
                      <p className="text-sm text-gray-500">{child.grade}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-600">{child.progress}%</div>
                      <div className="text-xs text-gray-500">Progreso</div>
                    </div>
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-purple-500 rounded-full" 
                        style={{ width: `${child.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Child Content */}
              <div className="p-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Recent Activity */}
                  <div className="lg:col-span-2">
                    <h3 className="font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
                    <div className="space-y-3">
                      {child.recentActivity.map((activity, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            activity.type === 'chat' ? 'bg-primary-100' :
                            activity.type === 'quiz' ? 'bg-green-100' : 'bg-blue-100'
                          }`}>
                            <span>
                              {activity.type === 'chat' ? '💬' : 
                               activity.type === 'quiz' ? '✏️' : '📄'}
                            </span>
                          </div>
                          <div className="flex-1">
                            <p className="text-sm text-gray-700">{activity.text}</p>
                            <p className="text-xs text-gray-400">{activity.time}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Strengths & Areas */}
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="text-green-500">💪</span> Fortalezas
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {child.strengths.map((s, i) => (
                          <span key={i} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="text-yellow-500">📝</span> Áreas de Mejora
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {child.areasToImprove.map((a, i) => (
                          <span key={i} className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                            {a}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Child Footer */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex gap-3">
                    <Link 
                      href={`/analytics?student=${child.id}`}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition"
                    >
                      Ver Detalles
                    </Link>
                    <button className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition">
                      Contactar Profesor
                    </button>
                  </div>
                  <div className="text-sm text-gray-500">
                    Última actualización: {new Date().toLocaleDateString('es-ES')}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-2xl p-6 border border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/analytics" className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition">
              <span className="text-2xl">📊</span>
              <div>
                <div className="font-medium text-blue-900">Ver Reportes</div>
                <div className="text-sm text-blue-600">Análisis de progreso</div>
              </div>
            </Link>
            <button className="flex items-center gap-3 p-4 bg-green-50 rounded-xl hover:bg-green-100 transition">
              <span className="text-2xl">📧</span>
              <div>
                <div className="font-medium text-green-900">Mensajes</div>
                <div className="text-sm text-green-600">Comunicarse con profesores</div>
              </div>
            </button>
            <button className="flex items-center gap-3 p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition">
              <span className="text-2xl">⚙️</span>
              <div>
                <div className="font-medium text-purple-900">Configuración</div>
                <div className="text-sm text-purple-600">Notificaciones y preferencias</div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
