import { apiClient } from './client'
import type { LoginResponse } from '../types/api'

export interface LoginPayload {
  username: string
  password: string
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', payload)
  return data
}

export async function getMe(): Promise<Omit<LoginResponse, 'access_token' | 'token_type'>> {
  const { data } = await apiClient.get<Omit<LoginResponse, 'access_token' | 'token_type'>>('/auth/me')
  return data
}
