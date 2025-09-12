import { useEffect, useRef } from 'react'
import { Paper, Typography } from '@mui/material'

export function LogPanel({ logs, maxHeight = 220 }) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (el) el.scrollTop = el.scrollHeight
  }, [logs])
  return (
    <Paper variant="outlined" sx={{ p: 1.5, mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>Server Logs</Typography>
      <div
        ref={ref}
        style={{
          fontFamily: 'monospace',
          fontSize: 12,
          lineHeight: '1.3em',
          maxHeight,
          overflowY: 'auto',
          whiteSpace: 'pre-wrap'
        }}
      >
        {logs.length ? logs.map((l, i) => {
          const color = l.level === 'error' ? '#ff5252' : l.level === 'warn' ? '#ffb300' : '#90caf9'
          return (
            <div key={i} style={{ display: 'flex', gap: 6 }}>
              <span style={{ color, fontWeight: 600 }}>[{l.time}]</span>
              {l.seq !== undefined && <span style={{ color: '#888' }}>#{l.seq}</span>}
              <span style={{ flex: 1 }}>{l.text}</span>
            </div>
          )
        }) : 'No logs yet.'}
      </div>
    </Paper>
  )
}
