import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import AppThemeProvider from './theme/AppThemeProvider.jsx'
import { HashRouter } from 'react-router-dom'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppThemeProvider>
      <HashRouter>
        <App />
      </HashRouter>
    </AppThemeProvider>
  </StrictMode>
)
