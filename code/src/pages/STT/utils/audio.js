export function startAudioCapture(onFrame, { sampleRate = 16000, bufferSize = 4096, onSamples } = {}) {
  const AudioCtx = window.AudioContext || window.webkitAudioContext
  const ctx = new AudioCtx({ sampleRate })
  let stopped = false
  let source, proc, stream
  const lastSamplesRef = { current: new Float32Array() }

  const init = async () => {
    stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } })
    source = ctx.createMediaStreamSource(stream)
    proc = ctx.createScriptProcessor(bufferSize, 1, 1)
    proc.onaudioprocess = (ev) => {
      if (stopped) return
      const input = ev.inputBuffer.getChannelData(0)
      // Keep a copy for visualization
      lastSamplesRef.current = input.slice ? input.slice() : new Float32Array(input)
      onSamples && onSamples(lastSamplesRef.current)
      const pcm = new Int16Array(input.length)
      for (let i = 0; i < input.length; i++) {
        let s = input[i]
        s = s < -1 ? -1 : s > 1 ? 1 : s
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      }
      onFrame(pcm)
    }
    source.connect(proc)
    proc.connect(ctx.destination)
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