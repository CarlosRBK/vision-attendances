import { useQuery } from '@tanstack/react-query'
import { listAttendances } from '../api'
import type { AttendanceFilters } from '../types'
import { Badge } from '@/shared/ui/Badge'
import { LoadingSpinner } from '@/shared/ui/LoadingSpinner'
import { EmptyState } from '@/shared/ui/EmptyState'

type AttendanceListProps = {
  filters?: AttendanceFilters
  showRefresh?: boolean
}

export default function AttendanceList({ filters, showRefresh = true }: AttendanceListProps) {
  const { data: attendances, isLoading, refetch } = useQuery({
    queryKey: ['attendances', filters],
    queryFn: () => listAttendances(filters)
  })

  const rows = Array.isArray(attendances) ? attendances : []

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      let relative = ''
      if (diffMins < 1) relative = 'Hace un momento'
      else if (diffMins < 60) relative = `Hace ${diffMins} min`
      else if (diffHours < 24) relative = `Hace ${diffHours}h`
      else if (diffDays === 1) relative = 'Ayer'
      else relative = `Hace ${diffDays} días`

      return {
        relative,
        absolute: date.toLocaleString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      }
    } catch {
      return { relative: 'Fecha inválida', absolute: timestamp }
    }
  }

  const getConfidenceBadge = (confidence: number) => {
    const percentage = Math.round(confidence * 100)
    if (percentage >= 80) return <Badge variant="success">{percentage}%</Badge>
    if (percentage >= 60) return <Badge variant="warning">{percentage}%</Badge>
    return <Badge variant="default">{percentage}%</Badge>
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (rows.length === 0) {
    return (
      <EmptyState
        title="No hay asistencias registradas"
        description="Las asistencias aparecerán aquí cuando se detecten rostros conocidos"
      />
    )
  }

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900 dark:text-gray-100">
          Asistencias ({rows.length})
        </h3>
        {showRefresh && (
          <button
            className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            {isLoading ? 'Actualizando…' : 'Actualizar'}
          </button>
        )}
      </div>

      <div className="overflow-x-auto text-black">
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th className="py-3 pr-4 font-medium">Persona</th>
              <th className="py-3 px-4 font-medium">Confianza</th>
              <th className="py-3 px-4 font-medium">Fecha y Hora</th>
              <th className="py-3 px-4 font-medium">Dispositivo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {rows.map((attendance) => {
              const timeInfo = formatTimestamp(attendance.timestamp)
              return (
                <tr
                  key={attendance.id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-3">
                      <div className="size-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 grid place-items-center text-white font-medium">
                        {attendance.person_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {attendance.person_name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          ID: {attendance.person_id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    {getConfidenceBadge(attendance.confidence)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-gray-900 dark:text-gray-100">
                      {timeInfo.absolute}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {timeInfo.relative}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant="default">{attendance.device_id}</Badge>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
