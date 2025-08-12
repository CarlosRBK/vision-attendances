import { motion } from 'framer-motion'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: string
  thickness?: number
  className?: string
}

/**
 * Componente de spinner de carga con animación suave y diseño premium
 */
export function LoadingSpinner({
  size = 'md',
  color = 'currentColor',
  thickness = 2,
  className = ''
}: LoadingSpinnerProps) {
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48
  }
  
  const actualSize = sizeMap[size]
  
  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <motion.svg
        width={actualSize}
        height={actualSize}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        animate={{ rotate: 360 }}
        transition={{
          duration: 1.5,
          ease: "linear",
          repeat: Infinity
        }}
      >
        <motion.circle
          cx="12"
          cy="12"
          r="10"
          stroke={color}
          strokeWidth={thickness}
          strokeLinecap="round"
          initial={{ pathLength: 0.2, opacity: 0.2 }}
          animate={{ 
            pathLength: [0.2, 0.8, 0.2],
            opacity: [0.2, 1, 0.2]
          }}
          transition={{
            duration: 1.5,
            ease: "easeInOut",
            repeat: Infinity,
            repeatType: "loop"
          }}
        />
      </motion.svg>
    </div>
  )
}
