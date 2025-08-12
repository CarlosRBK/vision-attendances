import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  autoFocus?: boolean
  debounceMs?: number
}

/**
 * Componente de entrada de búsqueda con estilo premium y debounce integrado
 * Incluye animación de enfoque y efecto de debounce para mejorar rendimiento
 */
export function SearchInput({
  value,
  onChange,
  placeholder = 'Buscar...',
  className = '',
  autoFocus = false,
  debounceMs = 300
}: SearchInputProps) {
  const [inputValue, setInputValue] = useState(value)
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Efecto para manejar el debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue !== value) {
        onChange(inputValue)
      }
    }, debounceMs)

    return () => clearTimeout(timer)
  }, [inputValue, onChange, value, debounceMs])

  // Sincronizar el valor del input cuando cambia externamente
  useEffect(() => {
    if (value !== inputValue) {
      setInputValue(value)
    }
  }, [value])

  // Autofocus cuando se monta el componente
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus()
    }
  }, [autoFocus])

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={placeholder}
          className="w-full h-10 pl-10 pr-4 py-2 text-sm bg-white  border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-gray-900 "
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          aria-label={placeholder}
        />

        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <SearchIcon />
        </div>

        {inputValue && (
          <button
            type="button"
            onClick={() => {
              setInputValue('')
              onChange('')
              inputRef.current?.focus()
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-500 transition-colors"
            aria-label="Limpiar búsqueda"
          >
            <ClearIcon />
          </button>
        )}
      </div>

      {/* Línea de enfoque animada */}
      {isFocused && (
        <motion.div
          className="absolute bottom-0 left-0 h-0.5 bg-blue-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.2 }}
        />
      )}
    </div>
  )
}

function SearchIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  )
}

function ClearIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  )
}
