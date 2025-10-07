import { useQuery } from '@tanstack/react-query'
import { listAttendances } from '../api'
import type { AttendanceFilters } from '../types'
import { Badge } from '@/shared/ui/Badge'
import { LoadingSpinner } from '@/shared/ui/LoadingSpinner'
import { EmptyState } from '@/shared/ui/EmptyState'
import { formatInTimeZone, toZonedTime } from 'date-fns-tz'
import { differenceInMinutes, differenceInHours, differenceInDays } from 'date-fns'

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

  const cleanPersonName = (name: string): string => {
    // Remover sufijo UUID si existe (ej: "test_d3ab5f0d" -> "test")
    return name.replace(/_[a-f0-9]{8}$/i, '').replace(/_/g, ' ')
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      const TIMEZONE = 'America/Argentina/Buenos_Aires'
      
      // Parse the UTC timestamp and convert to Buenos Aires timezone
      const utcDate = new Date(timestamp + 'Z') // Add 'Z' to ensure it's treated as UTC
      const buenosAiresDate = toZonedTime(utcDate, TIMEZONE)
      const now = new Date()
      const buenosAiresNow = toZonedTime(now, TIMEZONE)
      
      // Calculate differences
      const diffMins = differenceInMinutes(buenosAiresNow, buenosAiresDate)
      const diffHours = differenceInHours(buenosAiresNow, buenosAiresDate)
      const diffDays = differenceInDays(buenosAiresNow, buenosAiresDate)

      let relative = ''
      if (diffMins < 1) relative = 'Hace un momento'
      else if (diffMins < 60) relative = `Hace ${diffMins} min`
      else if (diffHours < 24) relative = `Hace ${diffHours}h`
      else if (diffDays === 1) relative = 'Ayer'
      else relative = `Hace ${diffDays} días`

      // Format date in Buenos Aires timezone with dd/MM/yyyy format
      const absolute = formatInTimeZone(
        utcDate,
        TIMEZONE,
        'dd/MM/yyyy, HH:mm'
      )

      return {
        relative,
        absolute
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
    <div className="rounded-2xl border border-gray-200 p-4 bg-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">
          Asistencias ({rows.length})
        </h3>
        {showRefresh && (
          <button
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            {isLoading ? 'Actualizando…' : 'Actualizar'}
          </button>
        )}
      </div>

      <div className="overflow-x-auto text-black bg-white">
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500 border-b border-gray-200">
            <tr>
              <th className="py-3 pr-4 font-medium">Persona</th>
              <th className="py-3 px-4 font-medium">Confianza</th>
              <th className="py-3 px-4 font-medium">Fecha y Hora</th>
              <th className="py-3 px-4 font-medium">Dispositivo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {rows.map((attendance) => {
              const timeInfo = formatTimestamp(attendance.timestamp)
              const cleanName = cleanPersonName(attendance.person_name)
              return (
                <tr
                  key={attendance.id}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-3">
                      <div className="size-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 grid place-items-center text-white font-medium">
                        {cleanName.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">
                          {cleanName}
                        </div>
                        <div className="text-xs text-gray-500">
                          ID: {attendance.person_id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    {getConfidenceBadge(attendance.confidence)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-gray-900">
                      {timeInfo.absolute}
                    </div>
                    <div className="text-xs text-gray-500">
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
