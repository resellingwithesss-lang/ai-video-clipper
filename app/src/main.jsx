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
    <main
      aria-live="polite"
      aria-busy="false"
      role="main"
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 1.5rem 2rem',
        gap: '1.5rem',
        backgroundColor: '#f9fafb',
        maxWidth: '1200px',
        margin: '0 auto',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      <App />
    </main>
  </StrictMode>,
)