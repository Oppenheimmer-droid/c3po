import api from '@/lib/api'
import type { Document, DocumentChunk, PaginatedResponse } from '@/types'

export interface DocumentUploadData {
  title: string
  description?: string
  subject_id?: string
  topic_id?: string
  difficulty?: number
  tags?: string[]
}

export const documentService = {
  async uploadDocument(
    file: File,
    data: DocumentUploadData,
    onProgress?: (progress: number) => void
  ): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    if (data.description) formData.append('description', data.description)
    if (data.subject_id) formData.append('subject_id', data.subject_id)
    if (data.topic_id) formData.append('topic_id', data.topic_id)
    if (data.difficulty) formData.append('difficulty', data.difficulty.toString())
    if (data.tags) formData.append('tags', data.tags.join(','))

    const response = await api.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  },

  async getDocuments(params?: {
    page?: number
    page_size?: number
    status?: string
    subject_id?: string
  }): Promise<PaginatedResponse<Document>> {
    const response = await api.get<PaginatedResponse<Document>>('/documents', {
      params,
    })
    return response.data
  },

  async getDocument(documentId: string): Promise<Document> {
    const response = await api.get<Document>(`/documents/${documentId}`)
    return response.data
  },

  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/documents/${documentId}`)
  },

  async getDocumentChunks(documentId: string, skip = 0, limit = 100): Promise<DocumentChunk[]> {
    const response = await api.get<DocumentChunk[]>(`/documents/${documentId}/chunks`, {
      params: { skip, limit },
    })
    return response.data
  },

  async reprocessDocument(documentId: string): Promise<void> {
    await api.post(`/documents/${documentId}/reprocess`)
  },
}

export default documentService