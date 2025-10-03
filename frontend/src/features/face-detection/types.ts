export type FaceDetection = {
  name: string
  confidence: number
  box: {
    x: number
    y: number
    width: number
    height: number
  }
}

export type DetectResponse = {
  success: boolean
  detections: FaceDetection[]
  timestamp: string
  known_faces: number
}

export type HealthResponse = {
  status: string
  service: string
  known_faces: number
  faces_folder: string
}

export type AttendanceTodayResponse = {
  date: string
  count: number
  registered: string[]
}
