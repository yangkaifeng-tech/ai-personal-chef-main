import { apiClient } from './client'
import type { DriverInfo, ListResponse, VehicleInfo } from '../types/api'

export interface PageQuery {
  keyword?: string
  status?: string
  page: number
  page_size: number
}

export interface DriverPayload {
  name: string
  phone: string
  id_card: string | null
  license_no: string | null
  status: string
  rating: number
  hired_at: string | null
}

export interface VehiclePayload {
  plate_no: string
  brand: string
  model: string
  color: string | null
  status: string
  seat_count: number
  driver_id: string | null
  registered_at: string | null
}

export async function fetchDrivers(params: PageQuery): Promise<ListResponse<DriverInfo>> {
  const { data } = await apiClient.get<ListResponse<DriverInfo>>('/drivers', { params })
  return data
}

export async function createDriver(payload: DriverPayload): Promise<DriverInfo> {
  const { data } = await apiClient.post<DriverInfo>('/drivers', payload)
  return data
}

export async function updateDriver(id: string, payload: DriverPayload): Promise<DriverInfo> {
  const { data } = await apiClient.put<DriverInfo>(`/drivers/${id}`, payload)
  return data
}

export async function deleteDriver(id: string): Promise<void> {
  await apiClient.delete(`/drivers/${id}`)
}

export async function fetchVehicles(params: PageQuery & { driver_id?: string }): Promise<ListResponse<VehicleInfo>> {
  const { data } = await apiClient.get<ListResponse<VehicleInfo>>('/vehicles', { params })
  return data
}

export async function createVehicle(payload: VehiclePayload): Promise<VehicleInfo> {
  const { data } = await apiClient.post<VehicleInfo>('/vehicles', payload)
  return data
}

export async function updateVehicle(id: string, payload: VehiclePayload): Promise<VehicleInfo> {
  const { data } = await apiClient.put<VehicleInfo>(`/vehicles/${id}`, payload)
  return data
}

export async function deleteVehicle(id: string): Promise<void> {
  await apiClient.delete(`/vehicles/${id}`)
}
