import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Initialise theme before first paint to avoid flash
try {
  const raw = localStorage.getItem('nebula-theme')
  if (raw) {
    const { state } = JSON.parse(raw)
    if (state?.isDark === false) document.documentElement.classList.add('light')
  }
} catch { /* ignore */ }

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
