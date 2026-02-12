import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found')
}

function Root() {
  // Improved loading state management
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate initial loading for app setup; replace with real API loading if needed
    const timer = setTimeout(() => setLoading(false), 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <main
      aria-live="polite"
      aria-busy={loading}
      role="main"
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '4rem 3rem 6rem',
        gap: '3rem',
        backgroundColor: '#f9fafb',
        maxWidth: '1200px',
        margin: '0 auto',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        lineHeight: 1.6,
        outline: 'none',
        boxSizing: 'border-box',
        transition: 'background-color 0.3s ease',
        boxShadow: '0 0 10px rgba(0,0,0,0.05)',
        borderRadius: '8px',
        position: 'relative',
        overflow: 'visible',
      }}
      tabIndex={-1} // improve focus management for screen readers
    >
      {/* Visually hidden heading for screen reader navigation */}
      <h1
        style={{
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: 0,
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0,0,0,0)',
          border: 0,
        }}
      >
        SaaS Application Main Content
      </h1>

      {/* Loading indicator */}
      {loading ? (
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          style={{
            margin: 'auto',
            padding: '2rem',
            fontSize: '1.25rem',
            color: '#374151',
            textAlign: 'center',
          }}
        >
          Loading application...
        </div>
      ) : (
        <App />
      )}
    </main>
  )
}

createRoot(rootElement).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)