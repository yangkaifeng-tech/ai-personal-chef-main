import { apiClient } from './client'
import type { ButtonInfo, ListResponse, MenuItem, RoleInfo, UserInfo } from '../types/api'

export interface UserPayload {
  username: string
  password?: string
  name: string | null
  status: string
  role_ids: string[]
}

export interface RolePayload {
  name: string
  code: string
  description: string | null
}

export interface MenuPayload {
  parent_id: string | null
  name: string
  path: string
  component: string
  icon: string | null
  sort: number
  visible: boolean
  permission_code: string | null
}

export interface ButtonPayload {
  menu_id: string
  name: string
  code: string
  description: string | null
}

export async function fetchUsers(params: {
  keyword?: string
  status?: string
  page: number
  page_size: number
}): Promise<ListResponse<UserInfo>> {
  const { data } = await apiClient.get<ListResponse<UserInfo>>('/permissions/users', { params })
  return data
}

export async function createUser(payload: UserPayload & { password: string }): Promise<UserInfo> {
  const { data } = await apiClient.post<UserInfo>('/permissions/users', payload)
  return data
}

export async function updateUser(id: string, payload: UserPayload): Promise<UserInfo> {
  const { data } = await apiClient.put<UserInfo>(`/permissions/users/${id}`, payload)
  return data
}

export async function deleteUser(id: string): Promise<void> {
  await apiClient.delete(`/permissions/users/${id}`)
}

export async function fetchRoles(): Promise<ListResponse<RoleInfo>> {
  const { data } = await apiClient.get<ListResponse<RoleInfo>>('/permissions/roles')
  return data
}

export async function createRole(payload: RolePayload): Promise<RoleInfo> {
  const { data } = await apiClient.post<RoleInfo>('/permissions/roles', payload)
  return data
}

export async function updateRole(id: string, payload: RolePayload): Promise<RoleInfo> {
  const { data } = await apiClient.put<RoleInfo>(`/permissions/roles/${id}`, payload)
  return data
}

export async function deleteRole(id: string): Promise<void> {
  await apiClient.delete(`/permissions/roles/${id}`)
}

export async function assignRoleMenus(id: string, ids: string[]): Promise<RoleInfo> {
  const { data } = await apiClient.put<RoleInfo>(`/permissions/roles/${id}/menus`, { ids })
  return data
}

export async function assignRoleButtons(id: string, ids: string[]): Promise<RoleInfo> {
  const { data } = await apiClient.put<RoleInfo>(`/permissions/roles/${id}/buttons`, { ids })
  return data
}

export async function fetchMenus(tree = false): Promise<ListResponse<MenuItem>> {
  const { data } = await apiClient.get<ListResponse<MenuItem>>('/permissions/menus', { params: { tree } })
  return data
}

export async function createMenu(payload: MenuPayload): Promise<MenuItem> {
  const { data } = await apiClient.post<MenuItem>('/permissions/menus', payload)
  return data
}

export async function updateMenu(id: string, payload: MenuPayload): Promise<MenuItem> {
  const { data } = await apiClient.put<MenuItem>(`/permissions/menus/${id}`, payload)
  return data
}

export async function deleteMenu(id: string): Promise<void> {
  await apiClient.delete(`/permissions/menus/${id}`)
}

export async function fetchButtons(): Promise<ListResponse<ButtonInfo>> {
  const { data } = await apiClient.get<ListResponse<ButtonInfo>>('/permissions/buttons')
  return data
}

export async function createButton(payload: ButtonPayload): Promise<ButtonInfo> {
  const { data } = await apiClient.post<ButtonInfo>('/permissions/buttons', payload)
  return data
}

export async function updateButton(id: string, payload: ButtonPayload): Promise<ButtonInfo> {
  const { data } = await apiClient.put<ButtonInfo>(`/permissions/buttons/${id}`, payload)
  return data
}

export async function deleteButton(id: string): Promise<void> {
  await apiClient.delete(`/permissions/buttons/${id}`)
}
