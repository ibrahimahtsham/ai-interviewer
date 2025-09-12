import { useRef, useState } from 'react'
import { Box, Button, Typography, Stack, Paper } from '@mui/material'
import { encodeWavFloat32 } from '../STT/utils/wav.js'
import { Waveform } from '../STT/components/Waveform.jsx'

export default function MicTestPage() {
  const [recording, setRecording] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [audioUrl, setAudioUrl] = useState('')
  const floatsRef = useRef([])
  const lastSamplesRef = useRef({ current: new Float32Array() })
  const ctrlRef = useRef(null)
  const DURATION_MS = 5000

  const start = async () => {
    if (recording) return
    setAudioUrl('')
    floatsRef.current = []
    setRecording(true)
    setCountdown(5)

    const t0 = performance.now()
    const tick = () => {
      const elapsed = performance.now() - t0
      const remain = Math.max(0, DURATION_MS - elapsed)
      setCountdown(Math.ceil(remain / 1000))
      if (remain <= 0) stop()
      else requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)

    const capture = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } })
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    const ctx = new AudioCtx({ sampleRate: 16000 })
    const source = ctx.createMediaStreamSource(capture)
    const proc = ctx.createScriptProcessor(4096, 1, 1)
    proc.onaudioprocess = (ev) => {
      const input = ev.inputBuffer.getChannelData(0)
      floatsRef.current.push(new Float32Array(input))
      lastSamplesRef.current.current = input.slice()
    }
    source.connect(proc)
    proc.connect(ctx.destination)
    ctrlRef.current = { ctx, source, proc, stream: capture }
  }

  const stop = async () => {
    if (!recording) return
    setRecording(false)
    const { ctx, source, proc, stream } = ctrlRef.current || {}
    proc && proc.disconnect()
    source && source.disconnect()
    stream && stream.getTracks().forEach(t => t.stop())
    ctx && ctx.state !== 'closed' && ctx.close()

    let length = floatsRef.current.reduce((a, b) => a + b.length, 0)
    const all = new Float32Array(length)
    let off = 0
    for (const chunk of floatsRef.current) { all.set(chunk, off); off += chunk.length }
    const blob = encodeWavFloat32(all, 16000)
    const url = URL.createObjectURL(blob)
    setAudioUrl(url)
  }

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Mic Test (5s Record & Playback)</Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <Button variant="contained" disabled={recording} onClick={start}>Record 5s</Button>
        <Button variant="outlined" disabled={!recording} onClick={stop}>Stop Early</Button>
        <Button variant="text" disabled={recording || !audioUrl} onClick={() => setAudioUrl('')}>Clear</Button>
      </Stack>
      {recording && <Typography variant="body2" sx={{ mb: 1 }}>Recording... ({countdown}s)</Typography>}
      <Waveform samplesRef={lastSamplesRef.current} />
      <Paper variant="outlined" sx={{ p:2, mt:2 }}>
        <Typography variant="subtitle2" gutterBottom>Playback</Typography>
        {audioUrl ? <audio controls src={audioUrl} /> : <Typography variant="body2">No recording yet.</Typography>}
      </Paper>
      <Typography variant="caption" color="text.secondary" sx={{ display:'block', mt:2 }}>
        After 5 seconds recording auto-stops and you can play it back.
      </Typography>
    </Box>
  )
}
