import { useRef, useEffect, useCallback } from 'react'

export function useWebSocket(url, { onMessage, onOpen, onClose, enabled = true }) {
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const onMessageRef = useRef(onMessage)
  const onOpenRef = useRef(onOpen)
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onMessageRef.current = onMessage
    onOpenRef.current = onOpen
    onCloseRef.current = onClose
  })

  const connect = useCallback(() => {
    if (!enabled || !url) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const defaultHost = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? `${window.location.hostname}:8000`
      : window.location.host
    
    const base = import.meta.env.VITE_WS_URL || `${protocol}//${defaultHost}`
    const fullUrl = `${base}${url}`

    const ws = new WebSocket(fullUrl)

    ws.onopen = () => {
      onOpenRef.current?.()
    }
    
    ws.onclose = () => {
      onCloseRef.current?.()
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = (err) => {
      console.warn('WebSocket error:', err)
      ws.close()
    }

    ws.onmessage = (event) => {
      try {
        onMessageRef.current?.(JSON.parse(event.data))
      } catch {
        onMessageRef.current?.(event.data)
      }
    }

    wsRef.current = ws
  }, [url, enabled])

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
