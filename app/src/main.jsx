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
        padding: '2rem 2rem 3rem',
        gap: '2rem',
        backgroundColor: '#f9fafb',
        maxWidth: '1200px',
        margin: '0 auto',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        lineHeight: 1.6,
      }}
      tabIndex={-1} // improve focus management for screen readers
    >
      <App />
    </main>
  </StrictMode>,
)