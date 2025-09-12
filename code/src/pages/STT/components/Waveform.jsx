import { useEffect, useRef } from 'react'

export function Waveform({ samplesRef, width = 600, height = 80, color = '#1976d2', bg = 'rgba(0,0,0,0.4)', lineWidth = 2 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    let raf
    const draw = () => {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      ctx.fillStyle = bg
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      const samples = samplesRef?.current
      if (samples && samples.length) {
        ctx.strokeStyle = color
        ctx.lineWidth = lineWidth
        ctx.beginPath()
        const mid = canvas.height / 2
        const len = samples.length
        const step = Math.max(1, Math.floor(len / canvas.width))
        for (let x = 0; x < canvas.width; x++) {
          const idx = x * step
          let min = 1.0, max = -1.0
            for (let i = 0; i < step && (idx + i) < len; i++) {
              const v = samples[idx + i]
              if (v < min) min = v
              if (v > max) max = v
            }
          const y1 = mid + min * mid
          const y2 = mid + max * mid
          ctx.moveTo(x, y1)
          ctx.lineTo(x, y2)
        }
        ctx.stroke()
      }
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(raf)
  }, [samplesRef, color, bg, lineWidth])

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ width: '100%', maxWidth: width, display: 'block', borderRadius: 4 }}
    />
  )
}
