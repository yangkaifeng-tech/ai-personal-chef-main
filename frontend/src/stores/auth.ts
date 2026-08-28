import { defineStore } from 'pinia'
import { getMe, login, type LoginPayload } from '../api/auth'
import type { MenuItem, UserInfo } from '../types/api'

interface AuthSnapshot {
  user: UserInfo | null
  menus: MenuItem[]
  permissions: string[]
}

function readSnapshot(): AuthSnapshot {
  const raw = localStorage.getItem('auth_state')
  if (!raw) {
    return { user: null, menus: [], permissions: [] }
  }
  try {
    return JSON.parse(raw) as AuthSnapshot
  } catch {
    return { user: null, menus: [], permissions: [] }
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') ?? '',
    ...readSnapshot(),
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    hasPermission: (state) => (code: string) => state.permissions.includes(code),
  },
  actions: {
    persist() {
      const snapshot: AuthSnapshot = {
        user: this.user,
        menus: this.menus,
        permissions: this.permissions,
      }
      localStorage.setItem('auth_state', JSON.stringify(snapshot))
    },
    async login(payload: LoginPayload) {
      const data = await login(payload)
      this.token = data.access_token
      this.user = data.user
      this.menus = data.menus
      this.permissions = data.permissions
      localStorage.setItem('access_token', data.access_token)
      this.persist()
    },
    async refresh() {
      if (!this.token) {
        return
      }
      const data = await getMe()
      this.user = data.user
      this.menus = data.menus
      this.permissions = data.permissions
      this.persist()
    },
    logout() {
      this.token = ''
      this.user = null
      this.menus = []
      this.permissions = []
      localStorage.removeItem('access_token')
      localStorage.removeItem('auth_state')
    },
  },
})
