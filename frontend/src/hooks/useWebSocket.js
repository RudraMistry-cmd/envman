import { useRef, useCallback, useEffect, useState } from 'react'

export function useWebSocket(url, onMessage) {
  const wsRef = useRef(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        resolve(ws)
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        onMessage(msg)
      }

      ws.onerror = () => {
        reject(new Error('WebSocket connection failed. Is the backend running?'))
      }

      ws.onclose = () => {
        setConnected(false)
        wsRef.current = null
      }

      setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          ws.close()
          reject(new Error('WebSocket connection timed out'))
        }
      }, 5000)
    })
  }, [url, onMessage])

  const close = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setConnected(false)
  }, [])

  useEffect(() => {
    return () => close()
  }, [close])

  return { connect, close, connected }
}
