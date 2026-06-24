import api from '@/lib/api'
import type { Evaluation, Question, EvaluationAttempt } from '@/types'

export interface CreateEvaluationData {
  title: string
  description?: string
  document_id: string
  question_count?: number
  difficulty?: number
  evaluation_type?: 'quiz' | 'exam' | 'practice'
  time_limit_minutes?: number
  passing_score?: number
}

export interface SubmitAnswerData {
  question_id: string
  answer_text: string
}

export const evaluationService = {
  async createEvaluation(data: CreateEvaluationData): Promise<Evaluation> {
    const response = await api.post<Evaluation>('/evaluations', data)
    return response.data
  },

  async getEvaluations(params?: {
    page?: number
    page_size?: number
    document_id?: string
  }): Promise<Evaluation[]> {
    const response = await api.get<Evaluation[]>('/evaluations', { params })
    return response.data
  },

  async getEvaluation(evaluationId: string): Promise<Evaluation> {
    const response = await api.get<Evaluation>(`/evaluations/${evaluationId}`)
    return response.data
  },

  async getQuestions(evaluationId: string, includeAnswers = false): Promise<Question[]> {
    const response = await api.get<Question[]>(
      `/evaluations/${evaluationId}/questions`,
      { params: { include_answers: includeAnswers } }
    )
    return response.data
  },

  async startAttempt(evaluationId: string): Promise<EvaluationAttempt> {
    const response = await api.post<EvaluationAttempt>(`/evaluations/${evaluationId}/start`)
    return response.data
  },

  async submitAttempt(
    evaluationId: string,
    attemptId: string,
    answers: SubmitAnswerData[]
  ): Promise<{
    score: number
    passed: boolean
    time_spent_seconds: number
    answers: Array<{ question_id: string; is_correct: boolean; points_earned: number; explanation?: string }>
    feedback: string
  }> {
    const response = await api.post<{
      score: number
      passed: boolean
      time_spent_seconds: number
      answers: Array<{ question_id: string; is_correct: boolean; points_earned: number; explanation?: string }>
      feedback: string
    }>(
      `/evaluations/${evaluationId}/submit`,
      { answers },
      { params: { attempt_id: attemptId } }
    )
    return response.data
  },

  async publishEvaluation(evaluationId: string): Promise<void> {
    await api.post(`/evaluations/${evaluationId}/publish`)
  },

  async getMyAttempts(params?: {
    page?: number
    page_size?: number
  }): Promise<EvaluationAttempt[]> {
    const response = await api.get<EvaluationAttempt[]>('/evaluations/attempts/my', { params })
    return response.data
  },
}

export default evaluationService