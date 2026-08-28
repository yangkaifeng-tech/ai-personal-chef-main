import { apiClient } from './client'
import type { ChatMessage, ConversationInfo } from '../types/api'

export async function fetchConversations(): Promise<{ conversations: ConversationInfo[] }> {
  const { data } = await apiClient.get<{ conversations: ConversationInfo[] }>('/conversations')
  return data
}

export async function fetchConversationMessages(conversationId: string): Promise<{ messages: ChatMessage[] }> {
  const { data } = await apiClient.get<{ messages: ChatMessage[] }>(`/conversations/${conversationId}/messages`)
  return data
}

export async function clearConversation(conversationId: string): Promise<void> {
  await apiClient.delete(`/conversations/${conversationId}`)
}

export async function presignImage(filename: string): Promise<{
  uploadUrl: string
  contentType: string
  accessUrl: string
}> {
  const { data } = await apiClient.get('/oss/presign', { params: { filename } })
  return data
}

export async function uploadImage(file: File): Promise<string> {
  const filename = `${Date.now()}-${crypto.randomUUID()}.${file.name.split('.').pop() || 'jpg'}`
  const presign = await presignImage(filename)
  await fetch(presign.uploadUrl, {
    method: 'PUT',
    headers: { 'Content-Type': presign.contentType },
    body: file,
  })
  return presign.accessUrl
}

export type StreamEvent =
  | { event: 'conversation'; payload: { conversation_id: string } }
  | { event: 'status'; payload: { content: string } }
  | { event: 'message'; payload: { content: string } }
  | { event: 'done'; payload: Record<string, never> }

export async function streamChat(
  payload: { message: string; image_url: string | null; conversation_id: string | null },
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok || !response.body) {
    throw new Error(`AI 管家请求失败：${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }
    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split('\n\n')
    buffer = chunks.pop() ?? ''
    for (const chunk of chunks) {
      const eventLine = chunk.split('\n').find((line) => line.startsWith('event: '))
      const dataLine = chunk.split('\n').find((line) => line.startsWith('data: '))
      const eventName = eventLine?.slice(7)
      const dataText = dataLine?.slice(6) ?? '{}'
      if (
        eventName === 'conversation' ||
        eventName === 'status' ||
        eventName === 'message' ||
        eventName === 'done'
      ) {
        onEvent({ event: eventName, payload: JSON.parse(dataText) } as StreamEvent)
      }
    }
  }
}
