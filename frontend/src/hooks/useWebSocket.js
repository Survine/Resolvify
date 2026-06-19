import { useRef, useEffect, useCallback } from 'react'

export function useWebSocket(url, { onMessage, onOpen, onClose, enabled = true }) {
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const connect = useCallback(() => {
    if (!enabled || !url) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const base = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`
    const ws = new WebSocket(`${base}${url}`)

    ws.onopen = () => onOpen?.()
    ws.onclose = () => {
      onClose?.()
      reconnectTimer.current = setTimeout(connect, 3000)
    }
    ws.onerror = () => ws.close()
    ws.onmessage = (event) => {
      try {
        onMessage?.(JSON.parse(event.data))
      } catch {
        onMessage?.(event.data)
      }
    }

    wsRef.current = ws
  }, [url, enabled, onMessage, onOpen, onClose])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }, [])

  return { send, ws: wsRef }
}
