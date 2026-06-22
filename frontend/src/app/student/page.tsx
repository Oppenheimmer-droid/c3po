'use client'

import { useAuthStore } from '@/lib/store'
import Link from 'next/link'

export default function StudentDashboard() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl p-6 border border-gray-100 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🎓</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Panel del Estudiante</h1>
                <p className="text-gray-500">Bienvenido, {user?.first_name} {user?.last_name}</p>
              </div>
            </div>
            <Link
              href="/chat"
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition flex items-center gap-2"
            >
              <span>💬</span>
              Nuevo Chat con IA
            </Link>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">78%</div>
                <div className="text-gray-500">Progreso General</div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full" style={{ width: '78%' }} />
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📚</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">8</div>
                <div className="text-gray-500">Cursos Activos</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">💬</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">45</div>
                <div className="text-gray-500">Chats con IA</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Courses */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Mis Cursos</h2>
              </div>
              <div className="divide-y divide-gray-100">
                {[
                  { name: 'Matemáticas', teacher: 'Prof. García', progress: 85, color: 'bg-blue-500' },
                  { name: 'Ciencias', teacher: 'Prof. López', progress: 72, color: 'bg-green-500' },
                  { name: 'Historia', teacher: 'Prof. Martínez', progress: 90, color: 'bg-yellow-500' },
                  { name: 'Lengua', teacher: 'Prof. Sánchez', progress: 65, color: 'bg-purple-500' },
                ].map((course, i) => (
                  <div key={i} className="p-6 hover:bg-gray-50 transition">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-medium text-gray-900">{course.name}</h3>
                        <p className="text-sm text-gray-500">{course.teacher}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${course.color}`}>
                        {course.progress}%
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${course.color} rounded-full`} 
                          style={{ width: `${course.progress}%` }}
                        />
                      </div>
                      <Link 
                        href="/chat" 
                        className="px-3 py-1 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition"
                      >
                        Chat
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Documents */}
            <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Documentos Recientes</h2>
              </div>
              <div className="divide-y divide-gray-100">
                {[
                  { name: 'Apuntes de Cálculo', type: 'PDF', date: 'Hace 2 días' },
                  { name: 'Resumen Historia Universal', type: 'DOCX', date: 'Hace 3 días' },
                  { name: 'Ejercicios de Álgebra', type: 'PDF', date: 'Hace 5 días' },
                ].map((doc, i) => (
                  <div key={i} className="p-4 flex items-center gap-4 hover:bg-gray-50 transition">
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                      <span className="text-lg">📄</span>
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{doc.name}</div>
                      <div className="text-sm text-gray-500">{doc.type} • {doc.date}</div>
                    </div>
                    <Link href="/documents" className="text-primary-600 hover:text-primary-700">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
              <div className="space-y-3">
                <Link href="/chat" className="flex items-center gap-3 p-3 bg-primary-50 rounded-xl hover:bg-primary-100 transition">
                  <span className="text-xl">🤖</span>
                  <span className="font-medium text-primary-700">Chat con IA</span>
                </Link>
                <Link href="/documents" className="flex items-center gap-3 p-3 bg-green-50 rounded-xl hover:bg-green-100 transition">
                  <span className="text-xl">📖</span>
                  <span className="font-medium text-green-700">Ver Documentos</span>
                </Link>
                <Link href="/evaluations" className="flex items-center gap-3 p-3 bg-purple-50 rounded-xl hover:bg-purple-100 transition">
                  <span className="text-xl">✏️</span>
                  <span className="font-medium text-purple-700">Hacer Quiz</span>
                </Link>
              </div>
            </div>

            {/* Upcoming */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-4">Próximos Eventos</h3>
              <div className="space-y-4">
                {[
                  { title: 'Examen de Matemáticas', date: 'Mañana', type: 'exam' },
                  { title: 'Entrega de Proyecto', date: 'En 3 días', type: 'deadline' },
                  { title: 'Chat con Prof. García', date: 'En 5 días', type: 'chat' },
                ].map((event, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      event.type === 'exam' ? 'bg-red-100' :
                      event.type === 'deadline' ? 'bg-yellow-100' : 'bg-blue-100'
                    }`}>
                      <span>
                        {event.type === 'exam' ? '📝' : event.type === 'deadline' ? '⏰' : '💬'}
                      </span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm">{event.title}</div>
                      <div className="text-xs text-gray-500">{event.date}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Achievements */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-4">Logros Recientes</h3>
              <div className="flex gap-2">
                {['🏆', '⭐', '🎯', '📚'].map((badge, i) => (
                  <div key={i} className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-lg">
                    {badge}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
