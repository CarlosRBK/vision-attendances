import { useState, useRef, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface TooltipProps {
  children: ReactNode
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
  maxWidth?: number
}

/**
 * Componente Tooltip premium que muestra información contextual al hacer hover
 * sobre un elemento con animaciones suaves y diseño moderno
 */
export function Tooltip({
  children,
  content,
  position = 'top',
  delay = 300,
  maxWidth = 250
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const handleMouseEnter = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delay)
  }
  
  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setIsVisible(false)
  }
  
  const positionStyles = {
    top: {
      initial: { opacity: 0, y: 10 },
      animate: { opacity: 1, y: 0 },
      className: 'bottom-full mb-2 left-1/2 transform -translate-x-1/2'
    },
    bottom: {
      initial: { opacity: 0, y: -10 },
      animate: { opacity: 1, y: 0 },
      className: 'top-full mt-2 left-1/2 transform -translate-x-1/2'
    },
    left: {
      initial: { opacity: 0, x: 10 },
      animate: { opacity: 1, x: 0 },
      className: 'right-full mr-2 top-1/2 transform -translate-y-1/2'
    },
    right: {
      initial: { opacity: 0, x: -10 },
      animate: { opacity: 1, x: 0 },
      className: 'left-full ml-2 top-1/2 transform -translate-y-1/2'
    }
  }
  
  return (
    <div 
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            className={`absolute z-50 ${positionStyles[position].className}`}
            initial={positionStyles[position].initial}
            animate={positionStyles[position].animate}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            style={{ maxWidth }}
          >
            <div className="bg-gray-900 text-white text-sm rounded-md py-1.5 px-3 shadow-lg">
              {content}
              <div className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
                position === 'top' ? 'bottom-[-4px] left-1/2 -translate-x-1/2' :
                position === 'bottom' ? 'top-[-4px] left-1/2 -translate-x-1/2' :
                position === 'left' ? 'right-[-4px] top-1/2 -translate-y-1/2' :
                'left-[-4px] top-1/2 -translate-y-1/2'
              }`} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
