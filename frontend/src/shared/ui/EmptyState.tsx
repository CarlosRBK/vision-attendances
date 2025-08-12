import { motion } from 'framer-motion'
import { type ReactNode } from 'react'
import { Button } from './Button'

interface EmptyStateProps {
  title: string
  description?: string
  icon?: ReactNode
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

/**
 * Componente para mostrar un estado vacío con estilo premium
 * Útil para mostrar cuando no hay datos disponibles en listas, grids, etc.
 */
export function EmptyState({
  title,
  description,
  icon,
  action,
  className = ''
}: EmptyStateProps) {
  return (
    <motion.div
      className={`flex flex-col items-center justify-center text-center p-8 ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {icon && (
        <div className="mb-4 text-[--muted-foreground] size-16 flex items-center justify-center">
          {icon}
        </div>
      )}
      
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      
      {description && (
        <p className="text-[--muted-foreground] text-sm max-w-md mb-6">{description}</p>
      )}
      
      {action && (
        <Button 
          variant="outline" 
          size="sm"
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </motion.div>
  )
}
