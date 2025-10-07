import api from '@/lib/http'
import type { Attendance, AttendanceFilters } from './types'

export async function listAttendances(filters?: AttendanceFilters): Promise<Attendance[]> {
  const params = new URLSearchParams()
  
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.person_id) params.append('person_id', filters.person_id)
  if (filters?.device_id) params.append('device_id', filters.device_id)
  if (filters?.limit) params.append('limit', filters.limit.toString())
  if (filters?.skip) params.append('skip', filters.skip.toString())
  
  const { data } = await api.get<unknown>(`/attendances/?${params.toString()}`)
  
  // Normalize to array
  if (Array.isArray(data)) return data as Attendance[]
  const anyData = data as any
  if (anyData && Array.isArray(anyData.results)) return anyData.results as Attendance[]
  if (anyData && Array.isArray(anyData.data)) return anyData.data as Attendance[]
  return []
}

export async function getTodayAttendances(person_id?: string): Promise<Attendance[]> {
  const params = person_id ? `?person_id=${person_id}` : ''
  const { data } = await api.get<unknown>(`/attendances/today/${params}`)
  
  // Normalize to array
  if (Array.isArray(data)) return data as Attendance[]
  const anyData = data as any
  if (anyData && Array.isArray(anyData.results)) return anyData.results as Attendance[]
  if (anyData && Array.isArray(anyData.data)) return anyData.data as Attendance[]
  return []
}

export async function getAttendance(attendanceId: string): Promise<Attendance> {
  const { data } = await api.get<Attendance>(`/attendances/${attendanceId}`)
  return data
}
