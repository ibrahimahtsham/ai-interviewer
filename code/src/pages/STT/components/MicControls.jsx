import { Stack, Button } from '@mui/material'

export function MicControls({ running, onStart, onFlush, onStop, onClear }) {
  return (
    <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
      <Button variant="contained" disabled={running} onClick={onStart}>Start</Button>
      <Button variant="outlined" disabled={!running} onClick={onFlush}>Flush</Button>
      <Button variant="outlined" color="error" disabled={!running} onClick={onStop}>Stop</Button>
      <Button variant="text" disabled={running} onClick={onClear}>Clear</Button>
    </Stack>
  )
}