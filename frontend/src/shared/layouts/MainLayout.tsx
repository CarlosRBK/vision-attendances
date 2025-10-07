import { useState, useEffect, type ReactNode } from 'react'
import { Button } from '../ui/Button'
import { ScrollToTop } from '../ui/ScrollToTop'
import { Breadcrumbs } from '../ui/Breadcrumbs'

interface MainLayoutProps {
  title?: string
  children: ReactNode
  breadcrumbs?: Array<{ label: string; href?: string; icon?: React.ReactNode }>
}

export function MainLayout({ children, title = 'Vision Attendances', breadcrumbs = [] }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth >= 768)

  // Detectar cambios en el tamaño de la ventana para ajustar el sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  })

  return (
    <div className="min-h-screen bg-white flex flex-col md:flex-row">
      {/* Sidebar - Overlay para móviles */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
      {/* Main content */}
      <div className="flex-1">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-white/95 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                aria-label={isSidebarOpen ? 'Cerrar menú' : 'Abrir menú'}
              >
                <MenuIcon />
              </Button>
              <h2 className="text-lg font-medium">{title}</h2>
            </div>

            <div className="flex items-center gap-3">
              {/* <Button variant="outline" size="sm" leftIcon={<BellIcon />}>
                Notificaciones
              </Button> */}
              <div className="size-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 grid place-items-center text-white font-medium">
                U
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6">
          {breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} />}
          {children}
          <ScrollToTop />
        </main>
      </div>
    </div>
  )
}




function MenuIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 6H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
