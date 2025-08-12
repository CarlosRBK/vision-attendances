export type Person = {
  id: string
  full_name: string
  email?: string
  grade?: string
  group?: string
  created_at: string
  updated_at?: string | null
  has_photo: boolean
  photo_url: string | null
}

export type CreatePersonPayload = {
  full_name: string
  email?: string
  grade?: string
  group?: string
  photo?: string // base64 data URL (optional)
}

// Update is JSON-only, photo is handled by a dedicated endpoint
export type UpdatePersonPayload = Partial<Omit<CreatePersonPayload, 'photo'>>
