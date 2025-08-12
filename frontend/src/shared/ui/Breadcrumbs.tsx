import { Fragment } from 'react'
import { motion } from 'framer-motion'

interface BreadcrumbItem {
  label: string
  href?: string
  icon?: React.ReactNode
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  className?: string
}

/**
 * Componente Breadcrumbs para mostrar la ruta de navegación actual
 * con animaciones suaves y estilo premium
 */
export function Breadcrumbs({ items, className = '' }: BreadcrumbsProps) {
  if (!items.length) return null
  
  return (
    <nav aria-label="Breadcrumb" className={`mb-4 ${className}`}>
      <ol className="flex items-center flex-wrap gap-1 text-sm">
        {items.map((item, index) => (
          <Fragment key={index}>
            {index > 0 && (
              <li aria-hidden="true" className="mx-1 text-[--muted-foreground]">
                <ChevronRightIcon />
              </li>
            )}
            <li>
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  delay: index * 0.05,
                  duration: 0.2
                }}
              >
                {index === items.length - 1 ? (
                  <span className="font-medium text-[--foreground] flex items-center gap-1">
                    {item.icon && <span className="text-[--muted-foreground]">{item.icon}</span>}
                    {item.label}
                  </span>
                ) : (
                  <a 
                    href={item.href || '#'} 
                    className="text-[--muted-foreground] hover:text-[--foreground] transition-colors flex items-center gap-1"
                  >
                    {item.icon && <span>{item.icon}</span>}
                    {item.label}
                  </a>
                )}
              </motion.div>
            </li>
          </Fragment>
        ))}
      </ol>
    </nav>
  )
}

function ChevronRightIcon() {
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
      <path d="m9 18 6-6-6-6" />
    </svg>
  )
}
