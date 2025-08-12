import { motion } from 'framer-motion'

interface SkeletonProps {
  className?: string
  variant?: 'rectangular' | 'circular' | 'text'
  animation?: 'pulse' | 'wave' | 'none'
}

/**
 * Componente Skeleton para mostrar estados de carga con estilo premium
 * Útil para mostrar placeholders mientras se cargan datos
 */
export function Skeleton({
  className = '',
  variant = 'rectangular',
  animation = 'pulse'
}: SkeletonProps) {
  const baseClasses = 'bg-[--muted]/30'
  
  const variantClasses = {
    rectangular: 'rounded-md',
    circular: 'rounded-full',
    text: 'rounded-md h-4'
  }
  
  // Animación de pulso
  const pulseAnimation = {
    animate: {
      opacity: [0.5, 0.8, 0.5],
      transition: {
        duration: 1.8,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    }
  }
  
  // Animación de onda
  const waveAnimation = {
    initial: { backgroundPosition: '-200% 0' },
    animate: {
      backgroundPosition: ['200% 0', '-200% 0'],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'linear'
      }
    }
  }
  
  const animationStyles = animation === 'wave' 
    ? 'bg-gradient-to-r from-[--muted]/20 via-[--muted]/40 to-[--muted]/20 bg-[length:200%_100%]'
    : ''
  
  const animationProps = animation === 'none' 
    ? {}
    : animation === 'pulse' 
      ? pulseAnimation
      : waveAnimation
  
  return (
    <motion.div
      className={`${baseClasses} ${variantClasses[variant]} ${animationStyles} ${className}`}
      {...animationProps}
    />
  )
}

/**
 * Componente para mostrar un esqueleto de carga de una tarjeta de persona
 */
export function PersonCardSkeleton() {
  return (
    <div className="h-full">
      <div className="border border-gray-200 rounded-lg overflow-hidden shadow-sm">
        <div className="p-4 space-y-4">
          {/* Avatar */}
          <div className="flex justify-center">
            <Skeleton variant="circular" className="size-20" />
          </div>
          
          {/* Nombre */}
          <div className="flex flex-col items-center gap-2">
            <Skeleton variant="text" className="w-3/4 h-5" />
            <Skeleton variant="text" className="w-1/2 h-4" />
          </div>
          
          {/* Tags */}
          <div className="flex justify-center gap-2 mt-2">
            <Skeleton className="w-16 h-6 rounded-full" />
            <Skeleton className="w-16 h-6 rounded-full" />
          </div>
          
          {/* Botones */}
          <div className="flex justify-center gap-2 pt-2">
            <Skeleton className="w-20 h-8 rounded-md" />
            <Skeleton className="w-20 h-8 rounded-md" />
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Componente para mostrar un esqueleto de carga de una fila de tabla
 */
export function PersonRowSkeleton() {
  return (
    <tr>
      <td className="py-3 px-4">
        <Skeleton variant="circular" className="size-8" />
      </td>
      <td className="py-3 px-4">
        <Skeleton variant="text" className="w-24 h-4" />
      </td>
      <td className="py-3 px-4">
        <Skeleton variant="text" className="w-32 h-4" />
      </td>
      <td className="py-3 px-4">
        <Skeleton className="w-16 h-6 rounded-full" />
      </td>
      <td className="py-3 px-4">
        <Skeleton className="w-16 h-6 rounded-full" />
      </td>
      <td className="py-3 px-4 text-right">
        <div className="flex justify-end gap-2">
          <Skeleton className="w-16 h-8 rounded-md" />
          <Skeleton className="w-16 h-8 rounded-md" />
        </div>
      </td>
    </tr>
  )
}
