import api from '@/lib/api'
import type { TenantAnalytics, StudentProgress } from '@/types'

export const analyticsService = {
  async getTenantOverview(): Promise<TenantAnalytics> {
    const response = await api.get<TenantAnalytics>('/api/v1/analytics/overview')
    return response.data
  },

  async getMyProgress(): Promise<StudentProgress> {
    const response = await api.get<StudentProgress>('/api/v1/analytics/students/me')
    return response.data
  },

  async getStudentProgress(studentId: string): Promise<StudentProgress> {
    const response = await api.get<StudentProgress>(`/api/v1/analytics/students/${studentId}`)
    return response.data
  },

  async getTeacherOverview(): Promise<{
    total_students: number
    evaluations_created: number
    avg_student_score: number | null
    active_students_7d: number
  }> {
    const response = await api.get('/api/v1/analytics/teacher/overview')
    return response.data
  },

  async getDocumentStats(documentId: string): Promise<{
    document_id: string
    title: string
    status: string
    chunk_count: number | null
    chat_sessions: number
    chat_messages: number
    evaluations: number
  }> {
    const response = await api.get(`/api/v1/analytics/documents/${documentId}/stats`)
    return response.data
  },

  async getUsageOverTime(days = 30): Promise<Array<{
    date: string
    chat_sessions: number
    chat_messages: number
    evaluation_attempts: number
  }>> {
    const response = await api.get('/api/v1/analytics/usage', {
      params: { days },
    })
    return response.data
  },
}

export default analyticsService