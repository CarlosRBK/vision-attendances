import { forwardRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  options: SelectOption[]
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  error?: string
  label?: string
  fullWidth?: boolean
}

export const Select = forwardRef<HTMLDivElement, SelectProps>(
  ({ 
    className = '', 
    options, 
    value, 
    onChange, 
    placeholder = 'Seleccionar...', 
    disabled = false,
    error,
    label,
    fullWidth = false,
    ...props 
  }, ref) => {
    const [isOpen, setIsOpen] = useState(false)
    
    const selectedOption = options.find(option => option.value === value)
    
    const handleSelect = (optionValue: string) => {
      onChange?.(optionValue)
      setIsOpen(false)
    }
    
    const widthClass = fullWidth ? 'w-full' : 'w-64'
    
    return (
      <div className={`relative ${widthClass} ${className}`} ref={ref} {...props}>
        {label && (
          <label className="block text-sm font-medium text-[--foreground] mb-1.5">
            {label}
          </label>
        )}
        
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          className={`
            flex items-center justify-between w-full px-3 py-2 text-left 
            bg-white border rounded-lg outline-none 
            focus:ring-2 focus:ring-blue-500/20 transition-all
            ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:border-gray-200/80'}
            ${error ? 'border-red-500' : 'border-gray-200'}
          `}
          disabled={disabled}
        >
          <span className={`block truncate ${!selectedOption ? 'text-gray-500' : ''}`}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <svg 
            className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto"
            >
              <ul className="py-1">
                {options.map((option) => (
                  <motion.li
                    key={option.value}
                    whileHover={{ backgroundColor: 'rgba(var(--muted-rgb), 0.3)' }}
                    onClick={() => handleSelect(option.value)}
                    className={`
                      px-3 py-2 cursor-pointer text-sm
                      ${option.value === value ? 'bg-blue-500/10 text-blue-600' : ''}
                    `}
                  >
                    {option.label}
                  </motion.li>
                ))}
                {options.length === 0 && (
                  <li className="px-3 py-2 text-sm text-gray-400">
                    No hay opciones disponibles
                  </li>
                )}
              </ul>
            </motion.div>
          )}
        </AnimatePresence>
        
        {error && (
          <p className="mt-1 text-xs text-red-500">{error}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'
