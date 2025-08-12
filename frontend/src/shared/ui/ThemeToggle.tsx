import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Tooltip } from './Tooltip'

interface ThemeToggleProps {
  className?: string
}

/**
 * Componente para cambiar entre tema claro y oscuro con animaciones suaves
 */
export function ThemeToggle({ className = '' }: ThemeToggleProps) {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Detectar tema inicial del sistema o preferencia guardada
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
      
      if (savedTheme) {
        return savedTheme
      }
      
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    
    return 'light'
  })
  
  // Aplicar tema al documento
  useEffect(() => {
    const root = window.document.documentElement
    
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    
    localStorage.setItem('theme', theme)
  }, [theme])
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }
  
  return (
    <Tooltip content={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}>
      <button
        onClick={toggleTheme}
        className={`relative size-9 rounded-full bg-[--muted]/30 flex items-center justify-center transition-colors hover:bg-[--muted]/50 ${className}`}
        aria-label={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
      >
        <motion.div
          initial={false}
          animate={{ rotate: theme === 'dark' ? 40 : 0 }}
          transition={{ duration: 0.3, type: 'spring', stiffness: 200 }}
          className="absolute"
        >
          {theme === 'light' ? <SunIcon /> : <MoonIcon />}
        </motion.div>
      </button>
    </Tooltip>
  )
}

function SunIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </svg>
  )
}
