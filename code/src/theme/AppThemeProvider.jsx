import { useState, useEffect, useMemo } from 'react'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { ColorModeContext } from './ColorModeContext.js'

export default function AppThemeProvider({ children }) {
  const stored = typeof window !== 'undefined' ? localStorage.getItem('color-mode') : null
  const prefersDark = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  const [mode, setMode] = useState(stored || (prefersDark ? 'dark' : 'dark')) // default dark

  useEffect(() => {
    localStorage.setItem('color-mode', mode)
  }, [mode])

  const toggleColorMode = () => setMode(m => (m === 'light' ? 'dark' : 'light'))

  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      ...(mode === 'dark'
        ? {
            primary: { main: '#90caf9' },
            background: { default: '#121212', paper: '#1e1e1e' }
          }
        : {
            primary: { main: '#1976d2' }
          })
    },
    components: {
      MuiAppBar: {
        defaultProps: { color: 'default' },
        styleOverrides: {
          root: ({ theme }) => ({
            background: theme.palette.mode === 'dark' ? '#1e1e1e' : '#ffffff'
          })
        }
      }
    }
  }), [mode])

  return (
    <ColorModeContext.Provider value={{ mode, toggleColorMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  )
}
