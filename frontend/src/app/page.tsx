import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <div className="text-center max-w-md px-4">
        {/* Logo */}
        <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <svg className="w-12 h-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-3">ReDrive Edu</h1>
        <p className="text-gray-500 mb-8">Tu plataforma de tutoría académica contextual impulsada por IA</p>
        
        {/* Quick Actions */}
        <div className="space-y-3">
          <a
            href="/bypass"
            className="block w-full py-3 px-4 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 transition"
          >
            🚀 Entrar directamente al Dashboard
          </a>
          
          <Link
            href="/auth/login"
            className="block w-full py-3 px-4 bg-white border-2 border-primary-200 text-primary-600 font-medium rounded-xl hover:bg-primary-50 transition"
          >
            🔐 Iniciar sesión
          </Link>
          
          <Link
            href="/auth/register"
            className="block w-full py-3 px-4 bg-accent-500 text-white font-medium rounded-xl hover:bg-accent-600 transition"
          >
            📝 Crear cuenta
          </Link>
        </div>
        
        {/* Demo Credentials */}
        <div className="mt-8 p-4 bg-gray-50 rounded-xl">
          <p className="text-sm font-medium text-gray-700 mb-2">🔑 Credenciales de prueba:</p>
          <div className="text-xs text-gray-500 space-y-1 text-left">
            <p><span className="font-medium">Admin:</span> admin@demo.com / admin123</p>
            <p><span className="font-medium">Profesor:</span> teacher@demo.com / teacher123</p>
            <p><span className="font-medium">Estudiante:</span> student@demo.com / student123</p>
          </div>
        </div>
      </div>
    </div>
  )
}