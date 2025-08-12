import { cva, type VariantProps } from 'class-variance-authority'

// Definición de variantes para el componente Badge
const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[--ring] focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "bg-blue-500 text-white hover:bg-blue-600",
        secondary: "bg-gray-200 text-gray-600 hover:bg-gray-300",
        destructive: "bg-red-500 text-white hover:bg-red-600",
        outline: "border border-gray-200 text-gray-600",
        success: "bg-green-500 text-white hover:bg-green-600",
        warning: "bg-amber-500 text-white hover:bg-amber-600",
        info: "bg-blue-500 text-white hover:bg-blue-600",
      },
      size: {
        sm: "text-xs px-2 py-0.5",
        md: "text-xs px-2.5 py-0.5",
        lg: "text-sm px-3 py-1",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

/**
 * Componente Badge para mostrar etiquetas o estados con estilo premium
 * Soporta diferentes variantes, tamaños y animaciones
 */
export function Badge({
  className,
  variant,
  size,
  ...props
}: BadgeProps) {
  return (
    <div
      className={badgeVariants({ variant, size, className })}
      {...props}
    />
  )
}
