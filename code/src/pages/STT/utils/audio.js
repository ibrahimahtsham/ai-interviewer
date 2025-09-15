export function startAudioCapture(onFrame, { sampleRate = 16000, bufferSize = 4096, onSamples, onStats } = {}) {
  const AudioCtx = window.AudioContext || window.webkitAudioContext
  const ctx = new AudioCtx({ sampleRate })
  let stopped = false
  let source, proc, stream
  const lastSamplesRef = { current: new Float32Array() }

  const init = async () => {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })
    source = ctx.createMediaStreamSource(stream)
    proc = ctx.createScriptProcessor(bufferSize, 1, 1)
    proc.onaudioprocess = (ev) => {
      if (stopped) return
      const input = ev.inputBuffer.getChannelData(0)
      // Keep a copy for visualization
      lastSamplesRef.current = input.slice ? input.slice() : new Float32Array(input)
      onSamples && onSamples(lastSamplesRef.current)
      const pcm = new Int16Array(input.length)
      let sum = 0, peak = 0
      for (let i = 0; i < input.length; i++) {
        let s = input[i]
        s = s < -1 ? -1 : s > 1 ? 1 : s
        sum += s * s
        const a = Math.abs(s); if (a > peak) peak = a
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      }
      if (onStats) {
        const rms = Math.sqrt(sum / (input.length || 1))
        onStats({ kind: 'frame', ctxRate: ctx.sampleRate, bufferSize, frameSamples: input.length, rms, peak })
      }
      onFrame(pcm)
    }
  source.connect(proc)
  // Mute processor output to avoid feedback, but keep node connected so onaudioprocess fires
  const silent = ctx.createGain()
  silent.gain.value = 0
  proc.connect(silent)
  silent.connect(ctx.destination)
    return stream
  }

  const ready = init()
  const stop = async () => {
    stopped = true
    try { proc && proc.disconnect(); source && source.disconnect() } catch {}
    stream && stream.getTracks().forEach(t => t.stop())
    if (ctx && ctx.state !== 'closed') await ctx.close()
  }
  return { ready, stop, lastSamplesRef }
}