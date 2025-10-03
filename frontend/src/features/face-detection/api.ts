import axios from 'axios'
import type { DetectResponse, HealthResponse, AttendanceTodayResponse } from './types'

// Cliente HTTP separado para face-services (puerto 5001)
const faceServicesClient = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Detecta rostros en un frame (imagen en base64)
 */
export async function detectFaces(frameBase64: string): Promise<DetectResponse> {
  const response = await faceServicesClient.post<DetectResponse>('/detect', {
    frame: frameBase64
  })
  return response.data
}

/**
 * Verifica el estado del servicio de detección facial
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await faceServicesClient.get<HealthResponse>('/health')
  return response.data
}

/**
 * Recarga manualmente los rostros conocidos
 */
export async function reloadFaces(): Promise<{ success: boolean; message: string; count: number }> {
  const response = await faceServicesClient.post<{ success: boolean; message: string; count: number }>('/reload')
  return response.data
}

/**
 * Obtiene la lista de asistencia del día actual
 */
export async function getAttendanceToday(): Promise<AttendanceTodayResponse> {
  const response = await faceServicesClient.get<AttendanceTodayResponse>('/attendance/today')
  return response.data
}
