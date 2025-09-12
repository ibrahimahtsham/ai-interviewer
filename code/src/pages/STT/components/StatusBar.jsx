import { Alert, Box, Typography } from '@mui/material'

export function StatusBar({ running, backendStatus, error, model }) {
  return (
    <Box sx={{ mt: 2 }}>
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}
      <Typography variant="caption" color="text.secondary">
        Status: {running ? 'Capturing' : 'Idle'} | Backend: {backendStatus} | Model: {model}
      </Typography>
    </Box>
  )
}