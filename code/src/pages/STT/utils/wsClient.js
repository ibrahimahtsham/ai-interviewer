export function createSTTClient(url, handlers = {}) {
  const { onOpen, onPartial, onFinal, onError, onClose } = handlers
  const ws = new WebSocket(url)
  ws.binaryType = 'arraybuffer'
  ws.onopen = () => onOpen && onOpen()
  ws.onerror = (e) => onError && onError(e)
  ws.onclose = () => onClose && onClose()
  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
      if (msg.type === 'partial') onPartial && onPartial(msg.text)
      else if (msg.type === 'final') onFinal && onFinal(msg.text)
    } catch {}
  }
  return {
    sendPCM(frame) { if (ws.readyState === 1) ws.send(frame.buffer) },
    flush() { if (ws.readyState === 1) ws.send(JSON.stringify({ command: 'flush' })) },
    stop() { if (ws.readyState === 1) ws.send(JSON.stringify({ command: 'stop' })); ws.close() },
    raw: ws
  }
}