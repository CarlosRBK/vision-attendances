export type Attendance = {
  id: string
  person_id: string
  person_name: string
  confidence: number
  timestamp: string
  device_id: string
}

export type AttendanceFilters = {
  start_date?: string
  end_date?: string
  person_id?: string
  device_id?: string
  limit?: number
  skip?: number
}
