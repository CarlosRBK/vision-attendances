import { useState } from 'react'
import AttendanceList from '../components/AttendanceList'
import { Card } from '@/shared/ui/Card'
import type { AttendanceFilters } from '../types'

export default function AttendancePage() {
  const [filters, setFilters] = useState<AttendanceFilters>({
    limit: 100,
    skip: 0
  })

  const [showToday, setShowToday] = useState(false)

  const handleTodayToggle = () => {
    if (!showToday) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      setFilters({
        ...filters,
        start_date: today.toISOString(),
        end_date: new Date().toISOString()
      })
    } else {
      const { start_date, end_date, ...rest } = filters
      setFilters(rest)
    }
    setShowToday(!showToday)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          📊 Registro de Asistencias
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Visualiza y gestiona las asistencias registradas por reconocimiento facial
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex items-center gap-4 flex-wrap">
          <button
            onClick={handleTodayToggle}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              showToday
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {showToday ? '✓ Hoy' : 'Mostrar solo hoy'}
          </button>

          <div className="flex-1" />

          <div className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando últimas {filters.limit} asistencias
          </div>
        </div>
      </Card>

      {/* Attendance List */}
      <AttendanceList filters={filters} />
    </div>
  )
}
