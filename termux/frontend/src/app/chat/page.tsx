'use client'

import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { chatService } from '@/services'
import { useChatStore } from '@/lib/store'
import type { ChatSession, ChatMessage, Citation } from '@/types'

export default function ChatPage() {
  const queryClient = useQueryClient()
  const { sessions, currentSessionId, setCurrentSession, addSession, setStreaming } = useChatStore()
  const [inputMessage, setInputMessage] = useState('')
  const [streamingText, setStreamingText] = useState('')
  const [currentCitations, setCurrentCitations] = useState<Citation[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Fetch sessions
  const { data: allSessions, isLoading: loadingSessions } = useQuery({
    queryKey: ['chat-sessions'],
    queryFn: () => chatService.getSessions(),
  })

  // Fetch messages for current session
  const { data: messages = [], isLoading: loadingMessages } = useQuery({
    queryKey: ['chat-messages', currentSessionId],
    queryFn: () => currentSessionId ? chatService.getMessages(currentSessionId) : Promise.resolve([]),
    enabled: !!currentSessionId,
  })

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: (data: { title: string }) => chatService.createSession(data),
    onSuccess: (session) => {
      addSession({ id: session.id, title: session.title })
      setCurrentSession(session.id)
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
    },
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: ({ sessionId, content }: { sessionId: string; content: string }) =>
      chatService.sendMessage(sessionId, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-messages', currentSessionId] })
    },
  })

  // Simple query mutation (no session required)
  const simpleQueryMutation = useMutation({
    mutationFn: (query: string) => chatService.simpleQuery(query),
    onSuccess: (result) => {
      setStreamingText(result.answer)
      setCurrentCitations(result.citations)
      setStreaming(false)
    },
    onError: (error) => {
      toast.error('Error al obtener respuesta')
      setStreaming(false)
    },
  })

  useEffect(() => {
    if (allSessions?.length && !currentSessionId) {
      setCurrentSession(allSessions[0].id)
    }
  }, [allSessions, currentSessionId, setCurrentSession])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    if (!currentSessionId) {
      // Create a new session first
      const title = inputMessage.substring(0, 50) + (inputMessage.length > 50 ? '...' : '')
      await createSessionMutation.mutateAsync({ title })
    }

    setStreaming(true)
    setStreamingText('')
    setCurrentCitations([])

    try {
      await simpleQueryMutation.mutateAsync(inputMessage)
    } catch {
      // Error handled in mutation
    }

    setInputMessage('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSendMessage()
    }
  }

  const handleNewChat = async () => {
    await createSessionMutation.mutateAsync({
      title: 'Nueva conversación',
    })
  }

  const displayMessages = messages

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Sidebar - Sessions */}
      <aside className="w-80 bg-white border-r border-gray-100 flex flex-col">
        <div className="p-4 border-b border-gray-100">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nuevo Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {loadingSessions ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-12 bg-gray-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="space-y-1">
              {allSessions?.map((session) => (
                <button
                  key={session.id}
                  onClick={() => setCurrentSession(session.id)}
                  className={`w-full text-left px-4 py-3 rounded-xl transition ${
                    currentSessionId === session.id
                      ? 'bg-primary-50 text-primary-700'
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <p className="font-medium truncate">{session.title}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {session.message_count} mensajes
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-gray-50">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {displayMessages.length === 0 && !streamingText && (
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Bienvenido al Chat con IA</h3>
                <p className="text-gray-500 mt-2 max-w-md mx-auto">
                  Pregunta sobre tus materiales de estudio. Obtén respuestas citadas directamente de tus documentos.
                </p>
              </div>
            )}

            {displayMessages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xl px-6 py-4 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border border-gray-200'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  
                  {message.citations && message.citations.length > 0 && (
                    <div className={`mt-4 pt-4 ${message.role === 'user' ? 'border-t-primary-500' : 'border-t-gray-200'} border-t`}>
                      <p className="text-xs font-medium mb-2 opacity-70">Fuentes:</p>
                      <div className="space-y-2">
                        {message.citations.map((citation, idx) => (
                          <div
                            key={idx}
                            className={`text-xs p-2 rounded-lg ${
                              message.role === 'user' ? 'bg-primary-500' : 'bg-gray-50'
                            }`}
                          >
                            <p className="font-medium">{citation.source}</p>
                            {citation.page && <p className="opacity-70">Página {citation.page}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Streaming Response */}
            {streamingText && (
              <div className="flex justify-start">
                <div className="max-w-xl px-6 py-4 rounded-2xl bg-white border border-gray-200">
                  <p className="whitespace-pre-wrap">{streamingText}</p>
                  {currentCitations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-500 mb-2">Fuentes:</p>
                      <div className="space-y-2">
                        {currentCitations.map((citation, idx) => (
                          <div key={idx} className="text-xs p-2 rounded-lg bg-gray-50">
                            <p className="font-medium">{citation.source}</p>
                            {citation.page && <p className="text-gray-400">Página {citation.page}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white border-t border-gray-100">
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu pregunta... (Ctrl+Enter para enviar)"
                className="w-full px-6 py-4 pr-24 bg-gray-50 border border-gray-200 rounded-2xl resize-none focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition"
                rows={1}
              />
              <div className="absolute right-4 bottom-4 flex items-center gap-2">
                <span className="text-xs text-gray-400">Ctrl+Enter</span>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || simpleQueryMutation.isPending}
                  className="p-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {simpleQueryMutation.isPending ? (
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              Las respuestas incluyen citas de tus documentos. Puedes confiar en la información proporcionada.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}