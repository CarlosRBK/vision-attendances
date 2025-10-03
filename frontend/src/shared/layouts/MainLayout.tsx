import { useState, useEffect, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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

      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0, x: -280 }}
            animate={{ width: 280, opacity: 1, x: 0 }}
            exit={{ width: 0, opacity: 0, x: -280 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="bg-white border-r border-gray-200 h-screen fixed md:sticky top-0 overflow-hidden z-30 shadow-lg"
          >
            <div className="p-6">
              <div className="flex items-center gap-3 mb-8">
                <div className="size-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 grid place-items-center text-white font-semibold">
                  V
                </div>
                <h1 className="text-xl font-semibold tracking-tight">Vision Attendances</h1>
              </div>

              <nav className="space-y-1">
                {/* <NavItem active icon={<HomeIcon />} label="Dashboard" /> */}
                <NavItem active icon={<PeopleIcon />} label="Alumnos" />
                <NavItem icon={<CalendarIcon />} label="Asistencias (Proximamente)" />
                {/* <NavItem icon={<SettingsIcon />} label="Configuración" /> */}
              </nav>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

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

interface NavItemProps {
  label: string
  icon?: React.ReactNode
  active?: boolean
}

function NavItem({ label, icon, active = false }: NavItemProps) {
  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`
        flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer
        ${active ? 'bg-blue-500/10 text-blue-600' : 'text-[--foreground] hover:bg-[--muted]/50'}
      `}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
      {active && (
        <motion.div
          layoutId="activeNavIndicator"
          className="ml-auto size-1.5 rounded-full bg-blue-600"
        />
      )}
    </motion.div>
  )
}


function PeopleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CalendarIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M19 4H5C3.89543 4 3 4.89543 3 6V20C3 21.1046 3.89543 22 5 22H19C20.1046 22 21 21.1046 21 20V6C21 4.89543 20.1046 4 19 4Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 2V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 2V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 10H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
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
