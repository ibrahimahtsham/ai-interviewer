export function createSTTClient(url, handlers = {}) {
  const { onOpen, onPartial, onFinal, onError, onClose, onLog } = handlers
  const ws = new WebSocket(url)
  ws.binaryType = 'arraybuffer'
  const stats = { frames: 0, bytes: 0, started: Date.now() }
  let lastMeta = 0

  ws.onopen = () => onOpen && onOpen()
  ws.onerror = (e) => onError && onError(e)
  ws.onclose = () => onClose && onClose()
  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
  if (msg.type === 'partial') onPartial && onPartial(msg.text)
  else if (msg.type === 'final') onFinal && onFinal(msg.text)
  else if (msg.type === 'log') onLog && onLog(msg)
  else if (msg.type === 'error') onLog && onLog({ text: `SERVER ERROR: ${msg.kind}: ${msg.error}`, level: 'error', ts: Date.now()/1000 })
    } catch {}
  }
  return {
    sendPCM(frame) {
      if (ws.readyState === 1) {
        stats.frames += 1
        stats.bytes += frame.byteLength
        ws.send(frame.buffer)
      }
    },
    sendMeta(obj) {
      if (ws.readyState !== 1) return
      const now = Date.now()
      const isBurst = obj && obj.kind === 'hello'
      if (isBurst || (now - lastMeta) > 1000) {
        lastMeta = now
        ws.send(JSON.stringify({ type: 'meta', data: obj, stats: { ...stats, uptimeMs: now - stats.started } }))
      }
    },
    flush() { if (ws.readyState === 1) ws.send(JSON.stringify({ command: 'flush' })) },
    stop() { if (ws.readyState === 1) ws.send(JSON.stringify({ command: 'stop' })); ws.close() },
    raw: ws
  }
}