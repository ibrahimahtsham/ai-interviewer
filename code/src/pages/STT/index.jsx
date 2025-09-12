import { useRef, useState } from 'react'
import { Box, Typography } from '@mui/material'
import { MicControls } from './components/MicControls.jsx'
import { TranscriptDisplay } from './components/TranscriptDisplay.jsx'
import { StatusBar } from './components/StatusBar.jsx'
import { startAudioCapture } from './utils/audio.js'
import { createSTTClient } from './utils/wsClient.js'
import { Waveform } from './components/Waveform.jsx'

export default function STTPage() {
  const [running, setRunning] = useState(false)
  const [partial, setPartial] = useState('')
  const [finals, setFinals] = useState([])
  const [error, setError] = useState('')
  const [backendStatus, setBackendStatus] = useState('disconnected')
  const audioRef = useRef(null)
  const sttRef = useRef(null)
  const waveformRef = useRef({ current: new Float32Array() })

  const clearAll = () => {
    setPartial('')
    setFinals([])
    setError('')
  }

  const start = async () => {
    clearAll()
    try {
      setBackendStatus('connecting')
      const client = createSTTClient('ws://localhost:8765', {
        onOpen: () => setBackendStatus('connected'),
        onPartial: (t) => setPartial(t),
        onFinal: (t) => { setFinals(f => [...f, t]); setPartial('') },
        onError: () => setBackendStatus('error'),
        onClose: () => setBackendStatus('disconnected')
      })
      sttRef.current = client
      const audio = startAudioCapture(frame => client.sendPCM(frame), {
        onSamples: (floats) => { waveformRef.current.current = floats }
      })
      audioRef.current = audio
      waveformRef.current = audio.lastSamplesRef
      await audio.ready
      setRunning(true)
    } catch (e) {
      setError(e.message || 'Failed to start')
      stop()
    }
  }

  const flush = () => sttRef.current?.flush()
  const stop = async () => {
    await audioRef.current?.stop()
    sttRef.current?.stop()
    setRunning(false)
  }

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Speech To Text (Local)</Typography>
      <MicControls running={running} onStart={start} onFlush={flush} onStop={stop} onClear={clearAll} />
  <Waveform samplesRef={waveformRef.current} />
  <TranscriptDisplay partial={partial} finals={finals} />
      <StatusBar running={running} backendStatus={backendStatus} error={error} model="tiny.en:int8" />
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
        Backend: see server/run.sh (start backend first) then npm run dev here.
      </Typography>
    </Box>
  )
}
