/**
 * API and WebSocket URL configuration.
 *
 * When running in Vite dev mode (typically port 5173), route to the
 * backend running on http://localhost:8000.
 * When running packaged/same-origin, use relative URLs for HTTP and
 * the current window location host for WebSocket.
 */
const isViteDev = typeof window !== 'undefined' && window.location.port === '5173'

export const API = isViteDev ? 'http://localhost:8000' : ''
export const WS_URL = isViteDev
  ? 'ws://localhost:8000/ws'
  : (typeof window !== 'undefined'
      ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
      : 'ws://localhost:8000/ws')
