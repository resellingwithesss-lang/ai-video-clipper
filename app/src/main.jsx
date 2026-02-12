import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found')
}

createRoot(rootElement).render(
  <StrictMode>
    <div aria-busy="true" aria-live="polite" style={{minHeight: '100vh', display: 'flex', flexDirection: 'column'}}>
      <App />
    </div>
  </StrictMode>,
)