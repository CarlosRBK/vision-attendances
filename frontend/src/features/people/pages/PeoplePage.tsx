import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MainLayout } from '@/shared/layouts/MainLayout'
import { Button } from '@/shared/ui/Button'
import PeopleGrid from '../components/PeopleGrid'
import PeopleFormModern from '../components/PeopleFormModern'
import type { Person } from '../types'

export default function PeoplePage() {
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null)
  const [showForm, setShowForm] = useState(false)
  
  const handleNewPerson = () => {
    setSelectedPerson(null)
    setShowForm(true)
  }
  
  const handleEditPerson = (person: Person) => {
    setSelectedPerson(person)
    setShowForm(true)
  }
  
  const handleCloseForm = () => {
    setShowForm(false)
    setSelectedPerson(null)
  }
  
  return (
    <MainLayout title="Gestión de Alumnos">
      <div className="space-y-8">
        <AnimatePresence mode="wait">
          {showForm ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-4 flex items-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCloseForm}
                  leftIcon={<BackIcon />}
                >
                  Volver a la lista
                </Button>
              </div>
              
              <PeopleFormModern 
                person={selectedPerson} 
                onCancel={handleCloseForm} 
              />
            </motion.div>
          ) : (
            <motion.div
              key="list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <PeopleGrid onEditPerson={handleEditPerson} onAddPerson={handleNewPerson} />
              
              <motion.div 
                className="fixed bottom-6 right-6"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleNewPerson}
                  className="rounded-full size-14 shadow-lg"
                  aria-label="Agregar persona"
                >
                  <PlusIcon />
                </Button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </MainLayout>
  )
}

// Icons
function BackIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 5V19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
