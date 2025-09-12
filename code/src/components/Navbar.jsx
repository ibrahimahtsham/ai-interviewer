import { useContext } from 'react'
import { AppBar, Toolbar, Typography, IconButton, Tooltip, Button } from '@mui/material'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'
import { ColorModeContext } from '../theme/ColorModeContext.js'
import { Link as RouterLink, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { mode, toggleColorMode } = useContext(ColorModeContext)
  const isDark = mode === 'dark'
  const { pathname } = useLocation()
  const isActive = (target) => (target === '/' ? pathname === '/' : pathname.startsWith(target))
  return (
    <AppBar position="sticky" elevation={1} sx={{ mb: 2 }}>
      <Toolbar>
        <Typography variant="h6" sx={{ fontWeight: 600, mr: 2 }}>
          AI Interviewer
        </Typography>
        <Button
          component={RouterLink}
          to="/"
          color={isActive('/') ? 'primary' : 'inherit'}
          variant={isActive('/') ? 'contained' : 'text'}
          sx={{ textTransform: 'none' }}
        >
          STT
        </Button>
        <Button
          component={RouterLink}
          to="/llm"
          color={isActive('/llm') ? 'primary' : 'inherit'}
          variant={isActive('/llm') ? 'contained' : 'text'}
          sx={{ textTransform: 'none', ml: 1, mr: 'auto' }}
        >
          LLM
        </Button>
        <Tooltip title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
          <IconButton color="inherit" onClick={toggleColorMode} aria-label="toggle dark mode">
            {isDark ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Tooltip>
      </Toolbar>
    </AppBar>
  )
}