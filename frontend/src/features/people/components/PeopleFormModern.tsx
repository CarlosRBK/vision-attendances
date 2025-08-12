import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'
import WebcamCapture from './WebcamCapture'
import { createPerson, updatePerson, updatePersonPhoto, deletePersonPhoto } from '../api'
import type { CreatePersonPayload, Person } from '../types'
import { Button } from '@/shared/ui/Button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from '@/shared/ui/Card'

export type PeopleFormProps = {
  person?: Person | null
  onCancel?: () => void
}

const emptyForm: CreatePersonPayload = {
  email: '',
  full_name: '',
  grade: '',
  group: '',
  photo: undefined,
}

export default function PeopleFormModern({ person, onCancel }: PeopleFormProps) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<CreatePersonPayload>(emptyForm)
  const isEditing = useMemo(() => !!person?.id, [person])
  const [webcamKey, setWebcamKey] = useState<number>(0) // Key para forzar remontaje del WebcamCapture

  useEffect(() => {
    if (person) {
      setForm({
        email: person.email || '',
        full_name: person.full_name,
        grade: person.grade || '',
        group: person.group || '',
        photo: undefined,
      })
    } else {
      setForm(emptyForm)
    }
  }, [person])

  const createMutation = useMutation({
    mutationFn: createPerson,
    onSuccess: () => {
      toast.success('Persona creada exitosamente', {
        description: `${form.full_name} ha sido registrado en el sistema.`
      })
      queryClient.invalidateQueries({ queryKey: ['people'] })
      // Limpiar completamente el formulario incluyendo la foto
      setForm(emptyForm)
      // Forzar el remontaje del componente WebcamCapture para limpiar su estado interno
      setWebcamKey(prev => prev + 1)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (payload: { personId: string; data: CreatePersonPayload }) => {
      const { personId, data } = payload
      const savedFields = await updatePerson(personId, {
        email: data.email || undefined,
        full_name: data.full_name,
        grade: data.grade || undefined,
        group: data.group || undefined,
      })
      let saved = savedFields
      if (data.photo) {
        saved = await updatePersonPhoto(personId, data.photo)
      }
      return saved
    },
    onSuccess: () => {
      toast.success('Persona actualizada exitosamente', {
        description: `Los datos de ${form.full_name} han sido actualizados.`
      })
      queryClient.invalidateQueries({ queryKey: ['people'] })
    },
  })

  const deletePhotoMutation = useMutation({
    mutationFn: deletePersonPhoto,
    onSuccess: () => {
      toast.success('Foto eliminada exitosamente', {
        description: 'La foto ha sido eliminada del registro.'
      })
      queryClient.invalidateQueries({ queryKey: ['people'] })
      setForm((f) => ({ ...f, photo: undefined }))
    },
  })

  const isMutating = createMutation.isPending || updateMutation.isPending || deletePhotoMutation.isPending

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.full_name) {
      toast.warning('Información incompleta', {
        description: 'El nombre completo es requerido para continuar.'
      })
      return
    }

    if (isEditing && person?.id) {
      updateMutation.mutate({ personId: person.id, data: form })
    } else {
      createMutation.mutate(form)
    }
  }

  const handleDeletePhoto = () => {
    if (!person?.id) return
    deletePhotoMutation.mutate(person.id)
  }

  const backendOrigin = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''
  const existingPhotoUrl = person?.has_photo && person.photo_url ? `${backendOrigin}${person.photo_url}` : null

  return (
    <Card variant="elevated" className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit}>
        <CardHeader>
          <CardTitle>{isEditing ? 'Editar persona' : 'Registrar nuevo alumno'}</CardTitle>
          <CardDescription>
            {isEditing 
              ? 'Actualiza la información del alumno en el sistema.' 
              : 'Completa el formulario para registrar un nuevo alumno en el sistema.'}
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium mb-1.5">
                  Nombre completo <span className="text-red-500">*</span>
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  value={form.full_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                  placeholder="Juan Pérez"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-1.5">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                  placeholder="juan.perez@escuela.edu"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="grade" className="block text-sm font-medium mb-1.5">
                    Grado
                  </label>
                  <input
                    id="grade"
                    name="grade"
                    value={form.grade}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border  border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                    placeholder="5to"
                  />
                </div>
                
                <div>
                  <label htmlFor="group" className="block text-sm font-medium mb-1.5">
                    Grupo
                  </label>
                  <input
                    id="group"
                    name="group"
                    value={form.group}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border  border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                    placeholder="A"
                  />
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <label className="block text-sm font-medium mb-1.5">
                Foto
              </label>
              <div className="bg-[--muted]/20 rounded-lg p-4 flex flex-col items-center">
                <WebcamCapture
                  key={webcamKey}
                  value={form.photo ?? (isEditing && existingPhotoUrl ? `${existingPhotoUrl}?v=${person?.updated_at ?? ''}` : null)}
                  onChange={(b64) => setForm((f) => ({ ...f, photo: b64 || undefined }))}
                  aspectRatio={1}
                />
                
                <AnimatePresence>
                  {isEditing && person?.has_photo && !form.photo && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="mt-3"
                    >
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleDeletePhoto}
                        isLoading={deletePhotoMutation.isPending}
                        leftIcon={<TrashIcon />}
                      >
                        Eliminar foto
                      </Button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <div>
            {isEditing && (
              <Button
                type="button"
                variant="ghost"
                onClick={() => setForm(emptyForm)}
                disabled={isMutating}
                leftIcon={<ResetIcon />}
              >
                Limpiar
              </Button>
            )}
          </div>
          
          <div className="flex gap-3">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isMutating}
              >
                Cancelar
              </Button>
            )}
            
            <Button
              type="submit"
              variant="primary"
              isLoading={isMutating}
              leftIcon={!isMutating && <SaveIcon />}
            >
              {isMutating
                ? (isEditing ? 'Guardando...' : 'Creando...')
                : (isEditing ? 'Guardar cambios' : 'Crear persona')}
            </Button>
          </div>
        </CardFooter>
      </form>
    </Card>
  )
}

// Icons
function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6H5H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M10 11V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M14 11V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function SaveIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16L21 8V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M17 21V13H7V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M7 3V8H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function ResetIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 2V8H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M21 12C20.9984 10.5062 20.6358 9.03211 19.9493 7.70192C19.2629 6.37174 18.2733 5.21999 17.0632 4.33879C15.8532 3.45758 14.4543 2.86863 12.9863 2.62298C11.5183 2.37733 10.0183 2.48107 8.60001 2.92502C7.18167 3.36896 5.88839 4.14134 4.82372 5.17682C3.75905 6.2123 2.95327 7.48079 2.47173 8.88534C1.99019 10.2899 1.84738 11.7879 2.05412 13.2564C2.26087 14.725 2.81019 16.1272 3.65 17.35L12 22L20.35 17.35C21.0797 16.3282 21.5913 15.1852 21.85 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
