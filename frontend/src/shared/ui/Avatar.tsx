import { forwardRef, useState } from 'react'
import { motion, type HTMLMotionProps } from 'framer-motion'
import { UserPlaceholderIcon } from './icons/UserPlaceholderIcon'

interface AvatarProps extends Omit<HTMLMotionProps<"div">, 'animate'> {
  src?: string | null
  alt?: string
  fallback?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  status?: 'online' | 'offline' | 'away' | 'busy' | null
  border?: boolean
}

const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ 
    className = '', 
    src, 
    alt = '', 
    fallback = '?', 
    size = 'md', 
    status = null,
    border = true,
    ...props 
  }, ref) => {
    const [imageError, setImageError] = useState(false)
    
    const sizeClasses = {
      sm: 'size-8',
      md: 'size-10',
      lg: 'size-14',
      xl: 'size-20',
    }
    
    const textSizeClasses = {
      sm: 'text-xs',
      md: 'text-sm',
      lg: 'text-base',
      xl: 'text-xl',
    }
    
    const statusSizeClasses = {
      sm: 'size-2',
      md: 'size-2.5',
      lg: 'size-3',
      xl: 'size-3.5',
    }
    
    const statusPositionClasses = {
      sm: 'right-0 bottom-0',
      md: 'right-0 bottom-0',
      lg: 'right-0.5 bottom-0.5',
      xl: 'right-1 bottom-1',
    }
    
    const statusColorClasses = {
      online: 'bg-green-500',
      offline: 'bg-gray-400',
      away: 'bg-yellow-500',
      busy: 'bg-red-500',
    }
    
    const borderClass = border ? 'border border-blue-300' : ''
    
    const showFallback = !src || imageError
    
    return (
      <motion.div
        ref={ref}
        className={`relative rounded-full overflow-hidden bg-gray-200 cursor-default ${sizeClasses[size]} ${borderClass} ${className}`}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        {...props as any}
      >
        {!showFallback ? (
          <img
            src={src!}
            alt={alt}
            className="size-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className={`size-full grid place-items-center text-gray-600 bg-gray-200 font-medium ${textSizeClasses[size]}`}>
            {fallback ? (
              <span>{alt?.charAt(0) || fallback}</span>
            ) : (
              <UserPlaceholderIcon className={`${sizeClasses[size]} p-2 text-gray-600`} />
            )}
          </div>
        )}
        
        {status && (
          <span className={`absolute ${statusPositionClasses[size]} ${statusSizeClasses[size]} ${statusColorClasses[status]} rounded-full ring-2 ring-gray-200`} />
        )}
      </motion.div>
    )
  }
)

Avatar.displayName = 'Avatar'

export { Avatar }
