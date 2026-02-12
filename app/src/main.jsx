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
        // Added consistent padding for smaller screens for better responsiveness
        paddingLeft: '1.5rem',
        paddingRight: '1.5rem',
      }}
      tabIndex={-1} // improve focus management for screen readers
    >
      {/* Added visually hidden heading for better screen reader navigation */}
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
      <App />
    </main>
  </StrictMode>
)