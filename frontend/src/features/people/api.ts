import api from '@/lib/http'
import { dataURLToFile } from '@/utils/base64'
import type { CreatePersonPayload, Person, UpdatePersonPayload } from './types'

export async function listPeople(): Promise<Person[]> {
  const { data } = await api.get<unknown>('/people/')
  // Normalize to array to accommodate backends that wrap results
  if (Array.isArray(data)) return data as Person[]
  const anyData = data as any
  if (anyData && Array.isArray(anyData.results)) return anyData.results as Person[]
  if (anyData && Array.isArray(anyData.data)) return anyData.data as Person[]
  return []
}

export async function getPerson(personId: string): Promise<Person> {
  const { data } = await api.get<Person>(`/people/${personId}`)
  return data
}

export async function createPerson(payload: CreatePersonPayload): Promise<Person> {
  // Backend expects multipart/form-data for create
  const fd = new FormData()
  fd.append('full_name', payload.full_name)
  if (payload.email && payload.email.trim()) fd.append('email', payload.email)
  if (payload.grade && payload.grade.trim()) fd.append('grade', payload.grade)
  if (payload.group && payload.group.trim()) fd.append('group', payload.group)
  if (payload.photo) fd.append('photo', dataURLToFile(payload.photo, 'photo.jpg'))
  const { data } = await api.post<Person>('/people/', fd)
  return data
}

export async function updatePerson(personId: string, payload: UpdatePersonPayload): Promise<Person> {
  // Backend expects JSON-only for update (photo handled separately)
  const body: Record<string, any> = {}
  if (payload.full_name && payload.full_name.trim()) body.full_name = payload.full_name
  if (payload.email && payload.email.trim()) body.email = payload.email
  if (payload.grade && payload.grade.trim()) body.grade = payload.grade
  if (payload.group && payload.group.trim()) body.group = payload.group
  const { data } = await api.put<Person>(`/people/${personId}`, body)
  return data
}

export async function updatePersonPhoto(personId: string, photo: string | File): Promise<Person> {
  const fd = new FormData()
  const file = typeof photo === 'string' ? dataURLToFile(photo, 'photo.jpg') : photo
  fd.append('photo', file)
  const { data } = await api.put<Person>(`/people/${personId}/photo`, fd)
  return data
}

export async function deletePersonPhoto(personId: string): Promise<Person> {
  const { data } = await api.delete<Person>(`/people/${personId}/photo`)
  return data
}

export async function deletePerson(personId: string): Promise<void> {
  await api.delete(`/people/${personId}`)
}
