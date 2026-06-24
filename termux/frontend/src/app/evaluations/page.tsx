'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { evaluationService } from '@/services'
import { formatRelativeTime } from '@/lib/utils'
import type { Evaluation, Question, EvaluationAttempt } from '@/types'

export default function EvaluationsPage() {
  const [selectedEvaluation, setSelectedEvaluation] = useState<Evaluation | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [currentAttempt, setCurrentAttempt] = useState<EvaluationAttempt | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [results, setResults] = useState<{
    score: number
    passed: boolean
    feedback: string
    answers: Array<{ question_id: string; is_correct: boolean; points_earned: number; explanation?: string }>
  } | null>(null)
  const [timeLeft, setTimeLeft] = useState<number | null>(null)

  // Fetch evaluations
  const { data: evaluations = [], isLoading } = useQuery({
    queryKey: ['evaluations'],
    queryFn: () => evaluationService.getEvaluations(),
  })

  // Fetch my attempts
  const { data: attempts = [] } = useQuery({
    queryKey: ['evaluation-attempts'],
    queryFn: () => evaluationService.getMyAttempts(),
  })

  // Start attempt mutation
  const startAttemptMutation = useMutation({
    mutationFn: (evaluationId: string) => evaluationService.startAttempt(evaluationId),
    onSuccess: (attempt) => {
      setCurrentAttempt(attempt)
      setAnswers({})
      setShowResults(false)
      setResults(null)
    },
  })

  // Submit attempt mutation
  const submitMutation = useMutation({
    mutationFn: ({ evaluationId, attemptId }: { evaluationId: string; attemptId: string }) =>
      evaluationService.submitAttempt(
        evaluationId,
        attemptId,
        Object.entries(answers).map(([question_id, answer_text]) => ({ question_id, answer_text }))
      ),
    onSuccess: (result) => {
      setResults(result)
      setShowResults(true)
      toast.success(result.passed ? '¡Aprobado!' : 'Revisa tus resultados')
    },
  })

  // Load questions when evaluation selected
  useEffect(() => {
    if (selectedEvaluation) {
      evaluationService.getQuestions(selectedEvaluation.id).then(setQuestions)
      if (selectedEvaluation.time_limit_minutes) {
        setTimeLeft(selectedEvaluation.time_limit_minutes * 60)
      }
    }
  }, [selectedEvaluation])

  // Timer
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || !currentAttempt) return
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev === null || prev <= 1) {
          // Auto-submit when time runs out
          if (currentAttempt) {
            submitMutation.mutate({
              evaluationId: selectedEvaluation!.id,
              attemptId: currentAttempt.id,
            })
          }
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [timeLeft, currentAttempt, selectedEvaluation, submitMutation])

  const handleStartAttempt = (evaluation: Evaluation) => {
    setSelectedEvaluation(evaluation)
    startAttemptMutation.mutate(evaluation.id)
  }

  const handleSubmit = () => {
    if (currentAttempt && selectedEvaluation) {
      submitMutation.mutate({
        evaluationId: selectedEvaluation.id,
        attemptId: currentAttempt.id,
      })
    }
  }

  const handleBackToList = () => {
    setSelectedEvaluation(null)
    setCurrentAttempt(null)
    setQuestions([])
    setAnswers({})
    setShowResults(false)
    setResults(null)
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Taking evaluation view
  if (currentAttempt && selectedEvaluation) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <button
                  onClick={handleBackToList}
                  className="text-sm text-gray-500 hover:text-primary-600 mb-2"
                >
                  ← Volver a evaluaciones
                </button>
                <h1 className="text-xl font-bold text-gray-900">{selectedEvaluation.title}</h1>
                <p className="text-gray-500 mt-1">{selectedEvaluation.question_count} preguntas</p>
              </div>
              {timeLeft !== null && (
                <div className={`text-2xl font-mono font-bold ${timeLeft < 60 ? 'text-red-500' : 'text-gray-900'}`}>
                  {formatTime(timeLeft)}
                </div>
              )}
            </div>
          </div>

          {/* Questions */}
          {!showResults ? (
            <>
              <div className="space-y-6">
                {questions.map((question, index) => (
                  <div key={question.id} className="bg-white rounded-2xl border border-gray-100 p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="w-8 h-8 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center font-medium">
                        {index + 1}
                      </span>
                      <span className="text-sm text-gray-500">{question.points} punto{question.points > 1 ? 's' : ''}</span>
                    </div>
                    
                    <p className="text-lg font-medium text-gray-900 mb-6">{question.question_text}</p>

                    {question.question_type === 'multiple_choice' && question.options && (
                      <div className="space-y-3">
                        {question.options.map((option, idx) => (
                          <label
                            key={idx}
                            className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition ${
                              answers[question.id] === idx.toString()
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-100 hover:border-gray-200'
                            }`}
                          >
                            <input
                              type="radio"
                              name={`question-${question.id}`}
                              checked={answers[question.id] === idx.toString()}
                              onChange={() => setAnswers({ ...answers, [question.id]: idx.toString() })}
                              className="w-5 h-5 text-primary-600"
                            />
                            <span className="text-gray-700">{option}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {question.question_type === 'true_false' && (
                      <div className="flex gap-4">
                        {['True', 'False'].map((option) => (
                          <label
                            key={option}
                            className={`flex-1 flex items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition ${
                              answers[question.id] === option.toLowerCase()
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-100 hover:border-gray-200'
                            }`}
                          >
                            <input
                              type="radio"
                              name={`question-${question.id}`}
                              checked={answers[question.id] === option.toLowerCase()}
                              onChange={() => setAnswers({ ...answers, [question.id]: option.toLowerCase() })}
                              className="w-5 h-5 text-primary-600"
                            />
                            <span className="ml-2 text-gray-700 font-medium">{option}</span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handleSubmit}
                disabled={Object.keys(answers).length < questions.length}
                className="w-full mt-6 py-4 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Enviar respuestas
              </button>
            </>
          ) : (
            /* Results View */
            <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center">
              <div className={`w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center ${
                results?.passed ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {results?.passed ? (
                  <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                {results?.score.toFixed(0)}%
              </h2>
              <p className={`text-lg mb-6 ${results?.passed ? 'text-green-600' : 'text-red-600'}`}>
                {results?.passed ? '¡Aprobado!' : 'No aprobado'}
              </p>

              <p className="text-gray-600 mb-8">{results?.feedback}</p>

              {/* Answer Review */}
              <div className="text-left border-t border-gray-100 pt-6">
                <h3 className="font-semibold text-gray-900 mb-4">Revisión de respuestas</h3>
                <div className="space-y-3">
                  {questions.map((question, idx) => {
                    const result = results?.answers.find(a => a.question_id === question.id)
                    return (
                      <div key={question.id} className={`p-4 rounded-xl ${
                        result?.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                      }`}>
                        <div className="flex items-center gap-2 mb-2">
                          {result?.is_correct ? (
                            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          )}
                          <span className="font-medium">{idx + 1}. {question.question_text}</span>
                        </div>
                        {result?.explanation && (
                          <p className="text-sm text-gray-600 ml-7">{result.explanation}</p>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              <button
                onClick={handleBackToList}
                className="mt-6 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 transition"
              >
                Volver a evaluaciones
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Evaluations list
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Evaluaciones</h1>
          <p className="text-gray-500 mt-1">Quizzes y exámenes disponibles</p>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : evaluations.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">No hay evaluaciones</h3>
            <p className="text-gray-500 mt-2">Aún no se han publicado evaluaciones para ti</p>
          </div>
        ) : (
          <div className="space-y-4">
            {evaluations.map((evaluation) => {
              const relatedAttempts = attempts.filter(a => a.evaluation_id === evaluation.id)
              const lastAttempt = relatedAttempts[0]
              
              return (
                <div
                  key={evaluation.id}
                  className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-soft transition"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{evaluation.title}</h3>
                        {evaluation.is_published && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                            Disponible
                          </span>
                        )}
                      </div>
                      {evaluation.description && (
                        <p className="text-gray-500 mb-4">{evaluation.description}</p>
                      )}
                      <div className="flex items-center gap-6 text-sm text-gray-400">
                        <span>{evaluation.question_count} preguntas</span>
                        {evaluation.time_limit_minutes && (
                          <span>⏱️ {evaluation.time_limit_minutes} min</span>
                        )}
                        <span>📊 {evaluation.passing_score}% para aprobar</span>
                      </div>
                    </div>
                    <div className="text-right">
                      {lastAttempt ? (
                        <div className="text-sm">
                          <p className="text-gray-500">Tu última puntuación</p>
                          <p className={`text-2xl font-bold ${lastAttempt.passed ? 'text-green-600' : 'text-red-600'}`}>
                            {lastAttempt.score?.toFixed(0)}%
                          </p>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleStartAttempt(evaluation)}
                          disabled={!evaluation.is_published}
                          className="px-6 py-3 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                        >
                          {evaluation.is_published ? 'Comenzar' : 'No disponible'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}