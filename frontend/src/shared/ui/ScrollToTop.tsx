import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Tooltip } from './Tooltip'

interface ScrollToTopProps {
  threshold?: number
  className?: string
}

/**
 * Componente ScrollToTop que aparece cuando el usuario ha desplazado
 * más allá del umbral especificado y permite volver al inicio de la página
 * con una animación suave
 */
export function ScrollToTop({ threshold = 300, className = '' }: ScrollToTopProps) {
  const [isVisible, setIsVisible] = useState(false)

  // Controlar visibilidad basada en la posición de scroll
  useEffect(() => {
    const toggleVisibility = () => {
      if (window.scrollY > threshold) {
        setIsVisible(true)
      } else {
        setIsVisible(false)
      }
    }

    window.addEventListener('scroll', toggleVisibility)
    return () => window.removeEventListener('scroll', toggleVisibility)
  }, [threshold])

  // Función para desplazarse al inicio con animación suave
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <Tooltip content="Volver arriba">
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={scrollToTop}
            className={`fixed bottom-6 right-6 size-12 rounded-full bg-blue-600 text-white shadow-lg flex items-center justify-center z-50 ${className}`}
            aria-label="Volver al inicio"
          >
            <ArrowUpIcon />
          </motion.button>
        </Tooltip>
      )}
    </AnimatePresence>
  )
}

function ArrowUpIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m18 15-6-6-6 6" />
    </svg>
  )
}
