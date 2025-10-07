import { useState } from 'react'
import PeoplePage from '@/features/people/pages/PeoplePage'
import FaceDetectionPage from '@/features/face-detection/pages/FaceDetectionPage'
import AttendancePage from '@/features/attendance/pages/AttendancePage'

type Page = 'people' | 'detection' | 'attendance'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('people')

  return (
    <div className="min-h-dvh bg-[radial-gradient(60%_60%_at_50%_-20%,color-mix(in_oklab,white_10%,transparent),transparent)]">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <svg className="w-8 h-8 text-blue-600" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 5C13.66 5 15 6.34 15 8C15 9.66 13.66 11 12 11C10.34 11 9 9.66 9 8C9 6.34 10.34 5 12 5ZM12 19.2C9.5 19.2 7.29 17.92 6 15.98C6.03 13.99 10 12.9 12 12.9C13.99 12.9 17.97 13.99 18 15.98C16.71 17.92 14.5 19.2 12 19.2Z" fill="currentColor"/>
              </svg>
              <span className="text-xl font-bold text-gray-900">Vision Attendances</span>
            </div>
            
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setCurrentPage('people')}
                className={`
                  px-4 py-2 rounded-md font-medium text-sm transition-all
                  ${currentPage === 'people' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                👥 Personas
              </button>
              <button
                onClick={() => setCurrentPage('detection')}
                className={`
                  px-4 py-2 rounded-md font-medium text-sm transition-all
                  ${currentPage === 'detection' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                📹 Detección Facial
              </button>
              <button
                onClick={() => setCurrentPage('attendance')}
                className={`
                  px-4 py-2 rounded-md font-medium text-sm transition-all
                  ${currentPage === 'attendance' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                📊 Asistencias
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main>
        {currentPage === 'people' && <PeoplePage />}
        {currentPage === 'detection' && <FaceDetectionPage />}
        {currentPage === 'attendance' && <AttendancePage />}
      </main>
    </div>
  )
}

export default App
