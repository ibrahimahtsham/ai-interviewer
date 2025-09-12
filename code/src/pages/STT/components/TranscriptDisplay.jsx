import { Paper, Typography } from '@mui/material'

export function TranscriptDisplay({ partial, finals }) {
  return (
    <>
      <Paper variant="outlined" sx={{ p: 2, mb: 2, minHeight: 90 }}>
        <Typography variant="subtitle2" gutterBottom>Live Partial</Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{partial || '...'}</Typography>
      </Paper>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>Final Transcript</Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {finals.length ? finals.join(' ') : 'No transcript yet.'}
        </Typography>
      </Paper>
    </>
  )
}