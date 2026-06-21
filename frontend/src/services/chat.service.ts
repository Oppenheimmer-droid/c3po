import api from '@/lib/api'
import type { ChatSession, ChatMessage, Citation } from '@/types'

export interface SendMessageData {
  content: string
}

export interface CreateSessionData {
  title: string
  document_id?: string
  subject_id?: string
}

export const chatService = {
  async createSession(data: CreateSessionData): Promise<ChatSession> {
    const response = await api.post<ChatSession>('/chat/sessions', data)
    return response.data
  },

  async getSessions(params?: { page?: number; page_size?: number }): Promise<ChatSession[]> {
    const response = await api.get<ChatSession[]>('/chat/sessions', { params })
    return response.data
  },

  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await api.get<ChatSession>(`/chat/sessions/${sessionId}`)
    return response.data
  },

  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}`)
  },

  async getMessages(sessionId: string, limit = 50): Promise<ChatMessage[]> {
    const response = await api.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`, {
      params: { limit },
    })
    return response.data
  },

  async sendMessage(sessionId: string, data: SendMessageData): Promise<ChatMessage> {
    const response = await api.post<ChatMessage>(
      `/chat/sessions/${sessionId}/messages`,
      data
    )
    return response.data
  },

  async simpleQuery(
    query: string,
    documentIds?: string[],
    subjectId?: string
  ): Promise<{ answer: string; citations: Citation[]; tokens_used: number }> {
    const response = await api.post<{ answer: string; citations: Citation[]; tokens_used: number }>(
      '/chat/query',
      null,
      {
        params: {
          query,
          document_ids: documentIds?.join(','),
          subject_id: subjectId,
        },
      }
    )
    return response.data
  },

  // Streaming version
  async sendMessageStream(
    sessionId: string,
    data: SendMessageData,
    onChunk: (chunk: string) => void,
    onCitations: (citations: Citation[]) => void,
    onDone: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    // First send the message to get the response ID
    try {
      const response = await this.sendMessage(sessionId, data)
      
      // Then poll or use SSE for the response
      // For now, we'll just call the simple query endpoint
      const result = await this.simpleQuery(data.content)
      
      // Stream the response
      const words = result.answer.split(' ')
      for (let i = 0; i < words.length; i++) {
        onChunk(words[i] + (i < words.length - 1 ? ' ' : ''))
        await new Promise(resolve => setTimeout(resolve, 20))
      }
      
      onCitations(result.citations)
      onDone()
    } catch (error) {
      onError(error as Error)
    }
  },
}

export default chatService