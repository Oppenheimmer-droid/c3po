'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store'

export default function TeacherDashboard() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl p-6 border border-gray-100 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">👨‍🏫</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Panel del Profesor</h1>
                <p className="text-gray-500">Bienvenido, {user?.first_name} {user?.last_name}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <Link
                href="/chat"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition"
              >
                Nuevo Chat
              </Link>
              <Link
                href="/documents"
                className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition"
              >
                Subir Documento
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-primary-600 mb-1">12</div>
            <div className="text-gray-500">Mis Cursos</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-green-600 mb-1">156</div>
            <div className="text-gray-500">Estudiantes</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-purple-600 mb-1">89</div>
            <div className="text-gray-500">Documentos</div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="text-3xl font-bold text-yellow-600 mb-1">342</div>
            <div className="text-gray-500">Chats</div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* My Courses */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">Mis Cursos</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {[
                { name: 'Matemáticas III', students: 45, progress: 78 },
                { name: 'Cálculo Diferencial', students: 32, progress: 65 },
                { name: 'Estadística', students: 28, progress: 82 },
                { name: 'Álgebra Lineal', students: 35, progress: 45 },
              ].map((course, i) => (
                <div key={i} className="p-6 hover:bg-gray-50 transition cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">{course.name}</h3>
                    <span className="text-sm text-gray-500">{course.students} estudiantes</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary-500 rounded-full" 
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-600">{course.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
              <div className="space-y-3">
                <Link href="/documents" className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span>📄</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Subir Documento</div>
                    <div className="text-xs text-gray-500">PDF, DOCX, PPT</div>
                  </div>
                </Link>
                <Link href="/evaluations" className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <span>✏️</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Crear Evaluación</div>
                    <div className="text-xs text-gray-500">Quiz o Examen</div>
                  </div>
                </Link>
                <Link href="/chat" className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <span>💬</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Chat con IA</div>
                    <div className="text-xs text-gray-500">Tutoría inteligente</div>
                  </div>
                </Link>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
              <div className="space-y-4">
                {[
                  { text: 'María García completó un quiz', time: 'Hace 5 min' },
                  { text: 'Nuevo documento subido: "Apuntes Cálculo"', time: 'Hace 1 hora' },
                  { text: 'Carlos López hizo una pregunta', time: 'Hace 2 horas' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-2 h-2 mt-2 bg-primary-500 rounded-full" />
                    <div>
                      <p className="text-sm text-gray-700">{item.text}</p>
                      <p className="text-xs text-gray-400">{item.time}</p>
                    </div>
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
