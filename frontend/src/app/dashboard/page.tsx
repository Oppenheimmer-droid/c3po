'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store'
import { getRoleLabel } from '@/lib/utils'

export default function DashboardPage() {
  const { user, isAuthenticated, initAuth } = useAuthStore()

  useEffect(() => {
    // Initialize auth - will auto-login if needed
    if (useAuthStore.getState().isLoading) {
      initAuth()
    }
  }, [])

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Iniciando sesión...</p>
        </div>
      </div>
    )
  }

  const roleCards = {
    superadmin: [
      { title: 'Gestionar Academias', href: '/admin/tenants', icon: '🏛️', description: 'Ver y administrar todas las academias' },
      { title: 'Métricas Globales', href: '/analytics', icon: '📊', description: 'Estadísticas de uso de la plataforma' },
    ],
    academy_admin: [
      { title: 'Gestionar Usuarios', href: '/admin/users', icon: '👥', description: 'Profesores, estudiantes y administradores' },
      { title: 'Documentos', href: '/documents', icon: '📄', description: 'Biblioteca de materiales' },
      { title: 'Asignaturas', href: '/subjects', icon: '📚', description: 'Configurar cursos y temas' },
      { title: 'Reportes', href: '/analytics', icon: '📈', description: 'Analíticas y progreso' },
    ],
    teacher: [
      { title: 'Mi Dashboard', href: '/teacher', icon: '📋', description: 'Resumen de mis cursos' },
      { title: 'Documentos', href: '/documents', icon: '📄', description: 'Subir y gestionar materiales' },
      { title: 'Evaluaciones', href: '/evaluations', icon: '✏️', description: 'Crear y revisar quizzes' },
      { title: 'Chat con IA', href: '/chat', icon: '💬', description: 'Tutoría inteligente' },
      { title: 'Analíticas', href: '/analytics', icon: '📊', description: 'Progreso de estudiantes' },
    ],
    student: [
      { title: 'Mi Progreso', href: '/student', icon: '🎯', description: 'Seguimiento de rendimiento' },
      { title: 'Evaluaciones', href: '/evaluations', icon: '✏️', description: 'Quizzes y exámenes' },
      { title: 'Chat con IA', href: '/chat', icon: '💬', description: 'Ayuda con mis estudios' },
      { title: 'Documentos', href: '/documents', icon: '📚', description: 'Materiales de clase' },
    ],
    parent: [
      { title: 'Mis Hijos', href: '/parent', icon: '👨‍👩‍👧', description: 'Seguimiento de hijos' },
      { title: 'Reportes', href: '/analytics', icon: '📊', description: 'Rendimiento académico' },
    ],
  }

  const cards = roleCards[user.role] || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ReDrive Edu</h1>
                <p className="text-sm text-gray-500">{user.tenant_name || 'Academy'}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleLabel(user.role).includes('Admin') ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                {getRoleLabel(user.role)}
              </span>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user.first_name} {user.last_name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium">
                  {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Bienvenido, {user.first_name} 👋</h2>
          <p className="text-gray-500 mt-1">¿Qué te gustaría hacer hoy?</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Link 
            href="/chat"
            className="flex items-center gap-4 p-4 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-white hover:shadow-lg transition"
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">Chat con IA</p>
              <p className="text-sm opacity-90">Pregunta sobre tus materiales</p>
            </div>
          </Link>

          <Link 
            href="/documents"
            className="flex items-center gap-4 p-4 bg-gradient-to-r from-accent-500 to-accent-600 rounded-xl text-white hover:shadow-lg transition"
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">Subir Documento</p>
              <p className="text-sm opacity-90">Añade materiales de estudio</p>
            </div>
          </Link>

          <Link 
            href="/evaluations"
            className="flex items-center gap-4 p-4 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl text-white hover:shadow-lg transition"
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">Evaluaciones</p>
              <p className="text-sm opacity-90">Tests y quizzes</p>
            </div>
          </Link>
        </div>

        {/* Role-specific cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card, index) => (
            <Link
              key={index}
              href={card.href}
              className="group p-6 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-soft transition-all"
            >
              <div className="text-4xl mb-4">{card.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">
                {card.title}
              </h3>
              <p className="text-sm text-gray-500 mt-1">{card.description}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}