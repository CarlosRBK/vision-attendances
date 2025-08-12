import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { listPeople, deletePerson } from '../api'
import type { Person } from '../types'
import { Avatar } from '@/shared/ui/Avatar'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/shared/ui/Card'
import { Button } from '@/shared/ui/Button'
import { Select } from '@/shared/ui/Select'
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'
import { Tooltip } from '@/shared/ui/Tooltip'
import { EmptyState } from '@/shared/ui/EmptyState'
import { SearchInput } from '@/shared/ui/SearchInput'
import { PersonCardSkeleton, PersonRowSkeleton } from '@/shared/ui/Skeleton'
import { Badge } from '@/shared/ui/Badge'
import { NoResultsIcon } from '@/shared/ui/icons/NoResultsIcon'
import { staggeredListVariants, listItemVariants } from '@/shared/ui/PageTransition'

interface PeopleGridProps {
  onEditPerson?: (person: Person) => void;
  onAddPerson?: () => void;
}

export default function PeopleGrid({ onEditPerson, onAddPerson }: PeopleGridProps) {
  const queryClient = useQueryClient()
  const [personToDelete, setPersonToDelete] = useState<Person | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const deleteMutation = useMutation({
    mutationFn: (personId: string) => deletePerson(personId),
    onSuccess: () => {
      toast.success('Persona eliminada exitosamente', {
        description: 'La persona ha sido eliminada del sistema.'
      })
      queryClient.invalidateQueries({ queryKey: ['people'] })
      setPersonToDelete(null)
      setIsDeleteDialogOpen(false)
    },
    onError: (error) => {
      toast.error('Error al eliminar persona', {
        description: 'Ocurrió un error al intentar eliminar la persona.'
      })
      console.error('Error deleting person:', error)
    }
  })

  const { data: people, isLoading, refetch } = useQuery({
    queryKey: ['people'],
    queryFn: listPeople
  })

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filterGrade, setFilterGrade] = useState<string>('')
  const [filterGroup, setFilterGroup] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')  
  
  const rows = Array.isArray(people) ? people : []
  
  // Extract unique grades and groups for filters
  const grades = [...new Set(rows.filter(p => p.grade).map(p => p.grade))].filter(Boolean) as string[]
  const groups = [...new Set(rows.filter(p => p.group).map(p => p.group))].filter(Boolean) as string[]
  
  const gradeOptions = [
    { value: '', label: 'Todos los grados' },
    ...grades.map(grade => ({ value: grade, label: grade }))
  ]
  
  const groupOptions = [
    { value: '', label: 'Todos los grupos' },
    ...groups.map(group => ({ value: group, label: group }))
  ]
  
  // Apply filters and search
  const filteredPeople = useMemo(() => {
    return rows.filter(person => {
      const matchesGrade = !filterGrade || person.grade === filterGrade
      const matchesGroup = !filterGroup || person.group === filterGroup
      
      // Search by name or email if query exists
      const matchesSearch = !searchQuery || (
        (person.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
        person.email?.toLowerCase().includes(searchQuery.toLowerCase()))
      )
      
      return matchesGrade && matchesGroup && matchesSearch
    })
  }, [rows, filterGrade, filterGroup, searchQuery])

  const imgSrc = (p: Person) => p.photo_url ? `http://localhost:8000${p.photo_url}` : ''

  // Track photos that failed to load to avoid setting broken src again on re-renders
  const [failedPhotoIds, setFailedPhotoIds] = useState<Record<string, boolean>>({})

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Alumnos</h2>
          <p className="text-[--muted-foreground]">Gestiona el registro de alumnos en el sistema</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Tooltip content="Actualizar lista de alumnos">
            <Button 
              variant="outline" 
              size="sm"
              leftIcon={<RefreshIcon />}
              onClick={() => {
                setFailedPhotoIds({})
                refetch()
              }} 
              isLoading={isLoading}
              aria-label="Actualizar lista de alumnos"
            >
              {isLoading ? 'Actualizando' : 'Actualizar'}
            </Button>
          </Tooltip>
          
          <Tooltip content="Agregar un nuevo alumno">
            <Button 
              variant="primary" 
              size="sm" 
              leftIcon={<PlusIcon />}
              onClick={() => onAddPerson?.()}
              aria-label="Agregar nuevo alumno"
            >
              Registrar alumno
            </Button>
          </Tooltip>
        </div>
      </div>
      
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-[--muted]/30 rounded-lg p-1">
            <Tooltip content="Vista de cuadrícula">
              <button
                className={`p-1.5 rounded cursor-pointer ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
                onClick={() => setViewMode('grid')}
                aria-label="Vista de cuadrícula"
              >
                <GridIcon />
              </button>
            </Tooltip>
            <Tooltip content="Vista de lista">
              <button
                className={`p-1.5 rounded cursor-pointer ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
                onClick={() => setViewMode('list')}
                aria-label="Vista de lista"
              >
                <ListIcon />
              </button>
            </Tooltip>
          </div>
          
          <p className="text-sm text-[--muted-foreground]">
            {filteredPeople.length} {filteredPeople.length === 1 ? 'alumno' : 'alumnos'}
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <SearchInput
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Buscar por nombre o email"
            className="w-full sm:w-64"
          />
          
          <div className="flex gap-3">
            <Select
              options={gradeOptions}
              value={filterGrade}
              onChange={setFilterGrade}
              placeholder="Filtrar por grado"
              label="Grado"
            />
            
            <Select
              options={groupOptions}
              value={filterGroup}
              onChange={setFilterGroup}
              placeholder="Filtrar por grupo"
              label="Grupo"
            />
          </div>
        </div>
      </div>
      
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {isLoading && (
            <div className="col-span-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, index) => (
                <PersonCardSkeleton key={`skeleton-${index}`} />
              ))}
            </div>
          )}
          
          <AnimatePresence>
            {!isLoading && filteredPeople.length > 0 ? (
              <motion.div
                className="col-span-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                initial="hidden"
                animate="show"
                variants={staggeredListVariants as any}
              >
                {filteredPeople.map((person) => (
              <motion.div
                key={person.id}
                variants={listItemVariants}
                layout
              >
                <Card interactive variant="elevated" className="h-full">
                  <CardHeader className="flex flex-col items-center text-center pb-0">
                    <div className="relative w-32 h-32 mx-auto overflow-hidden rounded-lg">
                      {person.photo_url && !failedPhotoIds[person.id] ? (
                        <img
                          src={imgSrc(person)}
                          alt={`Foto de ${person.full_name}`}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Marcar este id para no intentar recargar la imagen rota en próximos renders
                            setFailedPhotoIds(prev => ({ ...prev, [person.id]: true }))
                            // Cambio inmediato de src para evitar parpadeo mientras re-renderiza
                            e.currentTarget.src = '/placeholder-user.png'
                          }}
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-500 dark:text-gray-400">
                          <UserIcon className="w-12 h-12" />
                        </div>
                      )}
                    </div>
                    <CardTitle className="text-lg">{person.full_name}</CardTitle>
                      <p className="text-sm text-[--muted-foreground] mt-1">{person.email || 'N/A'}</p>
                  </CardHeader>
                  <CardContent className="text-center">
                    <div className="flex justify-center gap-3 mt-2">
                        <div className="px-2.5 py-1 bg-blue-500/10 text-blue-700 rounded-full text-xs font-medium">
                          Grado: {person.grade || 'N/A'}
                        </div>
                        <div className="px-2.5 py-1 bg-purple-500/10 text-purple-700 rounded-full text-xs font-medium">
                          Grupo: {person.group || 'N/A'}
                        </div>
                    </div>
                  </CardContent>
                  <CardFooter className="justify-center gap-2">
                    <Tooltip content="Editar esta persona">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        leftIcon={<EditIcon />}
                        onClick={() => onEditPerson?.(person)}
                        aria-label={`Editar a ${person.full_name}`}
                      >
                        Editar
                      </Button>
                    </Tooltip>
                    <Tooltip content="Eliminar esta persona">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        leftIcon={<TrashIcon />}
                        onClick={() => {
                          setPersonToDelete(person)
                          setIsDeleteDialogOpen(true)
                        }}
                        aria-label={`Eliminar a ${person.full_name}`}
                      >
                        Eliminar
                      </Button>
                    </Tooltip>
                  </CardFooter>
                </Card>
              </motion.div>
              ))}
              </motion.div>
            ) : !isLoading && (
              <div className="col-span-full">
                <EmptyState
                  title={filterGrade || filterGroup ? "No se encontraron alumnos con esos filtros" : "No hay alumnos registrados"}
                  description={filterGrade || filterGroup ? "Prueba con otros filtros o agrega nuevos alumnos" : "Agrega alumnos para comenzar a gestionar la asistencia"}
                  icon={<NoResultsIcon />}
                  action={{
                    label: "Agregar alumno",
                    onClick: () => onAddPerson?.()
                  }}
                />
              </div>
            )}
          </AnimatePresence>
          

        </div>
      ) : (
        <Card>
          <div className="overflow-x-auto relative" style={{ zIndex: 0 }}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-blue-500 text-white border-gray-200">
                  <th className="py-3 px-4 text-center font-medium">Foto</th>
                  <th className="py-3 px-4 text-left font-medium">Nombre</th>
                  <th className="py-3 px-4 text-left font-medium">Email</th>
                  <th className="py-3 px-4 text-center font-medium">Grado</th>
                  <th className="py-3 px-4 text-center font-medium">Grupo</th>
                  <th className="py-3 px-4 text-right font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && Array.from({ length: 5 }).map((_, index) => (
                  <PersonRowSkeleton key={`skeleton-${index}`} />
                ))}
                
                {!isLoading && filteredPeople.length > 0 && (
                  filteredPeople.map((person) => (
                    <motion.tr
                      key={person.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      variants={listItemVariants}
                      className="border-b border-gray-300 hover:bg-blue-100 hover:text-blue-700 hover:cursor-default"
                    >
                      <td className="py-3 px-4">
                        <div className="flex justify-center">
                          <Avatar 
                            src={person.photo_url && !failedPhotoIds[person.id] ? imgSrc(person) : undefined}
                            alt={person.full_name} 
                            fallback={person.full_name.charAt(0)}
                            size="md"
                            className="mx-auto"
                          />
                        </div>
                      </td>
                      <td className="py-3 px-4 font-medium">{person.full_name || 'Sin nombre'}</td>
                      <td className="py-3 px-4">{person.email || 'Sin correo'}</td>
                      <td className="py-3 px-4 text-center">
                        {person.grade ? (
                          <Badge variant="info" size="sm">
                            {person.grade}
                          </Badge>
                        ) : (
                          <span className="text-gray-400">Sin grado</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {person.group ? (
                          <Badge variant="secondary" size="sm">
                            {person.group}
                          </Badge>
                        ) : (
                          <span className="text-gray-400">Sin grupo</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex justify-end gap-2">
                          <Tooltip content="Editar esta persona">
                            <Button 
                              size="sm" 
                              variant="ghost" 
                              leftIcon={<EditIcon />}
                              onClick={() => onEditPerson?.(person)}
                              aria-label={`Editar a ${person.full_name}`}
                            >
                              Editar
                            </Button>
                          </Tooltip>
                          <Tooltip content="Eliminar esta persona">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              leftIcon={<TrashIcon />}
                              onClick={() => {
                                setPersonToDelete(person)
                                setIsDeleteDialogOpen(true)
                              }}
                              aria-label={`Eliminar a ${person.full_name}`}
                            >
                              Eliminar
                            </Button>
                          </Tooltip>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                )}
                
                {!isLoading && filteredPeople.length === 0 && (
                  <tr>
                    <td colSpan={6}>
                      <EmptyState
                        title={filterGrade || filterGroup ? "No se encontraron personas con esos filtros" : "No hay personas registradas"}
                        description={filterGrade || filterGroup ? "Prueba con otros filtros o agrega nuevas personas" : "Agrega personas para comenzar a gestionar la asistencia"}
                        icon={<NoResultsIcon />}
                        action={{
                          label: "Agregar persona",
                          onClick: () => onAddPerson?.()
                        }}
                        className="py-8"
                      />
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
      
      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        title={`¿Eliminar a ${personToDelete?.full_name}?`}
        description="Esta acción no se puede deshacer. La persona será eliminada permanentemente del sistema."
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={() => deleteMutation.mutate(personToDelete?.id || '')}
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

// Icons
function PlusIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 5V19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function RefreshIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3.51 9.00001C4.01717 7.56455 4.87913 6.2854 6.01547 5.27543C7.1518 4.26547 8.52547 3.55978 10.0083 3.22427C11.4911 2.88877 13.0348 2.93436 14.4952 3.35679C15.9556 3.77922 17.2853 4.56473 18.36 5.64001L23 10M1 14L5.64 18.36C6.71475 19.4353 8.04437 20.2208 9.50481 20.6432C10.9652 21.0657 12.5089 21.1112 13.9917 20.7757C15.4745 20.4402 16.8482 19.7346 17.9845 18.7246C19.1209 17.7146 19.9828 16.4355 20.49 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function GridIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 3H3V10H10V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M21 3H14V10H21V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M21 14H14V21H21V14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M10 14H3V21H10V14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function ListIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 6H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3 6H3.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3 12H3.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3 18H3.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function EditIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6H5H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M10 11V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M14 11V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function UserIcon({ className = '' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
