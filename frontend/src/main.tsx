import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './global.css'
import App from './App.tsx'
import UiProviders from './providers/UiProviders.tsx'

// Create a client
const queryClient = new QueryClient()

createRoot(document.getElementById('root')!).render(
  <UiProviders>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </UiProviders>
)
