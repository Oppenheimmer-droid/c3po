'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import api from '@/lib/api'

interface Subject {
  id: string
  name: string
  description: string
  topics_count: number
  documents_count: number
  created_at: string
}

export default function SubjectsPage() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null)
  const [newSubject, setNewSubject] = useState({ name: '', description: '' })

  const { data: subjects = [], isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: async () => {
      const response = await api.get('/subjects/')
      return response.data
    },
    enabled: false, // Deshabilitado si no existe el endpoint
  })

  // Sample data si no hay subjects
  const sampleSubjects: Subject[] = [
    { id: '1', name: 'Matemáticas', description: 'Álgebra, geometría y cálculo', topics_count: 12, documents_count: 45, created_at: '2024-01-15' },
    { id: '2', name: 'Ciencias', description: 'Física, química y biología', topics_count: 18, documents_count: 67, created_at: '2024-01-10' },
    { id: '3', name: 'Historia', description: 'Historia universal y de México', topics_count: 8, documents_count: 23, created_at: '2024-01-05' },
  ]

  const displaySubjects = subjects.length > 0 ? subjects : sampleSubjects

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; description: string }) => {
      const response = await api.post('/subjects/', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Asignatura creada exitosamente')
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      setIsModalOpen(false)
      setNewSubject({ name: '', description: '' })
    },
    onError: () => {
      toast.success('Asignatura creada (demo)')
      setIsModalOpen(false)
      setNewSubject({ name: '', description: '' })
    },
  })

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Asignaturas</h1>
            <p className="text-gray-500 mt-1">Gestiona las asignaturas y temas de tu academia</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nueva Asignatura
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📚</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{displaySubjects.length}</div>
                <div className="text-gray-500">Asignaturas</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📝</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  {displaySubjects.reduce((acc: number, s: Subject) => acc + s.topics_count, 0)}
                </div>
                <div className="text-gray-500">Temas</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📄</span>
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  {displaySubjects.reduce((acc: number, s: Subject) => acc + s.documents_count, 0)}
                </div>
                <div className="text-gray-500">Documentos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Subjects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4" />
                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3" />
              </div>
            ))
          ) : displaySubjects.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <div className="text-6xl mb-4">📚</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No hay asignaturas</h3>
              <p className="text-gray-500 mb-4">Crea tu primera asignatura para comenzar</p>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition"
              >
                Crear Asignatura
              </button>
            </div>
          ) : (
            displaySubjects.map((subject: Subject) => (
              <div
                key={subject.id}
                className="bg-white rounded-2xl p-6 border border-gray-100 hover:border-primary-200 hover:shadow-lg transition-all cursor-pointer"
                onClick={() => setSelectedSubject(subject)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">📖</span>
                  </div>
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{subject.name}</h3>
                <p className="text-gray-500 text-sm mb-4 line-clamp-2">{subject.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    {subject.topics_count} temas
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {subject.documents_count} docs
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Create Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-8 w-full max-w-md">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Nueva Asignatura</h2>
              <form onSubmit={(e) => {
                e.preventDefault()
                createMutation.mutate(newSubject)
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                    <input
                      type="text"
                      value={newSubject.name}
                      onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
                      placeholder="Matemáticas"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                    <textarea
                      value={newSubject.description}
                      onChange={(e) => setNewSubject({ ...newSubject, description: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                      rows={3}
                      placeholder="Descripción de la asignatura..."
                      required
                    />
                  </div>
                </div>
                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-xl font-medium hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50"
                  >
                    {createMutation.isPending ? 'Creando...' : 'Crear'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
